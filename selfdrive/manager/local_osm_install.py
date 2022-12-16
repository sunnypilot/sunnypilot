#!/usr/bin/env python3
import os
import subprocess

# NOTE: Do NOT import anything here that needs be built (e.g. params)
from common.basedir import BASEDIR
from common.params import Params
from common.spinner import Spinner
from selfdrive.mapd.lib.helpers import is_local_osm_installed, timestamp_local_osm_db, is_osm_db_up_to_date, OSM_LOCAL_PATH
from selfdrive.manager.custom_dep import wait_for_internet_connection
import time

# MAX_BUILD_PROGRESS = 100
# INSTALL_OSM_STEPS = 1021
# INSTALL_DB_STEPS = 58

def install_local_osm(spinner): #, steps=0, total_steps=INSTALL_OSM_STEPS):
  _install(spinner, "./install_osm.sh", "Installing OSM Server") #, steps, total_steps)

def install_osm_db(spinner): #, steps=0, total_steps=INSTALL_DB_STEPS):
  _install(spinner, "./install_osm_db.sh", "Installing OSM DB - " + Params().get("OsmLocationName", encoding="utf-8")) #, steps, total_steps)

def _install(spinner, script, title): #, steps, total_steps):
  spinner.update(title)
  process = subprocess.Popen(['sh', script], cwd=os.path.join(BASEDIR, 'installer/custom/'),
                             stdout=subprocess.PIPE)
  # Read progress from install script and update spinner
  frame = 0
  while True:
    output = process.stdout.readline()
    if process.poll() is not None:
      break
    spinner.update(title + (".".replace(".", "." * (frame % 5), 1)))
    frame += 1
    print(output.decode('utf8', 'replace'))
    time.sleep(0.1)
    # if output:
    #   steps += 1
    #   spinner.update(title + ": " + str(int(min(MAX_BUILD_PROGRESS * min(1., steps / total_steps), 100.))) + "%")
    #   print(output.decode('utf8', 'replace'))

if __name__ == "__main__":
  update_osm_db_check = Params().get_bool("OsmDbUpdatesCheck")
  if not (os.path.exists(f"{OSM_LOCAL_PATH}/db") or
          os.path.exists(f"{OSM_LOCAL_PATH}/v0.7.57")) or update_osm_db_check:
    spinner = Spinner()
    spinner.update("Waiting for internet connection...")
    if wait_for_internet_connection(return_on_failure=True):
      is_osm_installed = is_local_osm_installed()
      is_db_updated = is_osm_db_up_to_date()
      print(f'Local OSM Installer:\nOSM currently installed: {is_osm_installed}\nDB up to date: {is_db_updated}')

      if not is_osm_installed:
        install_local_osm(spinner) #, total_steps=INSTALL_OSM_STEPS)
      if not is_db_updated or update_osm_db_check:
        install_osm_db(spinner) #, total_steps=INSTALL_DB_STEPS)
        timestamp_local_osm_db()
    spinner.close()

  Params().put_bool("OsmDbUpdatesCheck", False)
