import requests
from urllib.parse import quote

from openpilot.common.params import Params


class MapboxIntegration:
  def __init__(self):
    self.params = Params()

  def get_public_token(self) -> str:
    token: str = self.params.get('MapboxToken', return_default=True)
    return token

  def set_destination(self, postvars, current_lon, current_lat, bearing=None) -> tuple[dict, bool]:
    if 'latitude' in postvars and 'longitude' in postvars:
      self.nav_confirmed(postvars, current_lon, current_lat, bearing)
      return postvars, True

    addr = postvars['place_name']
    if not addr:
      return postvars, False

    token = self.get_public_token()
    url = f'https://api.mapbox.com/geocoding/v5/mapbox.places/{quote(addr)}.json?access_token={token}&limit=1&proximity={current_lon},{current_lat}'
    try:
      response = requests.get(url, timeout=5)
      if response.status_code == 200:
        features = response.json()['features']
        if features:
          longitude, latitude = features[0]['geometry']['coordinates']
          postvars.update({'latitude': latitude, 'longitude': longitude, 'name': addr})
          self.nav_confirmed(postvars, current_lon, current_lat, bearing)
          return postvars, True
    except requests.RequestException:
      pass  # Broad exception to handle network errors like no internet without crashing navd process.
    return postvars, False

  def nav_confirmed(self, postvars, start_lon, start_lat, bearing=None) -> None:
    if not postvars:
      return

    latitude = float(postvars['latitude'])
    longitude = float(postvars['longitude'])

    data: dict = {'navData': {'current': {'latitude': latitude, 'longitude': longitude}, 'route': {}}}

    token = self.get_public_token()
    route_data = self.generate_route(start_lon, start_lat, longitude, latitude, token, bearing)
    if route_data:
      data['navData']['route'] = route_data
    self.params.put('MapboxSettings', data)

  @staticmethod
  def generate_route(start_lon, start_lat, end_lon, end_lat, token, bearing=None) -> dict | None:
    if not token:
      return None

    params = {
      'access_token': token,
      'geometries': 'geojson',
      'steps': 'true',
      'overview': 'full',
      'annotations': 'maxspeed',
      'alternatives': 'false',
      'banner_instructions': 'true',
    }
    if bearing is not None:
      params['bearings'] = f'{int((bearing + 360) % 360):.0f},90;'

    try:
      response = requests.get(f'https://api.mapbox.com/directions/v5/mapbox/driving/{start_lon},{start_lat};{end_lon},{end_lat}', params=params, timeout=5)
      data = response.json() if response.status_code == 200 else {}
    except requests.RequestException:
      return None

    routes = data['routes'] if data else None
    legs = routes[0]['legs'] if routes else None

    if data.get('code') != 'Ok' or not routes or not legs:
      return None

    route = routes[0]
    leg = legs[0]

    steps = [
      {
        'maneuver': step['maneuver']['type'],
        'instruction': step['maneuver']['instruction'],
        'distance': step['distance'],
        'duration': step['duration'],
        'location': {'longitude': step['maneuver']['location'][0], 'latitude': step['maneuver']['location'][1]},
        'modifier': step['maneuver'].get('modifier', 'none'),
        'bannerInstructions': step['bannerInstructions'],
      }
      for step in leg['steps']
    ]

    maxspeed = [{'speed': item['speed'], 'unit': item['unit']} for item in leg['annotation']['maxspeed'] if 'speed' in item]

    return {
      'steps': steps,
      'totalDistance': route['distance'],
      'totalDuration': route['duration'],
      'geometry': [{'longitude': coord[0], 'latitude': coord[1]} for coord in route['geometry']['coordinates']],
      'maxspeed': maxspeed,
    }
