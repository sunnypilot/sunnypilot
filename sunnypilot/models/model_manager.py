import asyncio
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, Optional

import aiohttp
import requests

from cereal import messaging, custom
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths

params = Params()


def get_models_from_url(url) -> list[custom.ModelManagerSP.ModelBundle]:
  """
  Fetches models from a given URL and parses them.
  :param url: URL to fetch models from.
  :return: List of ModelBundle objects.
  """
  response = requests.get(url)
  response.raise_for_status()
  json_data = response.json()

  model_bundles = []
  for key, value in json_data.items():
    model_bundle = custom.ModelManagerSP.ModelBundle()
    download_uri = custom.ModelManagerSP.DownloadUri()
    download_uri_nav = custom.ModelManagerSP.DownloadUri()
    download_uri_metadata = custom.ModelManagerSP.DownloadUri()

    download_uri.uri = value["download_uri"]["url"]
    download_uri.sha256 = value["download_uri"]["sha256"]

    if value.get("download_uri_nav"):
      download_uri_nav.uri = value["download_uri_nav"]["url"]
      download_uri_nav.sha256 = value["download_uri_nav"]["sha256"]

    if value.get("download_uri_metadata"):
      download_uri_metadata.uri = value["download_uri_metadata"]["url"]
      download_uri_metadata.sha256 = value["download_uri_metadata"]["sha256"]

    models = []
    driving_model = custom.ModelManagerSP.Model()
    driving_model.fullName = value["full_name"]
    driving_model.fileName = value["file_name"]
    driving_model.downloadUri = download_uri
    driving_model.type = 0
    models.append(driving_model)

    if value.get("download_uri_nav"):
      nav_model = custom.ModelManagerSP.Model()
      nav_model.fullName = value["full_name_nav"]
      nav_model.fileName = value["file_name_nav"]
      nav_model.downloadUri = download_uri_nav
      nav_model.type = 1
      models.append(nav_model)

    if value.get("download_uri_metadata"):
      metadata_model = custom.ModelManagerSP.Model()
      metadata_model.fullName = value["full_name_metadata"]
      metadata_model.fileName = value["file_name_metadata"]
      metadata_model.downloadUri = download_uri_metadata
      metadata_model.type = 2
      models.append(metadata_model)


    model_bundle.index = int(value["index"])
    model_bundle.internalName = key
    model_bundle.displayName = value["display_name"]
    model_bundle.models = models
    model_bundle.status = 0  # Adjust this as needed

    model_bundles.append(model_bundle)

  return model_bundles


class ModelManagerSP:
  def __init__(self):
    self.pm = messaging.PubMaster(["modelManagerSP"])
    self.available_models: list[custom.ModelManagerSP.ModelBundle] = []
    self.selected_bundle: Optional[custom.ModelManagerSP.ModelBundle] = None
    self._executor = ThreadPoolExecutor(max_workers=4)
    self._chunk_size = 128 * 1000  # 128 KB chunks

  def report_status(self):
    """Report current status through messaging system"""
    msg = messaging.new_message('modelManagerSP', valid=True)
    model_manager_state = msg.modelManagerSP
    if self.selected_bundle:
      model_manager_state.selectedBundle = self.selected_bundle
    model_manager_state.availableBundles = self.available_models
    self.pm.send('modelManagerSP', msg)

  @staticmethod
  async def _calculate_hash(file_path: str) -> Tuple[bytes, str]:
    """Calculate SHA256 hash of a file"""
    sha256_hash = hashlib.sha256()
    file_data = b""

    if os.path.exists(file_path):
      with open(file_path, "rb") as file:
        file_data = file.read()
        sha256_hash.update(file_data)

    return file_data, sha256_hash.hexdigest()

  async def verify_file_hash(self, file_path: str, expected_hash: str) -> Tuple[bytes, bool]:
    """
    Verifies the file's hash against the expected hash.
    Returns: Tuple (file_data, hash_matches)
    """
    if not expected_hash:
      return b"", True

    file_data, current_hash = await self._calculate_hash(file_path)
    hash_matches = (current_hash.lower() == expected_hash.lower())
    return file_data if hash_matches else b"", hash_matches

  async def _download_file(self, url: str, full_path: str, model) -> None:
    """Download a single file with progress tracking"""
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0

        with open(full_path, 'wb') as f:
          async for chunk in response.content.iter_chunked(self._chunk_size):
            f.write(chunk)
            bytes_downloaded += len(chunk)
            if total_size > 0:
              model.downloadProgress.status = 1
              model.downloadProgress.progress = (bytes_downloaded / total_size) * 100
              model.downloadProgress.eta = 0
              self.report_status()

  async def _process_model(self, model, destination_path: str) -> None:
    """Process a single model download including verification"""
    url = model.downloadUri.uri
    expected_hash = model.downloadUri.sha256
    filename = model.fileName
    full_path = os.path.join(destination_path, filename)

    try:
      # Check if file exists and hash matches
      _, hash_matches = await self.verify_file_hash(full_path, expected_hash)
      if os.path.exists(full_path) and hash_matches:
        model.downloadProgress.status = 2
        model.downloadProgress.progress = 100
        model.downloadProgress.eta = 0
        self.report_status()
        return

      # Download file
      await self._download_file(url, full_path, model)

      # Verify downloaded file
      _, hash_matches = await self.verify_file_hash(full_path, expected_hash)
      if not hash_matches:
        raise ValueError(f"Hash validation failed for {filename}")

      model.downloadProgress.status = 2
      self.report_status()

    except Exception as e:
      cloudlog.error(f"Error downloading {filename}: {str(e)}")
      if os.path.exists(full_path):
        os.remove(full_path)
      model.downloadProgress.status = 3
      self.selected_bundle.status = 3
      self.report_status()
      raise

  async def _download_all(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """Download all models in parallel"""
    self.selected_bundle = model_bundle
    self.selected_bundle.status = 1
    os.makedirs(destination_path, exist_ok=True)

    try:
      # Create download tasks for all models
      tasks = [
        self._process_model(model, destination_path)
        for model in self.selected_bundle.models
      ]

      # Run downloads in parallel
      await asyncio.gather(*tasks)

      self.selected_bundle.status = 2
      self.report_status()

    except Exception as e:
      self.selected_bundle.status = 3
      self.report_status()
      raise

  def download(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """
    Downloads files from the given ModelBundle.
    This is the main entry point that maintains the same interface as before.
    """
    asyncio.run(self._download_all(model_bundle, destination_path))

  def main_thread(self):
    rk = Ratekeeper(1, print_delay_threshold=None)

    models_url = "https://docs.sunnypilot.ai/models_v5.json"
    self.available_models = get_models_from_url(models_url)

    while True:
      index_of_model_to_download = params.get("ModelManager_DownloadIndex", block=False, encoding="utf-8")
      model_to_download = None
      if index_of_model_to_download:
        for model in self.available_models:
          if model.index == int(index_of_model_to_download):
            model_to_download = model
            break

      if model_to_download:
        try:
          self.download(model_to_download, Paths.model_root())
        except Exception as e:
          cloudlog.exception(e)
        finally:
          params.put("ModelManager_DownloadIndex", "")

      self.report_status()
      rk.keep_time()


if __name__ == "__main__":
  ModelManagerSP().main_thread()
