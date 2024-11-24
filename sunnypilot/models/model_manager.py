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

MODEL_STATUS_NOT_DOWNLOADING = 0
MODEL_STATUS_DOWNLOADING = 1
MODEL_STATUS_DOWNLOADED = 2
MODEL_STATUS_ERROR = 3


def fetch_model_data(value):
  download_uri = custom.ModelManagerSP.DownloadUri(uri=value["download_uri"]["url"], sha256=value["download_uri"]["sha256"])
  download_uri_nav = custom.ModelManagerSP.DownloadUri(uri=value.get("download_uri_nav", {}).get("url", ""),
                                                       sha256=value.get("download_uri_nav", {}).get("sha256", ""))
  download_uri_metadata = custom.ModelManagerSP.DownloadUri(uri=value.get("download_uri_metadata", {}).get("url", ""),
                                                            sha256=value.get("download_uri_metadata", {}).get("sha256", ""))
  models = [custom.ModelManagerSP.Model(fullName=value["full_name"], fileName=value["file_name"], downloadUri=download_uri, type=0)]
  if download_uri_nav.uri:
    models.append(
      custom.ModelManagerSP.Model(fullName=value["full_name_nav"], fileName=value["file_name_nav"], downloadUri=download_uri_nav, type=1))
  if download_uri_metadata.uri:
    models.append(custom.ModelManagerSP.Model(fullName=value["full_name_metadata"], fileName=value["file_name_metadata"],
                                              downloadUri=download_uri_metadata, type=2))
  return models


def get_models_from_url(url) -> list[custom.ModelManagerSP.ModelBundle]:
  response = requests.get(url)
  response.raise_for_status()
  json_data = response.json()
  model_bundles = []
  for key, value in json_data.items():
    models = fetch_model_data(value)
    model_bundle = custom.ModelManagerSP.ModelBundle(index=int(value["index"]),
                                                     internalName=key,
                                                     displayName=value["display_name"],
                                                     models=models,
                                                     status=MODEL_STATUS_NOT_DOWNLOADING)
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
    """Verifies the file's hash against the expected hash."""
    if not expected_hash:
      return b"", True
    file_data, current_hash = await self._calculate_hash(file_path)
    return file_data if current_hash.lower() == expected_hash.lower() else b"", current_hash.lower() == expected_hash.lower()

  async def _write_chunk(self, file, chunk):
    """Write chunk to file using executor to avoid blocking"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(self._executor, file.write, chunk)

  async def _download_file(self, url: str, full_path: str, model) -> None:
    """Download a single file with progress tracking"""
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0
        with open(full_path, 'wb') as f:
          while True:
            chunk = await response.content.read(self._chunk_size)
            if not chunk:
              break
            await self._write_chunk(f, chunk)
            bytes_downloaded += len(chunk)
            if total_size > 0:
              model.downloadProgress.status = MODEL_STATUS_DOWNLOADING
              model.downloadProgress.progress = (bytes_downloaded / total_size) * 100
              model.downloadProgress.eta = 0
              self.report_status()

  async def _process_model(self, model, destination_path: str) -> None:
    """Process a single model download including verification"""
    full_path = os.path.join(destination_path, model.fileName)
    try:
      if os.path.exists(full_path):
        _, hash_matches = await self.verify_file_hash(full_path, model.downloadUri.sha256)
        if hash_matches:
          model.downloadProgress.status = MODEL_STATUS_DOWNLOADED
          model.downloadProgress.progress = 100
          model.downloadProgress.eta = 0
          self.report_status()
          return
      await self._download_file(model.downloadUri.uri, full_path, model)
      _, hash_matches = await self.verify_file_hash(full_path, model.downloadUri.sha256)
      if not hash_matches:
        raise ValueError(f"Hash validation failed for {model.fileName}")
      model.downloadProgress.status = MODEL_STATUS_DOWNLOADED
      self.report_status()
    except Exception as e:
      cloudlog.error(f"Error downloading {model.fileName}: {str(e)}")
      if os.path.exists(full_path):
        os.remove(full_path)
      model.downloadProgress.status = MODEL_STATUS_ERROR
      self.selected_bundle.status = MODEL_STATUS_ERROR
      self.report_status()
      raise

  async def _download_all(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """Download all models in parallel"""
    self.selected_bundle = model_bundle
    self.selected_bundle.status = MODEL_STATUS_DOWNLOADING
    os.makedirs(destination_path, exist_ok=True)
    download_tasks = [self._process_model(model, destination_path) for model in self.selected_bundle.models]
    await asyncio.gather(*download_tasks)
    self.selected_bundle.status = MODEL_STATUS_DOWNLOADED
    self.report_status()

  def download(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """Maintain the same interface for downloading files."""
    asyncio.run(self._download_all(model_bundle, destination_path))

  def main_thread(self):
    rk = Ratekeeper(1, print_delay_threshold=None)
    models_url = "https://docs.sunnypilot.ai/models_v5.json"
    self.available_models = get_models_from_url(models_url)
    while True:
      index_of_model_to_download = params.get("ModelManager_DownloadIndex", block=False, encoding="utf-8")
      model_to_download = next((model for model in self.available_models if model.index == int(index_of_model_to_download)),
                               None) if index_of_model_to_download else None
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
