from __future__ import annotations

import threading
import time
from typing import Any

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.common.api.base import BaseApi
from openpilot.sunnypilot.sunnylink.athena.local_app_rows import LocalAppRow, build_local_app_rows
from openpilot.sunnypilot.sunnylink.athena.local_auth import (
  VERSION,
  AuthorizationError,
  LocalAuthority,
  Origin,
  text_field,
)
from openpilot.sunnypilot.sunnylink.athena.local_params import ENROLL as CLOUD_ENROLL_KEY, REVOKE as CLOUD_REVOKE_KEY
from openpilot.sunnypilot.sunnylink.athena.local_state import (
  LOCAL_APPS_KEY,
  LOCAL_APPS_META_KEY,
  REVOKE_ALL,
  REVOKE_KEY,
)

MAX_ALIAS_BYTES = 80

_params = Params()
_authority: LocalAuthority | None = None
_authority_lock = threading.Lock()
_meta_lock = threading.Lock()


def _text(value: Any) -> Any:
  return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def _get(params: Params, key: str) -> Any:
  try:
    return _text(params.get(key))
  except Exception:
    cloudlog.exception(f"sunnylinkd.local_auth.{key}_unreadable")
    return None


def _put(params: Params, key: str, value: Any) -> None:
  try:
    if value is None:
      params.remove(key)
    elif isinstance(value, bool):
      params.put_bool(key, value, block=True)
    else:
      params.put(key, value, block=True)
  except Exception:
    cloudlog.exception(f"sunnylinkd.local_auth.{key}_write_failed")


def _run(name: str, action: Any) -> Any:
  try:
    return action()
  except Exception:
    cloudlog.exception(f"sunnylinkd.local_auth.{name}_failed")
    return None


def _persist_registry(registry: dict[str, Any]) -> None:
  _params.put(LOCAL_APPS_KEY, registry, block=True)


def _read_registry() -> dict[str, Any] | None:
  value = _get(_params, LOCAL_APPS_KEY)
  return value if isinstance(value, dict) else None


def _build_authority() -> LocalAuthority | None:
  try:
    algorithm, private_pem, _ = BaseApi.get_key_pair()
    if algorithm is None or private_pem is None:
      return None
    pem = private_pem if isinstance(private_pem, bytes) else str(private_pem).encode()
    device_key = serialization.load_pem_private_key(pem, password=None)
    cloud_device_id, comma_device_id = (_get(_params, k) for k in ("SunnylinkDongleId", "DongleId"))
    if not isinstance(device_key, (ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey)) or not cloud_device_id or not comma_device_id:
      return None
    return LocalAuthority(cloud_device_id=cloud_device_id, comma_device_id=comma_device_id,
                          device_private_key=device_key, persist=_persist_registry, registry=_read_registry())
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.identity_unavailable")
    return None


def get_authority() -> LocalAuthority | None:
  global _authority
  with _authority_lock:
    if _authority is None:
      _authority = _build_authority()
    return _authority


def reset_authority() -> None:
  global _authority
  with _authority_lock:
    _authority = None


def _meta_write(apps: dict[str, Any]) -> None:
  _params.put(LOCAL_APPS_META_KEY, {"v": VERSION, "apps": apps}, block=True)


def _meta_read() -> dict[str, Any]:
  try:
    raw = _params.get(LOCAL_APPS_META_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_unreadable")
    return {}
  apps = raw.get("apps") if isinstance(raw, dict) else None
  return dict(apps) if isinstance(apps, dict) else {}


def _meta_update(app_key_id: str, **fields: Any) -> None:
  with _meta_lock:
    apps = _meta_read()
    apps[app_key_id] = dict(apps.get(app_key_id) or {}) | fields
    _meta_write(apps)


def read_grant_meta() -> dict[str, dict[str, Any]]:
  return {k: dict(v) for k, v in _meta_read().items() if isinstance(v, dict)}


def set_grant_alias(app_key_id: str, alias: str) -> None:
  cleaned = alias.strip() if isinstance(alias, str) else ""
  if cleaned:
    text_field(cleaned, MAX_ALIAS_BYTES)
  _meta_update(app_key_id, alias=cleaned)


def note_grant_seen(app_key_id: str) -> None:
  _run("meta_seen", lambda: _meta_update(app_key_id, last_seen=time.monotonic()))


def clear_grant_meta(app_key_id: str) -> None:
  try:
    with _meta_lock:
      apps = _meta_read()
      if apps.pop(app_key_id, None) is not None:
        _meta_write(apps)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_clear_failed")


def clear_all_grant_meta() -> None:
  try:
    with _meta_lock:
      if _meta_read():
        _meta_write({})
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_clear_failed")


def _require_authority(kind: str) -> LocalAuthority:
  authority = get_authority()
  if authority is None:
    raise AuthorizationError(f"{kind} unavailable")
  return authority


def cloud_enroll(raw_enrollment: str) -> dict[str, Any]:
  grant = _require_authority("enrollment").enroll(raw_enrollment, Origin.CLOUD)
  return {"app_id": grant.app_id, "app_name": grant.app_name}


def cloud_revoke(raw_revocation: str) -> dict[str, Any]:
  return {"app_id": _require_authority("revocation").revoke_by_self_proof(raw_revocation, Origin.CLOUD)}


def _take(params: Params, key: str) -> str | None:
  try:
    value = params.get(key)
    params.remove(key)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.command_unreadable")
    return None
  value = _text(value)
  return value if isinstance(value, str) and value else None


def claim_cloud_commands(params: Params | None = None) -> None:
  params = params or _params
  for key, apply in ((CLOUD_ENROLL_KEY, cloud_enroll), (CLOUD_REVOKE_KEY, cloud_revoke)):
    value = _take(params, key)
    if value is None:
      continue
    try:
      summary = apply(value)
    except AuthorizationError as e:
      cloudlog.warning(f"sunnylinkd.local_auth.{key}_rejected: {e}")
      continue
    except Exception:
      cloudlog.exception(f"sunnylinkd.local_auth.{key}_failed")
      continue
    cloudlog.event(f"sunnylinkd.local_auth.{key}_accepted", app_name=summary.get("app_name"))


def clear_pending_enrollment() -> None:
  authority = get_authority()
  if authority is not None:
    with authority.lock:
      authority.pending = None


def confirm_enrollment_tls(grant_key_id: str) -> dict[str, Any]:
  authority = _require_authority("enrollment")
  pending = authority.pending
  if pending is None or pending.app_id != grant_key_id:
    raise AuthorizationError("no pending enrollment for this key")
  committed = authority.confirm(pending, grant_key_id)
  return {"app_id": committed.app_id, "app_name": committed.app_name}


def revoke_local_app(app_key_id: str) -> bool:
  authority = get_authority()
  if authority is None:
    return False
  revoked = authority.revoke(app_key_id)
  if revoked:
    clear_grant_meta(app_key_id)
  return revoked


def revoke_all() -> int:
  authority = get_authority()
  if authority is None:
    return 0
  removed = authority.revoke_all()
  if not authority.grants:
    clear_all_grant_meta()
  return removed


def request_revoke(app_key_id: str, params: Params | None = None) -> None:
  if isinstance(app_key_id, str) and app_key_id:
    _put(params or _params, REVOKE_KEY, app_key_id)


def request_revoke_all(params: Params | None = None) -> None:
  _put(params or _params, REVOKE_KEY, REVOKE_ALL)


def service_revoke_requests(params: Params | None = None) -> bool:
  params = params or _params
  app_key_id = _take(params, REVOKE_KEY)
  if not app_key_id:
    return False
  if app_key_id == REVOKE_ALL:
    removed = _run("revoke_all", revoke_all)
    if removed:
      cloudlog.event("sunnylinkd.local_auth.grants_revoked", count=removed)
    return bool(removed)
  revoked = bool(_run("revoke", lambda: revoke_local_app(app_key_id)))
  if revoked:
    cloudlog.event("sunnylinkd.local_auth.grant_revoked", app_id=app_key_id)
  return revoked


def grants() -> list[dict[str, str]]:
  authority = get_authority()
  return [g.to_dict() for g in authority.grants.values()] if authority is not None else []


def read_granted_apps() -> list[dict[str, str]]:
  raw = _read_registry()
  entries = raw.get("grants") if raw is not None else None
  if not isinstance(entries, list):
    return []
  return [{"app_id": e["app_id"], "app_name": e["app_name"]} for e in entries
          if isinstance(e, dict) and isinstance(e.get("app_id"), str) and e["app_id"]
          and isinstance(e.get("app_name"), str)]


def app_rows() -> list[LocalAppRow]:
  return build_local_app_rows(read_granted_apps(), read_grant_meta(), time.monotonic())


def pending_enrollment() -> dict[str, str] | None:
  authority = get_authority()
  pending = authority.pending if authority is not None else None
  return pending.to_dict() if pending is not None else None
