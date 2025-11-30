"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import time


class ParamWatcher:
  def __init__(self, params):
    self.params = params
    self.cache = {}
    self.last_update = 0

  def _update_cache(self):
    for key in list(self.cache.keys()):
      self.cache[key] = self.params.get(key)
    self.last_update = time.monotonic()

  def get(self, key, default=None):
    if time.monotonic() - self.last_update > 0.2:
      self._update_cache()
    if key in self.cache:
      return self.cache[key]
    else:
      val = self.params.get(key, default)
      self.cache[key] = val
      return val

  def get_bool(self, key):
    value = self.get(key)
    return value is not None and value
