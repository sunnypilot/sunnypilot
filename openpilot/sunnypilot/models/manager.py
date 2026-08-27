"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import os
import time

import requests
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.common.hardware.hw import Paths

from openpilot.cereal import messaging, custom
from openpilot.sunnypilot.models.fetcher import ModelFetcher
from openpilot.sunnypilot.models.helpers import (ACTIVE_BUNDLE_KEYS, get_active_bundle, get_selected_bundle,
                                                  resolve_bundle_by_ref, validate_active_bundles, verify_file)

# (connect, read) seconds. read is per-request inactivity, not a total cap
DOWNLOAD_TIMEOUT = (30, 30)


class DownloadCancelled(Exception):
  pass


class ModelManagerSP:
  """Manages model downloads and status reporting"""

  def __init__(self):
    self.params = Params()
    self.model_fetcher = ModelFetcher(self.params)
    self.pm = messaging.PubMaster(["modelManagerSP"])
    self.sm = messaging.SubMaster(["deviceState"])
    self.chestnut_present = False
    self.available_models: list[custom.ModelManagerSP.ModelBundle] = []
    self.source_models: dict[str, list[custom.ModelManagerSP.ModelBundle]] = {}
    self.selected_bundle: custom.ModelManagerSP.ModelBundle = None
    self.active_bundle: custom.ModelManagerSP.ModelBundle = get_active_bundle(self.params, usbgpu=self.chestnut_present)
    self._chunk_size = 128 * 1000  # 128 KB chunks
    self._download_start_times: dict[str, float] = {}  # Track start time per model
    self._download_ref: bytes | str | None = None

  def _download_interrupted(self) -> bool:
    # only removal cancels: a different ref is a queued selection that
    # _release_download_ref leaves in place for the next tick
    return self.params.get("ModelManager_DownloadRef") is None

  def _release_download_ref(self) -> None:
    if self.params.get("ModelManager_DownloadRef") == self._download_ref:
      self.params.remove("ModelManager_DownloadRef")
    self._download_ref = None

  def _sync_artifact_progress(self, source_artifact) -> None:
    """Mirror download progress to all artifacts sharing the same filename in the selected bundle."""
    if not self.selected_bundle:
      return
    for model in self.selected_bundle.models:
      artifact = model.artifact
      if artifact is not source_artifact and artifact.fileName == source_artifact.fileName:
        artifact.downloadProgress.status = source_artifact.downloadProgress.status
        artifact.downloadProgress.progress = source_artifact.downloadProgress.progress
        artifact.downloadProgress.eta = source_artifact.downloadProgress.eta

  def _calculate_eta(self, filename: str, progress: float) -> int:
    """Calculate ETA based on elapsed time and current progress"""
    if filename not in self._download_start_times or progress <= 0:
      return 60  # Default ETA for new downloads

    elapsed_time = time.monotonic() - self._download_start_times[filename]
    if elapsed_time <= 0:
      return 60

    # If we're at X% after Y seconds, we can estimate total time as (Y / X) * 100
    total_estimated_time = (elapsed_time / progress) * 100
    eta = total_estimated_time - elapsed_time

    return max(1, int(eta))  # Return at least 1 second if download is ongoing

  async def _download_file(self, url: str, path: str, model) -> None:
    """Downloads a file with progress tracking"""
    self._download_start_times[model.fileName] = time.monotonic()

    with requests.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:  # noqa: ASYNC210
      response.raise_for_status()
      total_size = int(response.headers.get("content-length", 0))
      bytes_downloaded = 0

      with open(path, 'wb') as f:  # noqa: ASYNC230
        for chunk in response.iter_content(chunk_size=self._chunk_size):  # type: bytes
          f.write(chunk)
          bytes_downloaded += len(chunk)

          if self._download_interrupted():
            raise DownloadCancelled("Download cancelled")

          if total_size > 0:
            progress = (bytes_downloaded / total_size) * 100
            model.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
            model.downloadProgress.progress = progress
            model.downloadProgress.eta = self._calculate_eta(model.fileName, progress)
            self._sync_artifact_progress(model)
            self._report_status()

    # Clean up start time after download completes
    del self._download_start_times[model.fileName]

  async def _download_chunked(self, base_url: str, base_path: str, artifact, skip: frozenset[int] | set[int] = frozenset()) -> None:
    from openpilot.common.file_chunker import get_chunk_name, get_manifest_path

    num_chunks = len(artifact.chunks)
    if num_chunks == 0:
      raise ValueError("No chunks defined in artifact")

    manifest_path = get_manifest_path(base_path)
    self._download_start_times[artifact.fileName] = time.monotonic()

    # Shared connection saves a TCP+TLS handshake per chunk.
    # Keep sequential: the link saturates on one stream and Session is not thread-safe.
    completed = len(skip)
    with requests.Session() as session:
      for i, _ in enumerate(artifact.chunks):
        if i in skip:
          continue
        chunk_url = get_chunk_name(base_url, i, num_chunks)
        chunk_path = get_chunk_name(base_path, i, num_chunks)
        chunk_downloaded = 0
        with session.get(chunk_url, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
          response.raise_for_status()
          chunk_size = int(response.headers.get("content-length", 0))
          with open(chunk_path, 'wb') as f:  # noqa: ASYNC230
            for data in response.iter_content(chunk_size=self._chunk_size):
              f.write(data)
              chunk_downloaded += len(data)
              if self._download_interrupted():
                raise DownloadCancelled("Download cancelled")
              intra = chunk_downloaded / max(chunk_size, 1)
              progress = min(99.0, ((completed + intra) / num_chunks) * 100)
              artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
              artifact.downloadProgress.progress = progress
              artifact.downloadProgress.eta = self._calculate_eta(artifact.fileName, progress)
              self._sync_artifact_progress(artifact)
              self._report_status()
        completed += 1

    with open(manifest_path, 'w') as f:  # noqa: ASYNC230
      f.write(str(num_chunks))
    if os.path.isfile(base_path):  # noqa: ASYNC240
      os.remove(base_path)
    del self._download_start_times[artifact.fileName]

  async def _process_artifact(self, artifact, destination_path: str) -> None:
    if not artifact.downloadUri.uri:
      return None
    if self._download_interrupted():
      raise DownloadCancelled("Download cancelled")

    url = artifact.downloadUri.uri
    expected_hash = artifact.downloadUri.sha256
    filename = artifact.fileName
    full_path = os.path.join(destination_path, filename)

    try:
      # progress counts only valid chunks so a resumed download continues the
      # bar from where verification left it, instead of falling back to zero
      is_cached = False
      valid_chunks: set[int] = set()
      if len(artifact.chunks) > 0:
        from openpilot.common.file_chunker import get_chunk_name
        num_chunks = len(artifact.chunks)
        for i, chunk in enumerate(artifact.chunks):
          if self._download_interrupted():
            raise DownloadCancelled("Download cancelled")
          if await verify_file(get_chunk_name(full_path, i, num_chunks), chunk.sha256):
            valid_chunks.add(i)
          artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.verifying
          artifact.downloadProgress.progress = (len(valid_chunks) / num_chunks) * 100
          self._sync_artifact_progress(artifact)
          self._report_status()
        is_cached = len(valid_chunks) == num_chunks
      else:
        if await verify_file(full_path, expected_hash):
          is_cached = True

      if is_cached:
        artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.cached
        artifact.downloadProgress.progress = 100
        artifact.downloadProgress.eta = 0
        self._sync_artifact_progress(artifact)
        self._report_status()
        return

      if len(artifact.chunks) > 0:
        await self._download_chunked(url, full_path, artifact, skip=valid_chunks)
        from openpilot.common.file_chunker import get_chunk_name
        for i, chunk in enumerate(artifact.chunks):
          chunk_path = get_chunk_name(full_path, i, len(artifact.chunks))
          if not await verify_file(chunk_path, chunk.sha256):
            raise ValueError(f"Hash validation failed for chunk {i+1} of {filename}")
      else:
        await self._download_file(url, full_path, artifact)
        if not await verify_file(full_path, expected_hash):
          raise ValueError(f"Hash validation failed for {filename}")

      artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloaded
      artifact.downloadProgress.progress = 100
      artifact.downloadProgress.eta = 0
      self._sync_artifact_progress(artifact)
      self._report_status()

    except DownloadCancelled:
      # a cancel keeps whatever is on disk: complete chunks resume the next attempt
      self._download_start_times.pop(artifact.fileName, None)
      artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.failed
      artifact.downloadProgress.eta = 0
      self._sync_artifact_progress(artifact)
      if self.selected_bundle:
        self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      self._report_status()
      raise

    except Exception as e:
      cloudlog.error(f"Error downloading {filename}: {str(e)}")
      for f in [full_path] + [p for p in (os.path.join(destination_path, f) for f in os.listdir(destination_path)) if filename in p]:
        if os.path.isfile(f):  # noqa: ASYNC240
          os.remove(f)
      artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.failed
      artifact.downloadProgress.eta = 0
      self._sync_artifact_progress(artifact)
      if self.selected_bundle:
        self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      self._report_status()
      self._download_start_times.pop(artifact.fileName, None)
      raise

  async def _process_model(self, model, destination_path: str) -> None:
    """Processes a single model download including verification"""
    await self._process_artifact(model.artifact, destination_path)

  def _report_status(self) -> None:
    """Reports current status through messaging system"""
    msg = messaging.new_message('modelManagerSP', valid=True)
    model_manager_state = msg.modelManagerSP
    if self.selected_bundle:
      model_manager_state.selectedBundle = self.selected_bundle

    if self.active_bundle:
      model_manager_state.activeBundle = self.active_bundle

    model_manager_state.availableBundles = self.available_models
    self.pm.send('modelManagerSP', msg)

  async def _download_bundle(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str, source: str) -> None:
    self.selected_bundle = model_bundle
    self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloading
    for model in self.selected_bundle.models:
      model.artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
    self._report_status()
    os.makedirs(destination_path, exist_ok=True)

    try:
      seen_artifacts: set[str] = set()
      for model in self.selected_bundle.models:
        artifact = model.artifact
        if not artifact.fileName:
          continue
        if artifact.fileName in seen_artifacts:
          artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.cached
          artifact.downloadProgress.progress = 100
          artifact.downloadProgress.eta = 0
        else:
          seen_artifacts.add(artifact.fileName)
          await self._process_artifact(artifact, destination_path)

      if self._download_interrupted():
        raise DownloadCancelled("Download cancelled")
      self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloaded
      self.params.put(ACTIVE_BUNDLE_KEYS[source], model_bundle.to_dict(), block=True)
      self.active_bundle = get_active_bundle(self.params, usbgpu=self.chestnut_present)

    except Exception:
      if self.selected_bundle is not None:
        self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      raise

    finally:
      self._report_status()

  def download(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str, source: str) -> None:
    """Main entry point for downloading a model bundle"""
    asyncio.run(self._download_bundle(model_bundle, destination_path, source))

  def _process_download_requests(self) -> None:
    # loops so a ref queued during a download starts in the same tick, without
    # the bar dropping to idle for a tick between the two transfers
    last_ref = None
    while (ref_to_download := self.params.get("ModelManager_DownloadRef")) is not None:
      if ref_to_download == last_ref:  # a repeating ref falls back to the next tick instead of spinning
        return
      last_ref = ref_to_download
      resolved = resolve_bundle_by_ref(ref_to_download, self.source_models)
      if not resolved:
        return
      model_to_download, source = resolved
      self._download_ref = ref_to_download
      try:
        self.download(model_to_download, Paths.model_root(), source)
      except Exception as e:
        cloudlog.exception(e)
      finally:
        self._release_download_ref()
        self.selected_bundle = None

  def main_thread(self) -> None:
    """Main thread for model management"""
    rk = Ratekeeper(1, print_delay_threshold=None)

    while True:
      try:
        self.sm.update(0)
        self.chestnut_present = self.sm['deviceState'].chestnutPresent
        self.source_models = {source: self.model_fetcher.get_bundles_for_source(source) for source in ModelFetcher.MODEL_SOURCES}
        self.available_models = self.source_models[ModelFetcher.active_source(self.chestnut_present)]
        validate_active_bundles(self.params, self.source_models)
        self.active_bundle = get_active_bundle(self.params, usbgpu=self.chestnut_present)

        self._process_download_requests()

        if self.params.get("ModelManager_ClearCache"):
          self.clear_model_cache()
          self.params.remove("ModelManager_ClearCache")

        self._report_status()
        rk.keep_time()

      except Exception as e:
        cloudlog.exception(f"Error in main thread: {str(e)}")
        rk.keep_time()

  def clear_model_cache(self) -> None:
    """
    Clears the model cache directory of all files except those in the active model bundle.
    """

    # Get list of files used by both slots' selected bundles (either may become
    # the truly active bundle depending on hardware availability)
    active_files = []
    for source in ACTIVE_BUNDLE_KEYS:
      if selected_bundle := get_selected_bundle(self.params, source):
        for model in selected_bundle.models:
          if model.artifact.fileName:
            active_files.append(model.artifact.fileName)

    # Remove all files except active ones (including their chunk files)
    model_dir = Paths.model_root()
    try:
      for filename in os.listdir(model_dir):
        base = filename.split('.chunk')[0] if '.chunk' in filename else filename
        if base not in active_files and filename not in active_files:
          file_path = os.path.join(model_dir, filename)
          if os.path.isfile(file_path):
            os.remove(file_path)
      cloudlog.info("Model cache cleared, keeping active model files")
    except Exception as e:
      cloudlog.exception(f"Error clearing model cache: {str(e)}")

def main():
  ModelManagerSP().main_thread()


if __name__ == "__main__":
  main()
