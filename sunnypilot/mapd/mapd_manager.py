#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json
import platform
import os
import glob
import shutil
from datetime import datetime

from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper, config_realtime_process
from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.selfdrived.alertmanager import set_offroad_alert
from openpilot.sunnypilot.mapd.live_map_data.osm_map_data import OsmMapData
from openpilot.system.hardware.hw import Paths
from openpilot.sunnypilot.mapd import MAPD_PATH
from openpilot.sunnypilot.mapd.mapd_installer import VERSION, update_installed_version

# PFEIFER - MAPD {{
params = Params()
mem_params = Params("/dev/shm/params") if platform.system() != "Darwin" else params
# }} PFEIFER - MAPD


def get_files_for_cleanup() -> list[str]:
  paths = [
    f"{Paths.mapd_root()}/db",
    f"{Paths.mapd_root()}/v*"
  ]
  files_to_remove = []
  for path in paths:
    if os.path.exists(path):
      files = glob.glob(path + '/**', recursive=True)
      files_to_remove.extend(files)
  # check for version and mapd files
  if not os.path.isfile(MAPD_PATH):
    files_to_remove.append(MAPD_PATH)
  return files_to_remove


def cleanup_old_osm_data(files_to_remove: list[str]) -> None:
  for file in files_to_remove:
    # Remove trailing slash if path is file
    if file.endswith('/') and os.path.isfile(file[:-1]):
      file = file[:-1]
    # Try to remove as file or symbolic link first
    if os.path.islink(file) or os.path.isfile(file):
      os.remove(file)
    elif os.path.isdir(file):  # If it's a directory
      shutil.rmtree(file, ignore_errors=False)


def request_refresh_osm_location_data(nations: list[str], states: list[str] = None) -> None:
  params.put("OsmDownloadedDate", str(datetime.now().timestamp()))
  params.put_bool("OsmDbUpdatesCheck", False)

  osm_download_locations = {
    "nations": nations,
    "states": states or []
  }

  osm_download_locations_dump = json.dumps({
    "nations": nations,
    "states": states or []
  })

  print(f"Downloading maps for {osm_download_locations_dump}")
  mem_params.put("OSMDownloadLocations", osm_download_locations)


def filter_nations_and_states(nations: list[str], states: list[str] = None) -> tuple[list[str], list[str]]:
  """Filters and prepares nation and state data for OSM map download.

  If the nation is 'US' and a specific state is provided, the nation 'US' is removed from the list.
  If the nation is 'US' and the state is 'All', the 'All' is removed from the list.
  The idea behind these filters is that if a specific state in the US is provided,
  there's no need to download map data for the entire US. Conversely,
  if the state is unspecified (i.e., 'All'), we intend to download map data for the whole US,
  and 'All' isn't a valid state name, so it's removed.

  Parameters:
  nations (list): A list of nations for which the map data is to be downloaded.
  states (list, optional): A list of states for which the map data is to be downloaded. Defaults to None.

  Returns:
  tuple: Two lists. The first list is filtered nations and the second list is filtered states.
  """

  if "US" in nations and states and not any(x.lower() == "all" for x in states):
    # If a specific state in the US is provided, remove 'US' from nations
    nations.remove("US")
  elif "US" in nations and states and any(x.lower() == "all" for x in states):
    # If 'All' is provided as a state (case invariant), remove those instances from states
    states = [x for x in states if x.lower() != "all"]
  elif "US" not in nations and states and any(x.lower() == "all" for x in states):
    states.remove("All")
  return nations, states or []


def update_osm_db() -> None:
  # last_downloaded_date = params.get("OsmDownloadedDate", return_default=True)
  # if params.get_bool("OsmDbUpdatesCheck") or time.monotonic() - last_downloaded_date >= 604800:  # 7 days * 24 hours/day * 60
  if params.get_bool("OsmDbUpdatesCheck"):
    cleanup_old_osm_data(get_files_for_cleanup())
    country = params.get("OsmLocationName", return_default=True)
    state = params.get("OsmStateName", return_default=True)
    filtered_nations, filtered_states = filter_nations_and_states([country], [state])
    request_refresh_osm_location_data(filtered_nations, filtered_states)

  if not mem_params.get("OSMDownloadBounds"):
    mem_params.put("OSMDownloadBounds", "")

  if not mem_params.get("LastGPSPosition"):
    mem_params.put("LastGPSPosition", "{}")


def main_thread():
  update_installed_version(VERSION, params)
  config_realtime_process([0, 1, 2, 3], 5)

  rk = Ratekeeper(1, print_delay_threshold=None)
  live_map_sp = OsmMapData()

  # Create folder needed for OSM
  try:
    os.mkdir(Paths.mapd_root())
  except FileExistsError:
    pass
  except PermissionError:
    cloudlog.exception(f"mapd: failed to make {Paths.mapd_root()}")

  while True:
    show_alert = get_files_for_cleanup() and params.get_bool("OsmLocal")
    set_offroad_alert("Offroad_OSMUpdateRequired", show_alert, "This alert will be cleared when new maps are downloaded.")

    update_osm_db()
    live_map_sp.tick()
    rk.keep_time()


def main():
  main_thread()


if __name__ == "__main__":
  main()
