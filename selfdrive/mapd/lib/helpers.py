import overpy
import subprocess
import email.utils as eut
import time

from common.params import Params
from system.version import get_version
from urllib.request import Request, urlopen


OSM_LOCAL_PATH = "/data/media/0/osm"
OSM_DB_STAMP_FILE = OSM_LOCAL_PATH + "/db_stamp"
OSM_QUERY = [f"{OSM_LOCAL_PATH}/v0.7.57/bin/osm3s_query", f"--db-dir={OSM_LOCAL_PATH}/db"]
OSM_DB_STAMP_REMOTE = "https://sunnypilot-osm.s3.us-east-2.amazonaws.com/osm-db/timestamps"


def get_current_s3_osm_db_timestamp():
  try:
    local_osm_db_name = Params().get("OsmLocationName", encoding="utf8")
    req = Request(url=f"{OSM_DB_STAMP_REMOTE}/{local_osm_db_name}.txt", headers={"User-Agent": f"sunnypilot-{get_version()}"})
    r = urlopen(req)
    if r.status != 200:
      print(f'Failed to fetch timestamp for S3 OSM db.\n\n{r.status}')
      return None

    timestamp_string = r.read().decode("utf-8").strip()
    if timestamp_string is None:
      print('Timestamp file for S3 OSM db contained no value.')
      return None

    parsed_date = eut.parsedate(timestamp_string)
    return time.mktime(parsed_date)
  except Exception as e:
    print(f'Could not parse timestamp for S3 local osm db.\n\n{e}')
    return None


def persist_s3_osm_db_timestamp(timestamp):
  try:
    with open(OSM_DB_STAMP_FILE, 'w') as file:
      file.write(f'{timestamp}')
  except Exception as e:
    print(f'Failed to timestamp local OSM db.\n\n{e}')


def get_local_osm_timestamp():
  try:
    with open(OSM_DB_STAMP_FILE, 'r') as file:
      return float(file.readline())
  except Exception as e:
    print(f'Failed to read timestamp for local OSM db.\n\n{e}')
    return None


def is_osm_db_up_to_date():
  current_osm_ts = get_local_osm_timestamp()
  if current_osm_ts is None:
    return False

  current_s3_osm_ts = get_current_s3_osm_db_timestamp()
  if current_s3_osm_ts is None:
    return True

  return current_osm_ts == current_s3_osm_ts


def timestamp_local_osm_db():
  current_s3_osm_ts = get_current_s3_osm_db_timestamp()
  if current_s3_osm_ts is not None:
    persist_s3_osm_db_timestamp(current_s3_osm_ts)


def is_local_osm_installed(params=Params()):
  api = overpy.Overpass()
  waypoint = params.get("OsmWayTest", encoding="utf8")
  if waypoint is None:
    return False
  q = f"""
      way({waypoint});
      (._;>;);
      out;
      """

  try:
    completion = subprocess.run(OSM_QUERY + [f"--request={q}"], check=True, capture_output=True)
    print(f'OSM local query returned with exit code: {completion.returncode}')

    if completion.returncode != 0:
      return False

    print(f'OSM Local query returned:\n\n{completion.stdout}')

    ways = api.parse_xml(completion.stdout).ways
    success = len(ways) == 1
    print(f"Test osm script returned {len(ways)} ways")
    print(f'OSM local server query {"succeeded" if success else "failed"}')

    return success

  except Exception as e:
    print(e)
    return False
