#!/usr/bin/env python3
import os
import time
import traceback
import urllib.request
import stat
from openpilot.selfdrive.mapd_manager import COMMON_DIR, MAPD_PATH, VERSION_PATH
from urllib.request import urlopen

VERSION = 'v1.7.0'
URL = f"https://github.com/pfeiferj/openpilot-mapd/releases/download/{VERSION}/mapd"



# NOTE: Do NOT import anything here that needs be built (e.g. params)
from common.spinner import Spinner
from common.text_window import TextWindow
import selfdrive.sentry as sentry

class MapdInstallManager:
  def download(self):
    self._create_directory()
    self._download_file()
    self._store_version()

  def check_and_download(self):
    if self.download_needed():
      self.download()

  def download_needed(self):
    return not self._is_exists() or self._needs_update()

  def _create_directory(self):
    if not os.path.exists(COMMON_DIR):
      os.makedirs(COMMON_DIR)

  def _download_file(self):
    with urllib.request.urlopen(URL) as f:
      with open(MAPD_PATH, 'wb') as output:
        output.write(f.read())
        os.fsync(output.fileno())
        current_permissions = stat.S_IMODE(os.lstat(MAPD_PATH).st_mode)
        os.chmod(MAPD_PATH, current_permissions | stat.S_IEXEC)

  def _store_version(self):
    with open(VERSION_PATH, 'w') as output:
      output.write(VERSION)
      os.fsync(output.fileno())

  def _is_exists(self):
    return os.path.exists(MAPD_PATH) and os.path.exists(VERSION_PATH)

  def _needs_update(self):
    with open(VERSION_PATH) as f:
      return f.read() != VERSION

def wait_for_internet_connection(return_on_failure=False):
  retries = 0
  while True:
    try:
      _ = urlopen('https://www.google.com/', timeout=10)
      return True
    except Exception as e:
      print(f'Wait for internet failed: {e}')
      if return_on_failure and retries == 15:
        return False
      retries += 1
      time.sleep(2)  # Wait for 2 seconds before retrying


if __name__ == "__main__":
  try:
    install_manager = MapdInstallManager()
    spinner = Spinner()
    spinner.update("Checking if mapd is installed and valid")
    if not install_manager.download_needed():
      spinner.update("Mapd is good!")
      exit(0)

    spinner.update("Waiting for internet connection...")
    if wait_for_internet_connection(return_on_failure=True):
      spinner.update(f"Downloading pfeiferj's mapd [{VERSION}]")
      install_manager.check_and_download()
    spinner.close()

  except Exception:
    sentry.init(sentry.SentryProject.SELFDRIVE)
    traceback.print_exc()
    sentry.capture_exception()

    error = traceback.format_exc(-3)
    error = "OSM Offline Database Manager failed to start\n\n" + error
    with TextWindow(error) as t:
      t.wait_for_exit()
