#!/usr/bin/env python3
import os
import subprocess
import sys
import time
import traceback

# NOTE: Do NOT import anything here that needs be built (e.g. params)
from common.basedir import BASEDIR
from common.params import Params
from common.spinner import Spinner
from common.text_window import TextWindow
import selfdrive.sentry as sentry
from selfdrive.manager.custom_dep import wait_for_internet_connection


def install_local_osm(_spinner):
  _install(_spinner, "./install_osm.sh", "Installing OSM Server")


def install_osm_db(_spinner):
  _install(_spinner, "./install_osm_db.sh", "Installing OSM DB - " + Params().get("OsmLocationName", encoding="utf-8"))


def _install(_spinner, script, title):
  _spinner.update(title)
  process = subprocess.Popen(['sh', script], cwd=os.path.join(BASEDIR, 'installer/custom/'),
                             stdout=subprocess.PIPE)
  # Read progress from install script and update spinner
  frame = 0
  while True:
    output = process.stdout.readline()
    if process.poll() is not None:
      break
    _spinner.update(title + (".".replace(".", "." * (frame % 5), 1)))
    frame += 1
    print(output.decode('utf8', 'replace'))
    time.sleep(0.1)


if __name__ == "__main__":
  try:
    from selfdrive.mapd.lib.helpers import is_local_osm_installed, timestamp_local_osm_db, is_osm_db_up_to_date, OSM_LOCAL_PATH
    sys.path.append(os.path.join(BASEDIR, "third_party/mapd"))
    params = Params()
    update_osm_db_check = params.get_bool("OsmDbUpdatesCheck")
    if not (os.path.exists(f"{OSM_LOCAL_PATH}/db") or
            os.path.exists(f"{OSM_LOCAL_PATH}/v0.7.57")) or update_osm_db_check:
      spinner = Spinner()
      spinner.update("Waiting for internet connection...")
      if wait_for_internet_connection(return_on_failure=True):
        is_osm_installed = is_local_osm_installed(params)
        is_db_updated = is_osm_db_up_to_date()
        print(f'Local OSM Installer:\nOSM currently installed: {is_osm_installed}\nDB up to date: {is_db_updated}')

        if not is_osm_installed:
          install_local_osm(spinner)
        if not is_db_updated:
          install_osm_db(spinner)
          timestamp_local_osm_db()
      spinner.close()

    params.put_bool("OsmDbUpdatesCheck", False)
  except Exception:
    sentry.init(sentry.SentryProject.SELFDRIVE)
    traceback.print_exc()
    sentry.capture_exception()

    error = traceback.format_exc(-3)
    error = "OSM Offline Database Manager failed to start\n\n" + error
    with TextWindow(error) as t:
      t.wait_for_exit()
