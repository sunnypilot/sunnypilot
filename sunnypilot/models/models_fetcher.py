import hashlib
import json
import os

from openpilot.common.swaglog import cloudlog
from openpilot.common.realtime import Ratekeeper
from openpilot.common.params import Params
from openpilot.system.hardware.hw import Paths
import cereal.messaging as messaging

import requests
params = Params()

class ModelsFetcher:
  def __init__(self):
    self.pm = messaging.PubMaster(["ModelsFetcher"])

  @staticmethod
  def verify_file_hash(file_path, expected_hash):
    """
    Verifies the file's hash against the expected hash.
    :param file_path: Path to the file to verify.
    :param expected_hash: Expected SHA256 hash of the file.
    :return: Tuple (file_data, hash_matches)
    """
    hash_matches = False
    file_data = b""

    if not expected_hash:
      # If no hash is provided, assume verification isn't required
      hash_matches = True
    else:
      if os.path.exists(file_path):
        with open(file_path, "rb") as file:
          file_data = file.read()
          current_hash = hashlib.sha256(file_data).hexdigest()
          hash_matches = (current_hash == expected_hash)

    # Return the file data if hash matches or no hash was provided; empty otherwise
    return file_data if hash_matches else b"", hash_matches


  def download(self, download_info, filename, destination_path):
    """
    Downloads a file from the given URL.
    :param download_info: Dictionary containing 'url' and 'sha256'.
    :param filename: Name of the file to save as.
    :param destination_path: Directory to save the file.
    :param progress_callback: Optional callback function for download progress.
    """
    url = download_info["url"]
    expected_hash = download_info.get("sha256", "")

    full_path = os.path.join(destination_path, filename)
    os.makedirs(destination_path, exist_ok=True)

    # Verify if the file already exists and its hash matches
    file_data, hash_matches = ModelsFetcher.verify_file_hash(full_path, expected_hash)
    if os.path.exists(full_path) and hash_matches:
      print(f"File already downloaded and verified: {filename}")
      self.progress_report(100)
      return file_data, True

    # Proceed with the download if file does not exist or hash verification failed
    with requests.get(url, stream=True) as response:
      response.raise_for_status()
      total_size = int(response.headers.get("Content-Length", 0))
      bytes_downloaded = 0

      with open(full_path, "wb") as file:
        for chunk in response.iter_content(chunk_size=5120):
          file.write(chunk)
          bytes_downloaded += len(chunk)
          if total_size > 0:
           self.progress_report(((bytes_downloaded / total_size) * 100))

    # Verify the hash after download
    _, hash_matches = ModelsFetcher.verify_file_hash(full_path, expected_hash)
    if not hash_matches:
      print(f"The downloaded file didn't pass hash validation: {filename}")
      os.remove(full_path)
      raise ValueError("Hash validation failed!")

    print(f"Download complete and verified: {filename}")
    return file_data, False

  @staticmethod
  def extract_file_name(content_disposition):
    """
    Extracts filename from Content-Disposition header.
    :param content_disposition: Content-Disposition header value.
    :return: Extracted filename or None.
    """
    filename_tag = "filename="
    idx = content_disposition.find(filename_tag)
    if idx == -1:
      return None

    filename = content_disposition[idx + len(filename_tag):]
    if filename.startswith('"') and filename.endswith('"'):
      return filename[1:-1]
    return filename

  @staticmethod
  def get_models_from_url(url):
    """
    Fetches models from a given URL and parses them.
    :param url: URL to fetch models from.
    :return: List of parsed models (example format, adjust as needed).
    """
    response = requests.get(url)
    response.raise_for_status()
    json_data = response.json()

    return [{"model_name": key, **value} for key, value in json_data.items()]


  # Example usage:
  def progress_report(self, progress):
    model_selector_msg = messaging.new_message('modelSelectorSP')
    model_selector_msg.valid = True
    model_selector_sp = model_selector_msg.modelSelectorSP
    download_progress = model_selector_sp.downloadProgress
    download_progress.status = 0
    download_progress.progress = progress
    download_progress.eta = 0
    self.pm.send('ModelsFetcher', model_selector_msg)

# if __name__ == "__main__":
#
#   fetcher = ModelsFetcher()
#
#   # Fetch models
#   models_url = "https://docs.sunnypilot.ai/models_v5.json"
#   models = fetcher.get_models_from_url(models_url)
#
#
#   test = models[1]
#   try:
#     fetcher.download(test.get('download_uri'), test.get('file_name'), "./downloads", progress_callback=progress_report)
#   except Exception as e:
#     print(f"Error: {e}")



def main_thread(sm=None, pm=None):
  rk = Ratekeeper(1, print_delay_threshold=None)
  fetcher = ModelsFetcher()

  while True:
    model_to_download = params.get("ModelsFetcher_DownloadRequested", block=False, encoding="utf-8")
    if model_to_download:
      try:
        model_data = json.loads(model_to_download)
        fetcher.download(model_data.get('download_uri'), model_data.get('file_name'), Paths.model_root())

        model_uri_nav = model_data.get('download_uri_nav')
        if model_uri_nav:
          fetcher.download(model_uri_nav, model_data.get('file_name_nav'), Paths.model_root())

        model_uri_metadata = model_data.get('download_uri_metadata')
        if model_uri_metadata:
          fetcher.download(model_data.get('download_uri_metadata'), model_data.get('file_name_metadata'), Paths.model_root())
      except Exception as e:
        cloudlog.exception(e)
      finally:
        params.put("ModelsFetcher_DownloadRequested", "")

    rk.keep_time()


def main():
  main_thread()


if __name__ == "__main__":
  main()
