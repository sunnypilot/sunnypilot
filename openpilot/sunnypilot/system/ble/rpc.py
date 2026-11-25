"""
Copyright (c) 2021-, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import json

from openpilot.common.hardware import HARDWARE
from openpilot.common.version import get_version
from openpilot.sunnypilot.sunnylink.athena.params_guard import BLOCKED_PARAMS, is_local_param

METHOD_NOT_FOUND = -32601
INVALID_REQUEST = -32600
REFUSED = -32001
MAX_PARAM_KEYS = 32
HOTSPOT_WAIT = 30.0  # seconds for the hotspot to come up after hotspot.start


class RpcError(Exception):
  def __init__(self, code: int, message: str):
    super().__init__(message)
    self.code = code


def _refused(message: str) -> RpcError:
  return RpcError(REFUSED, message)


def _wifi_status() -> dict:
  # wpa_supplicant answers at once; a fresh WifiManager reports no SSID until its own thread catches up
  try:
    from openpilot.common.hardware.comma.hardware import wpa_supplicant_cmd
    status = wpa_supplicant_cmd("STATUS")
  except (OSError, ImportError):
    return {"wifi_ssid": None, "hotspot": False}
  hotspot = status.get("mode") == "AP"
  connected = status.get("wpa_state") == "COMPLETED" and not hotspot
  return {"wifi_ssid": (status.get("ssid") or None) if connected else None, "hotspot": hotspot}


def _default_wifi():
  from openpilot.system.ui.lib.wifi_manager import WifiManager
  return WifiManager()


class Rpc:
  def __init__(self, params, wifi=None):
    self._params = params
    self._wifi_factory = wifi or _default_wifi
    self._wifi_obj = None
    self._pending: list[tuple[str, int, float]] = []  # hotspot.start waiting for the hotspot

  def handle(self, token: str, body: bytes, grants: list[dict], this: str | None, now: float) -> tuple[dict | None, str | None]:
    # returns (response, after): response None means answered later by poll(); after "forget" drops the link
    try:
      request = json.loads(body)
      rid, method = request["id"], request["method"]
      if not isinstance(rid, int) or not isinstance(method, str):
        raise TypeError("id and method")
    except (ValueError, KeyError, TypeError):
      return _envelope(None, error=(INVALID_REQUEST, "invalid request")), None
    args = request.get("params") or {}
    try:
      return self._dispatch(token, rid, method, args, grants, this, now)
    except RpcError as e:
      return _envelope(rid, error=(e.code, str(e))), None

  def poll(self, now: float) -> list[tuple[str, dict]]:
    done, waiting = [], []
    for token, rid, deadline in self._pending:
      wifi = self._wifi()
      if wifi.is_tethering_active():
        done.append((token, _envelope(rid, result=self._credentials(wifi))))
      elif now >= deadline:
        done.append((token, _envelope(rid, error=(REFUSED, "hotspot did not start"))))
      else:
        waiting.append((token, rid, deadline))
    self._pending = waiting
    return done

  def _dispatch(self, token, rid, method, args, grants, this, now):
    if method == "status.get":
      return _envelope(rid, result=self._status(grants)), None
    if method == "params.get":
      return _envelope(rid, result=self._get(args)), None
    if method == "params.set":
      return _envelope(rid, result=self._set(args)), None
    if method == "hotspot.start":
      wifi = self._wifi()
      if wifi.is_tethering_active():
        return _envelope(rid, result=self._credentials(wifi)), None
      wifi.set_tethering_active(True)
      self._pending.append((token, rid, now + HOTSPOT_WAIT))
      return None, None
    if method == "hotspot.stop":
      self._wifi().set_tethering_active(False)
      return _envelope(rid, result={}), None
    if method == "hotspot.credentials":
      wifi = self._wifi()
      if not wifi.is_tethering_active():
        raise _refused("hotspot is off")
      return _envelope(rid, result=self._credentials(wifi)), None
    if method == "phones.list":
      return _envelope(rid, result=[{"name": g["name"], "added": g["added"], "last_seen": g["last_seen"],
                                     "this": g["spki"] == this} for g in grants]), None
    if method == "phones.forgetSelf":
      return _envelope(rid, result={}), "forget"
    raise RpcError(METHOD_NOT_FOUND, f"unknown method {method}")

  def _wifi(self):
    if self._wifi_obj is None:
      try:
        self._wifi_obj = self._wifi_factory()
      except Exception as e:
        raise _refused("wifi unavailable") from e
    return self._wifi_obj

  def _credentials(self, wifi) -> dict:
    return {"ssid": wifi.tethering_ssid, "password": wifi.tethering_password}

  def _status(self, grants: list[dict]) -> dict:
    return {"version": get_version(), "agnos": HARDWARE.get_os_version(), "dongle_id": self._params.get("DongleId"),
            "onroad": not self._params.get_bool("IsOffroad"), "engaged": self._params.get_bool("IsEngaged"),
            "network": _wifi_status(), "phones": len(grants)}

  def _known(self) -> set[str]:
    return {key.decode() for key in self._params.all_keys()}

  def _check_keys(self, keys: list[str]):
    for key in keys:
      if key in BLOCKED_PARAMS or is_local_param(key):
        raise _refused(f"{key} is not available")

  def _check_known(self, keys: list[str]):
    known = self._known()
    for key in keys:
      if key not in known:
        raise _refused(f"unknown param {key}")

  def _get(self, args: dict) -> dict:
    keys = args.get("keys")
    if not isinstance(keys, list) or len(keys) > MAX_PARAM_KEYS or not all(isinstance(k, str) for k in keys):
      raise _refused("keys must be a list of at most 32 names")
    self._check_keys(keys)
    known = self._known()
    values = {}
    for key in keys:
      value = self._params.get(key) if key in known else None
      values[key] = None if isinstance(value, bytes) else value  # raw bytes have no JSON form
    return {"values": values}

  def _set(self, args: dict) -> dict:
    values = args.get("values")
    if not isinstance(values, dict):
      raise _refused("values must be an object")
    self._check_keys(list(values))
    self._check_known(list(values))
    for key, value in values.items():
      try:
        self._params.put(key, value, block=True)
      except (TypeError, ValueError, KeyError) as e:
        raise _refused(f"bad value for {key}") from e
    return {"ok": list(values)}


def _envelope(rid, result=None, error=None) -> dict:
  if error is not None:
    return {"jsonrpc": "2.0", "id": rid, "error": {"code": error[0], "message": error[1]}}
  return {"jsonrpc": "2.0", "id": rid, "result": result}
