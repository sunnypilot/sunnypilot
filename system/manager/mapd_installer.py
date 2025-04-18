#!/usr/bin/env python3
import logging
import os
import stat
import time
import traceback
import requests
from pathlib import Path
from urllib.request import urlopen
import openpilot.system.sentry as sentry
from cereal import messaging
from common.spinner import Spinner
from common.params import Params
from openpilot.system.mapd_manager import COMMON_DIR, MAPD_PATH, MAPD_BIN_DIR
from openpilot.system.version import is_prebuilt

VERSION = 'v1.9.0'
URL = f"https://github.com/pfeiferj/openpilot-mapd/releases/download/{VERSION}/mapd"


class MapdInstallManager:
  def __init__(self, spinner_ref: Spinner):
    self._spinner = spinner_ref

  def download(self):
    self.ensure_directories_exist()
    self._download_file()
    self.update_installed_version(VERSION)

  def check_and_download(self):
    if self.download_needed():
      self.download()

  @staticmethod
  def download_needed():
    return not os.path.exists(MAPD_PATH) or MapdInstallManager.get_installed_version() != VERSION

  @staticmethod
  def ensure_directories_exist():
    if not os.path.exists(COMMON_DIR):
      os.makedirs(COMMON_DIR)
    if not os.path.exists(MAPD_BIN_DIR):
      os.makedirs(MAPD_BIN_DIR)

  @staticmethod
  def _safe_write_and_set_executable(file_path, content):
    with open(file_path, 'wb') as output:
      output.write(content)
      output.flush()
      os.fsync(output.fileno())
    current_permissions = stat.S_IMODE(os.lstat(file_path).st_mode)
    os.chmod(file_path, current_permissions | stat.S_IEXEC)

  def _download_file(self, num_retries=5):
    temp_file = Path(MAPD_PATH + ".tmp")
    download_timeout = 60
    for cnt in range(num_retries):
      try:
        response = requests.get(URL, stream=True, timeout=download_timeout)
        response.raise_for_status()
        self._safe_write_and_set_executable(temp_file, response.content)
        # No exceptions encountered. Safe to replace original file.
        temp_file.replace(MAPD_PATH)
        return
      except requests.exceptions.ReadTimeout:
        self._spinner.update(f"ReadTimeout caught. Timeout is [{download_timeout}]. Retrying download... [{cnt}]")
        time.sleep(0.5)
      except requests.exceptions.RequestException as e:
        self._spinner.update(f"RequestException caught: {e}. Retrying download... [{cnt}]")
        time.sleep(0.5)

    # Delete temp file if the process was not successful.
    if temp_file.exists():
      temp_file.unlink()
    logging.error("Failed to download file after all retries")

  @staticmethod
  def update_installed_version(version):
    Params().put("MapdVersion", version)

  @staticmethod
  def get_installed_version():
    return Params().get("MapdVersion", encoding="utf-8")

  def wait_for_internet_connection(self, return_on_failure=False):
    max_retries = 10
    for retries in range(max_retries+1):
      self._spinner.update(f"Waiting for internet connection... [{retries}/{max_retries}]")
      time.sleep(2)
      try:
        _ = urlopen('https://sentry.io', timeout=10)
        return True
      except Exception as e:
        print(f'Wait for internet failed: {e}')
        if return_on_failure and retries == max_retries:
          return False

  def non_prebuilt_install(self):
    sm = messaging.SubMaster(['deviceState'])
    metered = sm['deviceState'].networkMetered

    if metered:
      self._spinner.update(f"Can't proceed with mapd install since network is metered!")
      time.sleep(5)
      return False

    try:
      self.ensure_directories_exist()
      if not self.download_needed():
        self._spinner.update("Mapd is good!")
        time.sleep(0.1)
        return True

      if self.wait_for_internet_connection(return_on_failure=True):
        self._spinner.update(f"Downloading pfeiferj's mapd [{install_manager.get_installed_version()}] => [{VERSION}].")
        time.sleep(0.1)
        self.check_and_download()
      self._spinner.close()

    except Exception:
      for i in range(6):
        self._spinner.update(f"Failed to download OSM maps won't work until properly downloaded!"
                             f"Try again manually rebooting. "
                             f"Boot will continue in {5 - i}s...")
        time.sleep(1)

      sentry.init(sentry.SentryProject.SELFDRIVE)
      traceback.print_exc()
      sentry.capture_exception()


if __name__ == "__main__":
  spinner = Spinner()
  install_manager = MapdInstallManager(spinner)
  install_manager.ensure_directories_exist()
  if is_prebuilt():
    debug_msg = f"[DEBUG] This is prebuilt, no mapd install required. VERSION: [{VERSION}], Param [{install_manager.get_installed_version()}]"
    spinner.update(debug_msg)
    install_manager.update_installed_version(VERSION)
  else:
    spinner.update(f"Checking if mapd is installed and valid. Prebuilt [{is_prebuilt()}]")
    install_manager.non_prebuilt_install()
