"""Local Sunnydrive pairing shared by sunnydrived and the comma UI."""

import hashlib
import re
import secrets
import time
from datetime import UTC, datetime

from openpilot.common.params import Params


PAIRED_KEY = "SunnydrivePairedClients"
REQUESTS_KEY = "SunnydrivePairingRequests"
PAIRING_SECONDS = 5 * 60
CLIENT_ID_RE = re.compile(r"[A-Za-z0-9_-]{16,128}")


def _params(params=None):
  return params or Params()


def _dict(params, key):
  value = params.get(key)
  return value if isinstance(value, dict) else {}


def device_id(params=None):
  params = _params(params)
  return params.get("DongleId") or params.get("HardwareSerial") or "unregistered"


def device_name(params=None):
  identity = device_id(params)
  return f"comma {identity[-8:]}" if identity != "unregistered" else "comma"


def is_offroad(params=None):
  return _params(params).get_bool("IsOffroad")


def _require_allowed(params):
  if not params.get_bool("SunnydriveAutoPairPrompt"):   # the comma's "allow pairing" switch
    raise PermissionError("pairing is turned off on the comma")


def paired_clients(params=None):
  return _dict(_params(params), PAIRED_KEY)


def is_paired(client_id, params=None):
  return client_id in paired_clients(params)


def authorized(token, params=None):
  if not token:
    return False
  digest = hashlib.sha256(token.encode()).hexdigest()
  return any(secrets.compare_digest(digest, str(client.get("token_hash", ""))) for client in paired_clients(params).values())


def _pair(client_id, name, params):
  if not CLIENT_ID_RE.fullmatch(client_id):
    raise ValueError("invalid client id")
  token = secrets.token_urlsafe(32)
  clients = paired_clients(params)
  clients[client_id] = {"name": str(name or "Sunnydrive phone")[:80], "token_hash": hashlib.sha256(token.encode()).hexdigest(),
                        "paired_at": int(datetime.now(UTC).timestamp())}
  params.put(PAIRED_KEY, clients, block=True)
  return token


def request_pairing(client_id, name, params=None):
  if not CLIENT_ID_RE.fullmatch(client_id):
    raise ValueError("invalid client id")
  params = _params(params)
  _require_allowed(params)
  now = int(time.monotonic())
  requests = {key: value for key, value in _dict(params, REQUESTS_KEY).items()
              if int(value.get("expires", 0)) > now and value.get("client_id") != client_id}
  request_id = secrets.token_urlsafe(18)
  requests[request_id] = {"client_id": client_id, "name": str(name or "Sunnydrive phone")[:80], "status": "pending", "expires": now + PAIRING_SECONDS}
  params.put(REQUESTS_KEY, requests, block=True)
  return request_id


def pairing_requests(params=None):
  params = _params(params)
  now = int(time.monotonic())
  requests = _dict(params, REQUESTS_KEY)
  fresh = {key: value for key, value in requests.items() if int(value.get("expires", 0)) > now}
  if fresh != requests:
    params.put(REQUESTS_KEY, fresh, block=True) if fresh else params.remove(REQUESTS_KEY)
  return fresh


def approve_request(request_id, params=None):
  params = _params(params)
  requests = pairing_requests(params)
  request = requests.get(request_id)
  if not request or request.get("status") != "pending":
    return False
  request["token"] = _pair(request["client_id"], request.get("name"), params)
  request["status"] = "approved"
  requests[request_id] = request
  params.put(REQUESTS_KEY, requests, block=True)
  return True


def consume_request(request_id, params=None):
  params = _params(params)
  requests = pairing_requests(params)
  request = requests.get(request_id)
  if not request:
    return {"status": "expired"}
  result = {"status": request.get("status", "pending")}
  if request.get("status") == "approved":
    result["token"] = request.get("token", "")
    requests.pop(request_id, None)
    params.put(REQUESTS_KEY, requests, block=True) if requests else params.remove(REQUESTS_KEY)
  return result


def unpair(client_id=None, params=None):
  params = _params(params)
  clients = paired_clients(params)
  if client_id is None:
    params.remove(PAIRED_KEY)
    return bool(clients)
  removed = clients.pop(client_id, None) is not None
  if removed:
    params.put(PAIRED_KEY, clients, block=True) if clients else params.remove(PAIRED_KEY)
  return removed
