import asyncio
import os
from typing import Optional

import aiohttp
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths

from cereal import messaging, custom
from sunnypilot.models.model_fetcher import ModelFetcher
from sunnypilot.models.model_helper import verify_file


class ModelManagerSP:
  """Manages model downloads and status reporting"""

  def __init__(self):
    self.params = Params()
    self.model_fetcher = ModelFetcher(self.params)
    self.pm = messaging.PubMaster(["modelManagerSP"])
    self.available_models: list[custom.ModelManagerSP.ModelBundle] = []
    self.selected_bundle: Optional[custom.ModelManagerSP.ModelBundle] = None
    self._chunk_size = 128 * 1000  # 128 KB chunks

  async def _download_file(self, url: str, path: str, model) -> None:
    """Downloads a file with progress tracking"""
    async with aiohttp.ClientSession() as session:
      async with session.get(url) as response:
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        bytes_downloaded = 0

        with open(path, 'wb') as f:
          async for chunk in response.content.iter_chunked(self._chunk_size):  # type: bytes
            f.write(chunk)
            bytes_downloaded += len(chunk)
            if total_size > 0:
              model.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
              model.downloadProgress.progress = (bytes_downloaded / total_size) * 100
              model.downloadProgress.eta = 0
              self._report_status()

  async def _process_model(self, model, destination_path: str) -> None:
    """Processes a single model download including verification"""
    url = model.downloadUri.uri
    expected_hash = model.downloadUri.sha256
    filename = model.fileName
    full_path = os.path.join(destination_path, filename)

    try:
      # Check existing file
      if os.path.exists(full_path) and await verify_file(full_path, expected_hash):
        model.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloaded
        model.downloadProgress.progress = 100
        model.downloadProgress.eta = 0
        self._report_status()
        return

      # Download and verify
      await self._download_file(url, full_path, model)
      if not await verify_file(full_path, expected_hash):
        raise ValueError(f"Hash validation failed for {filename}")

      model.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloaded
      self._report_status()

    except Exception as e:
      cloudlog.error(f"Error downloading {filename}: {str(e)}")
      if os.path.exists(full_path):
        os.remove(full_path)
      model.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.failed
      self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      self._report_status()
      raise

  def _report_status(self) -> None:
    """Reports current status through messaging system"""
    msg = messaging.new_message('modelManagerSP', valid=True)
    model_manager_state = msg.modelManagerSP
    if self.selected_bundle:
      model_manager_state.selectedBundle = self.selected_bundle
    model_manager_state.availableBundles = self.available_models
    self.pm.send('modelManagerSP', msg)

  async def _download_bundle(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """Downloads all models in a bundle"""
    self.selected_bundle = model_bundle
    self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloading
    os.makedirs(destination_path, exist_ok=True)

    try:
      tasks = [self._process_model(model, destination_path)
               for model in self.selected_bundle.models]
      await asyncio.gather(*tasks)
      self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloaded

    except Exception as e:
      self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      raise

    finally:
      self._report_status()

  def download(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str) -> None:
    """Main entry point for downloading a model bundle"""
    asyncio.run(self._download_bundle(model_bundle, destination_path))

  def main_thread(self) -> None:
    """Main thread for model management"""
    rk = Ratekeeper(1, print_delay_threshold=None)

    while True:
      try:
        self.available_models = self.model_fetcher.get_available_models()

        index_to_download = self.params.get("ModelManager_DownloadIndex",
                                            block=False, encoding="utf-8")
        if index_to_download:
          model_to_download = next(
            (model for model in self.available_models
             if model.index == int(index_to_download)),
            None
          )

          if model_to_download:
            try:
              self.download(model_to_download, Paths.model_root())
            except Exception as e:
              cloudlog.exception(e)
            finally:
              self.params.put("ModelManager_DownloadIndex", "")

        self._report_status()
        rk.keep_time()

      except Exception as e:
        cloudlog.exception(f"Error in main thread: {str(e)}")
        rk.keep_time()


if __name__ == "__main__":
  ModelManagerSP().main_thread()
