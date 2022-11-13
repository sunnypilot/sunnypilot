#!/usr/bin/env python3
import os
import subprocess

# NOTE: Do NOT import anything here that needs be built (e.g. params)
from common.basedir import BASEDIR
from common.params import Params
from common.spinner import Spinner
from selfdrive.hardware import TICI
from selfdrive.mapd.lib.helpers import is_local_osm_installed, timestamp_local_osm_db, is_osm_db_up_to_date
from selfdrive.manager.custom_dep import wait_for_internet_connection


MAX_BUILD_PROGRESS = 100
INSTALL_OSM_STEPS = 1021
INSTALL_DB_STEPS = 58

OSM_LOCAL_PATH = "/data/media/0/osm"


def install_local_osm(spinner, steps=0, total_steps=INSTALL_OSM_STEPS + INSTALL_DB_STEPS):
  osm_install = subprocess.Popen(['sh', './install_osm.sh'], cwd=os.path.join(BASEDIR, 'installer/custom/'),
                                 stdout=subprocess.PIPE)
  # Read progress from install script and update spinner
  while True:
    output = osm_install.stdout.readline()
    if osm_install.poll() is not None:
      break
    if output:
      steps += 1
      spinner.update_progress(MAX_BUILD_PROGRESS * min(1., steps / total_steps), 100.)
      print(output.decode('utf8', 'replace'))


def install_osm_db(spinner, steps=0, total_steps=INSTALL_DB_STEPS):
  # Fetch and get db
  fetch_osm_db = subprocess.Popen(['sh', './install_osm_db.sh'], cwd=os.path.join(BASEDIR, 'installer/custom/'),
                                  stdout=subprocess.PIPE)
   #Read progress from install script and update spinner
  while True:
    output = fetch_osm_db.stdout.readline()
    if fetch_osm_db.poll() is not None:
      break
    if output:
      steps += 1
      spinner.update_progress(MAX_BUILD_PROGRESS * min(1., steps / total_steps), 100.)
      print(output.decode('utf8', 'replace'))


if __name__ == "__main__" and TICI:
  if not (os.path.exists(f"{OSM_LOCAL_PATH}/db") or
          os.path.exists(f"{OSM_LOCAL_PATH}/v0.7.57")) or Params().get_bool("UpdatesOsmDbCheck"):
    if wait_for_internet_connection(return_on_failure=True):
      is_osm_installed = is_local_osm_installed()
      is_db_updated = is_osm_db_up_to_date()
      print(f'Local OSM Installer:\nOSM currently installed: {is_osm_installed}\nDB up to date: {is_db_updated}')

      if is_osm_installed and (is_db_updated or not Params().get_bool("UpdatesOsmDbCheck")):
        pass
      else:
        spinner = Spinner()
        spinner.update_progress(0, 100)

        if is_osm_installed and not is_db_updated:
          install_osm_db(spinner)
        elif not is_osm_installed and is_db_updated:
          install_local_osm(spinner)
        else:
          install_local_osm(spinner)
          install_osm_db(spinner, steps=INSTALL_OSM_STEPS, total_steps=INSTALL_OSM_STEPS + INSTALL_DB_STEPS)

        timestamp_local_osm_db()

  Params().put_bool("UpdatesOsmDbCheck", False)
