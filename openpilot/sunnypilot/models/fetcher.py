"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import time
import os
import requests
from requests.exceptions import (SSLError, RequestException, HTTPError)
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.common.hardware.hw import Paths
from openpilot.sunnypilot.models.helpers import is_bundle_version_compatible
from openpilot.cereal import custom


class ModelParser:
  """Handles parsing of model data into cereal objects"""

  @staticmethod
  def _parse_download_uri(download_uri_data) -> custom.ModelManagerSP.DownloadUri:
    download_uri = custom.ModelManagerSP.DownloadUri()
    download_uri.uri = download_uri_data.get("url")
    download_uri.sha256 = download_uri_data.get("sha256")
    return download_uri

  @staticmethod
  def _parse_chunk(chunk_data) -> custom.ModelManagerSP.Chunk:
    chunk = custom.ModelManagerSP.Chunk()
    chunk.fileName = chunk_data.get("file_name")
    chunk.sha256 = chunk_data.get("sha256")
    return chunk

  @staticmethod
  def _parse_artifact(artifact_data) -> custom.ModelManagerSP.Artifact:
    artifact = custom.ModelManagerSP.Artifact()
    artifact.fileName = artifact_data.get("file_name")
    artifact.downloadUri = ModelParser._parse_download_uri(artifact_data.get("download_uri", {}))

    if "chunks" in artifact_data:
      artifact.chunks = [ModelParser._parse_chunk(chunk_data) for chunk_data in artifact_data["chunks"]]

      try:
        model_dir = Paths.model_root()
        os.makedirs(model_dir, exist_ok=True)
        manifest_path = os.path.join(model_dir, f"{artifact.fileName}.chunkmanifest")
        num_chunks = str(len(artifact.chunks))

        if not os.path.exists(manifest_path) or open(manifest_path).read().strip() != num_chunks:
          with open(manifest_path, "w") as f:
            f.write(num_chunks)
          cloudlog.info(f"Wrote chunk manifest for {artifact.fileName}: {num_chunks} chunks")
      except Exception as e:
        cloudlog.warning(f"Failed to write chunk manifest for {artifact.fileName}: {e}")

    return artifact

  @staticmethod
  def _parse_model(model_data) -> custom.ModelManagerSP.Model:
    model = custom.ModelManagerSP.Model()

    model.type = model_data.get("type")
    model.artifact = ModelParser._parse_artifact(model_data.get("artifact", {}))
    return model

  @staticmethod
  def _parse_overrides(overrides_data: dict[str, str]) -> list[custom.ModelManagerSP.Override]:
    overrides = []
    for key, value in overrides_data.items():
      override = custom.ModelManagerSP.Override()
      override.key = key
      override.value = value
      overrides.append(override)
    return overrides

  @staticmethod
  def _parse_bundle(bundle) -> custom.ModelManagerSP.ModelBundle:
    model_bundle = custom.ModelManagerSP.ModelBundle()
    model_bundle.index = int(bundle["index"])
    model_bundle.internalName = bundle["short_name"]
    model_bundle.displayName = bundle["display_name"]
    model_bundle.models = [ModelParser._parse_model(model) for model in bundle.get("models",[])]
    model_bundle.status = 0
    model_bundle.generation = int(bundle["generation"])
    model_bundle.environment = bundle["environment"]
    model_bundle.runner = bundle.get("runner", custom.ModelManagerSP.Runner.snpe)
    model_bundle.is20hz = bundle.get("is_20hz", False)
    model_bundle.minimumSelectorVersion = int(bundle["minimum_selector_version"])
    model_bundle.overrides = ModelParser._parse_overrides(bundle.get("overrides", {}))
    model_bundle.ref = bundle.get("ref")

    return model_bundle

  @staticmethod
  def parse_models(json_data: dict) -> list[custom.ModelManagerSP.ModelBundle]:
    found_bundles = [ModelParser._parse_bundle(bundle) for bundle in json_data.get("bundles", [])]
    return [bundle for bundle in found_bundles if is_bundle_version_compatible(bundle.to_dict())]


class ModelCache:
  """Handles caching of model data to avoid frequent remote fetches"""

  def __init__(self, params: Params, cache_timeout: int = int(3600 * 1e9), suffix: str = ""):
    self.params = params
    self.cache_timeout = cache_timeout
    self._LAST_SYNC_KEY = f"ModelManager_LastSyncTime{suffix}"
    self._CACHE_KEY = f"ModelManager_ModelsCache{suffix}"

  def _is_expired(self) -> bool:
    """Checks if the cache has expired"""
    current_time = int(time.monotonic() * 1e9)
    last_sync = self.params.get(self._LAST_SYNC_KEY) or 0
    return bool(last_sync == 0) or (current_time - last_sync) >= self.cache_timeout

  def get(self) -> tuple[dict, bool]:
    """
    Retrieves cached model data and expiration status atomically.
    Returns: Tuple of (cached_data, is_expired)
    If no cached data exists or on error, returns an empty dict
    """
    try:
      cached_data = self.params.get(self._CACHE_KEY)
      if not cached_data:
        cloudlog.warning("No cached model data available")
        return {}, True
      return cached_data, self._is_expired()
    except Exception as e:
      cloudlog.exception(f"Error retrieving cached model data: {str(e)}")
      return {}, True

  def set(self, data: dict) -> None:
    """Updates the cache with new model data"""
    self.params.put(self._CACHE_KEY, data, block=True)
    self.params.put(self._LAST_SYNC_KEY, int(time.monotonic() * 1e9), block=True)


class ModelFetcher:
  """Handles fetching and caching of model data from remote source"""
  MODEL_URL = "https://raw.githubusercontent.com/sunnypilot/sunnypilot-models/refs/heads/gh-pages/docs/driving_models_v21.json"
  MODEL_URL_CHESTNUT = "https://raw.githubusercontent.com/sunnypilot/sunnypilot-models/refs/heads/gh-pages/docs/driving_models_chestnut_v22.json"

  MODEL_SOURCES = {
    "qcom": (MODEL_URL, ""),
    "chestnut": (MODEL_URL_CHESTNUT, "_Chestnut"),
  }

  def __init__(self, params: Params):
    self.params = params
    self.model_parser = ModelParser()
    self.model_caches = {
      source: ModelCache(params, suffix=suffix)
      for source, (_, suffix) in self.MODEL_SOURCES.items()
    }
    self._refetched: set[str] = set()
    self.params.put("ModelManager_ActiveJson", {
      "qcom": self.MODEL_URL,
      "chestnut": self.MODEL_URL_CHESTNUT,
    }, block=True)

  @staticmethod
  def active_source(chestnut_present: bool) -> str:
    return "chestnut" if chestnut_present else "qcom"

  def _fetch_and_cache_models(self, source: str) -> list[custom.ModelManagerSP.ModelBundle] | None:
    """Fetches fresh model data from remote and updates cache.
    Returns None on transport errors. Raises on 404 and other fatal HTTP errors.
    """
    model_url, _ = self.MODEL_SOURCES[source]
    try:
      response = requests.get(model_url, timeout=10)

      # Explicitly handle 404 differently
      if response.status_code == 404:
        cloudlog.error(f"Models URL returned 404 Not Found: {model_url}")
        raise HTTPError(f"404 Not Found: {model_url}", response=response)

      # Raise for any other 4xx/5xx
      response.raise_for_status()

      json_data = response.json()
      parsed = self.model_parser.parse_models(json_data)
      if parsed:
        self.model_caches[source].set(json_data)
        cloudlog.debug(f"Successfully updated models cache for {source}")
      return parsed

    except ConnectionError as e:
      cloudlog.warning(f"DNS/connection error while fetching models: {e}")
    except SSLError as e:
      cloudlog.warning(f"SSL error while fetching models: {e}")
    except RequestException as e:
      cloudlog.warning(f"Request transport error while fetching models: {e}")
    except Exception as e:
      cloudlog.exception(f"Unexpected error fetching models: {e}")

    return None

  @staticmethod
  def _cache_matches_source(source: str, cached_data: dict) -> bool:
    bundles = cached_data.get("bundles", [])
    if source == "chestnut":
      return any(bundle.get("is_big") is True for bundle in bundles)
    return not any(bundle.get("is_big") is True for bundle in bundles)

  def get_bundles_for_source(self, source: str) -> list[custom.ModelManagerSP.ModelBundle]:
    if source not in self.MODEL_SOURCES:
      cloudlog.warning(f"Unknown model source: {source}")
      return []

    cached_data, is_expired = self.model_caches[source].get()

    if cached_data and not is_expired:
      # a source is refetched over a mismatch at most once per process: if the fresh
      # manifest still mismatches, the URL is authoritative and the cache is trusted
      if self._cache_matches_source(source, cached_data) or source in self._refetched:
        try:
          parsed = self.model_parser.parse_models(cached_data)
        except Exception:
          cloudlog.warning(f"Failed to parse cached models for {source}; refetching", exc_info=True)
        else:
          if parsed:
            cloudlog.debug(f"Using valid cached models data for source {source}")
            return parsed
          # a source-matching cache that yields no valid bundles is stale (e.g. an old
          # manifest version) - do not trust it, refetch so the source is repopulated
          cloudlog.warning(f"Cached models for {source} have no valid bundles; refetching")
      else:
        self._refetched.add(source)
        cloudlog.warning(f"Cached models for {source} not valid; refetching once")

    fetched_bundles = self._fetch_and_cache_models(source)
    if fetched_bundles is not None:
      return fetched_bundles

    if not cached_data:
      cloudlog.warning("Failed to fetch fresh data and no cache available")

    cloudlog.warning("Failed to fetch fresh data. Using expired cache as fallback")
    try:
      return self.model_parser.parse_models(cached_data)
    except Exception:
      return []


def get_cached_bundles(params: Params, source: str) -> list[custom.ModelManagerSP.ModelBundle]:

  if source not in ModelFetcher.MODEL_SOURCES:
    cloudlog.warning(f"Unknown model source: {source}")
    return []
  _, suffix = ModelFetcher.MODEL_SOURCES[source]
  cached_data = params.get(f"ModelManager_ModelsCache{suffix}")
  if not cached_data:
    return []
  try:
    return ModelParser.parse_models(cached_data)
  except Exception as e:
    cloudlog.warning(f"Failed to parse cached models for source {source}: {e}")
    return []


if __name__ == "__main__":
  from openpilot.selfdrive.modeld.helpers import chestnut_present
  params = Params()
  model_fetcher = ModelFetcher(params)
  bundles = model_fetcher.get_bundles_for_source(ModelFetcher.active_source(chestnut_present()))
  for bundle in bundles:
    for model in bundle.models:
      model_overrides = {override.key: override.value for override in bundle.overrides}
      print(f"Bundle: {bundle.internalName}, Type: {model.type}, Status: {bundle.status}, Overrides: {model_overrides}")
      print(f"Artifact: {model.artifact.fileName}, Download URI: {model.artifact.downloadUri.uri}")
      if model.artifact.chunks:
        print(f"Contains {len(model.artifact.chunks)} chunks.")
