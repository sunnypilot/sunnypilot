import overpy
import subprocess
import numpy as np
from cereal import log
from common.params import Params
from selfdrive.mapd.lib.geo import R
from selfdrive.mapd.lib.helpers import is_local_osm_installed, OSM_QUERY

DataType = log.LiveMapData.DataType


def create_way(way_id, node_ids, from_way):
  """
  Creates and OSM Way with the given `way_id` and list of `node_ids`, copying attributes and tags from `from_way`
  """
  return overpy.Way(way_id, node_ids=node_ids, attributes={}, result=from_way._result,
                    tags=from_way.tags)


class OSM:
  def __init__(self):
    self.api = overpy.Overpass()
    self.param_s = Params()
    self._osm_local_db_enabled = self.param_s.get_bool("OsmLocalDb")
    self._local_osm_installed = is_local_osm_installed(self.param_s)
    # self.api = overpy.Overpass(url='http://3.65.170.21/api/interpreter')

  def _online_query(self, q, area_q):
    print("Query OSM from remote server")
    query = self.api.query(q + area_q)
    areas, ways = query.areas, query.ways
    data_type = DataType.online
    return areas, ways, data_type

  def fetch_road_ways_around_location(self, lat, lon, radius):
    # Calculate the bounding box coordinates for the bbox containing the circle around location.
    bbox_angle = np.degrees(radius / R)
    # fetch all ways and nodes on this ways in bbox
    bbox_str = f'{str(lat - bbox_angle)},{str(lon - bbox_angle)},{str(lat + bbox_angle)},{str(lon + bbox_angle)}'
    lat_lon = "(%f,%f)" % (lat, lon)
    q = """
        way(""" + bbox_str + """)
          [highway]
          [highway!~"^(footway|path|corridor|bridleway|steps|cycleway|construction|bus_guideway|escape|service|track)$"];
        (._;>;);
        out;"""
    area_q = """is_in""" + lat_lon + """;area._[admin_level~"[24]"];
        convert area ::id = id(), admin_level = t['admin_level'],
        name = t['name'], "ISO3166-1:alpha2" = t['ISO3166-1:alpha2'];out;
        """
    try:
      if self._osm_local_db_enabled and self._local_osm_installed:
        print("Query OSM from local server")
        completion = subprocess.run(OSM_QUERY + [f"--request={q}"], check=True, capture_output=True)
        ways = self.api.parse_xml(completion.stdout).ways
        if completion.returncode == 0 and len(ways) != 0:
          try:
            areas = self.api.query(area_q).areas
          except Exception as e:
            print(f'Exception while querying "AREAS" OSM from local server:\n{e}')
            areas = None
          data_type = DataType.offline
        else:
          areas, ways, data_type = self._online_query(q, area_q)
      else:
        areas, ways, data_type = self._online_query(q, area_q)
    except Exception as e:
      print(f'Exception while querying OSM:\n{e}')
      areas, ways, data_type = [], [], DataType.default

    return areas, ways, data_type
