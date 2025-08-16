import requests
import time
import logging

LOG = logging.getLogger(__name__)

class WazeAPI:
  BASE_URL = "https://waze.p.rapidapi.com"
  CACHE_DURATION = 60

  def __init__(self, api_key):
    self.headers = {
      "X-RapidAPI-Key": api_key,
      "X-RapidAPI-Host": "waze.p.rapidapi.com"
    }
    self._cache = None
    self._cache_time = 0

  def get_traffic_alerts(self, lat, lon, radius=1000):
    now = time.time()
    if self._cache and (now - self._cache_time) < self.CACHE_DURATION:
      return self._cache

    url = f"{self.BASE_URL}/alerts"
    params = {
      "lat": lat,
      "lon": lon,
      "radius": radius
    }

    try:
      response = requests.get(url, headers=self.headers, params=params, timeout=5)
      response.raise_for_status()
      data = response.json()
      self._cache = data
      self._cache_time = now
      return data
    except Exception as e:
      LOG.warning(f"WazeAPI get_traffic_alerts failed: {e}")
      return None
