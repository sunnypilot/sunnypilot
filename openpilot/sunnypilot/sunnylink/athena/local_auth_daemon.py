"""The local daemon's store: the enrolled phones, their display metadata and the Params the
device UI uses to ask for a pairing window or a revocation.

Only `localsunnylinkd` holds the authority; the settings UI (another process) reads a view and
sends requests, so it can never persist a grant list of its own.
"""
from __future__ import annotations

import threading
import time
from typing import Any

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.common.api.base import BaseApi
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
  PAIRING_QR_KEY,
  PAIRING_REQUEST_KEY,
  REVOKE_ALL_KEY,
  REVOKE_KEY,
)

MAX_ALIAS_BYTES = 80

_params = Params()
_authority: LocalAuthority | None = None
_authority_lock = threading.Lock()
_meta_lock = threading.Lock()


def _persist_registry(registry: dict[str, Any]) -> None:
  """Durable write before callers publish the change in memory (fail-closed ordering)."""
  _params.put(LOCAL_APPS_KEY, registry, block=True)


def _read_registry() -> dict[str, Any] | None:
  raw = _params.get(LOCAL_APPS_KEY)
  return raw if isinstance(raw, dict) else None


def _build_authority() -> LocalAuthority | None:
  try:
    algorithm, private_pem, _public_pem = BaseApi.get_key_pair()
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.identity_unavailable")
    return None
  if algorithm is None or private_pem is None:
    return None

  try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, rsa

    pem = private_pem if isinstance(private_pem, bytes) else str(private_pem).encode()
    device_key = serialization.load_pem_private_key(pem, password=None)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.identity_load_failed")
    return None
  if not isinstance(device_key, (ec.EllipticCurvePrivateKey, rsa.RSAPrivateKey)):
    cloudlog.error("sunnylinkd.local_auth.identity_unsupported")
    return None

  cloud_device_id = _params.get("SunnylinkDongleId")
  comma_device_id = _params.get("DongleId")
  if not cloud_device_id or not comma_device_id:
    return None

  return LocalAuthority(
    cloud_device_id=cloud_device_id.decode() if isinstance(cloud_device_id, bytes) else cloud_device_id,
    comma_device_id=comma_device_id.decode() if isinstance(comma_device_id, bytes) else comma_device_id,
    device_private_key=device_key,
    persist=_persist_registry,
    registry=_read_registry(),
  )


def get_authority() -> LocalAuthority | None:
  """The process authority, or None when local trust is unavailable (fail closed).

  Every failure reports None instead of raising: the daemon calls this from its serving loop.
  """
  global _authority
  with _authority_lock:
    if _authority is not None:
      return _authority
    try:
      _authority = _build_authority()
    except Exception:
      cloudlog.exception("sunnylinkd.local_auth.authority_unavailable")
      return None
    return _authority


def reset_authority() -> None:
  global _authority
  with _authority_lock:
    _authority = None


def arm_local_pairing() -> str | None:
  authority = get_authority()
  if authority is None:
    return None
  try:
    return authority.arm()
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.arm_failed")
    return None


def cancel_local_pairing() -> None:
  authority = get_authority()
  if authority is not None:
    authority.cancel()


def _publish_qr(qr: str | None, params: Params) -> None:
  try:
    if qr:
      params.put(PAIRING_QR_KEY, qr, block=True)
    else:
      params.remove(PAIRING_QR_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.qr_publish_failed")


def _clear_request(params: Params) -> None:
  try:
    params.remove(PAIRING_REQUEST_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.pairing_request_clear_failed")


def _armed_qr(authority: LocalAuthority) -> str | None:
  with authority.lock:
    window = authority.window
    if window is None or authority.clock() >= window.deadline:
      return None
    return window.qr


def read_pairing_qr(params: Params | None = None) -> str | None:
  """The QR currently published for the UI, which is also the window's visible state."""
  params = params or _params
  try:
    value = params.get(PAIRING_QR_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.qr_read_failed")
    return None
  if isinstance(value, bytes):
    value = value.decode("utf-8", errors="replace")
  return value if isinstance(value, str) and value else None


def _read_meta() -> dict[str, Any]:
  try:
    raw = _params.get(LOCAL_APPS_META_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_unreadable")
    return {}
  apps = raw.get("apps") if isinstance(raw, dict) else None
  return dict(apps) if isinstance(apps, dict) else {}


def _write_meta(apps: dict[str, Any]) -> None:
  _params.put(LOCAL_APPS_META_KEY, {"v": VERSION, "apps": apps}, block=True)


def read_grant_meta() -> dict[str, dict[str, Any]]:
  """Per-phone display metadata: `{key_id: {"alias": str, "last_seen": float}}`, fail-soft."""
  try:
    entries = _read_meta()
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_unreadable")
    return {}
  return {key_id: dict(entry) for key_id, entry in entries.items() if isinstance(entry, dict)}


def set_grant_alias(app_key_id: str, alias: str) -> bool:
  """Record the name a phone calls itself. Metadata only: nothing here grants anything."""
  cleaned = (alias or "").strip() if isinstance(alias, str) else ""
  if cleaned:
    text_field(cleaned, MAX_ALIAS_BYTES)
  with _meta_lock:
    apps = _read_meta()
    entry = dict(apps.get(app_key_id) or {})
    entry["alias"] = cleaned
    apps[app_key_id] = entry
    _write_meta(apps)
  return True


def note_grant_seen(app_key_id: str) -> None:
  """Stamp "this phone just connected"; a metadata failure never costs a working session."""
  try:
    with _meta_lock:
      apps = _read_meta()
      entry = dict(apps.get(app_key_id) or {})
      entry["last_seen"] = time.monotonic()
      apps[app_key_id] = entry
      _write_meta(apps)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_seen_failed")


def clear_grant_meta(app_key_id: str) -> None:
  try:
    with _meta_lock:
      apps = _read_meta()
      if apps.pop(app_key_id, None) is not None:
        _write_meta(apps)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_clear_failed")


def clear_all_grant_meta() -> None:
  try:
    with _meta_lock:
      if _read_meta():
        _write_meta({})
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.meta_clear_failed")


def clear_pairing_params(params: Params | None = None) -> None:
  """The UI's cancel signal: the daemon cancels the window it owns on its next tick."""
  params = params or _params
  _clear_request(params)
  _publish_qr(None, params)


def clear_pairing_window(params: Params | None = None) -> None:
  """The daemon's own teardown: cancel the window this process holds and clear both params."""
  clear_pairing_params(params)
  cancel_local_pairing()


def service_pairing_window(params: Params | None = None) -> str | None:
  """Arm, publish or close the pairing window from the UI's request flag. Never raises."""
  params = params or _params
  try:
    return _service_pairing_window(params)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.pairing_window_failed")
    return read_pairing_qr(params)


def _service_pairing_window(params: Params) -> str | None:
  try:
    requested = bool(params.get_bool(PAIRING_REQUEST_KEY))
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.pairing_request_unreadable")
    requested = False

  authority = get_authority()
  if authority is None:
    # No identity key means nothing could ever enroll: never show a window that cannot complete.
    _clear_request(params)
    _publish_qr(None, params)
    return None

  armed = _armed_qr(authority)
  published = read_pairing_qr(params)

  if armed is not None:
    if published is None:
      # A live window the UI no longer shows is a window the user cancelled.
      cancel_local_pairing()
      cloudlog.event("sunnylinkd.local_auth.window_cancelled")
      return None
    if published != armed:
      # Only a stale QR is replaced: an armed, displayed window is never rotated, the app may
      # already have scanned it.
      _publish_qr(armed, params)
    return armed

  if authority.window is not None:
    # The code's displayed lifetime is over. Hide it — the UI closes its dialog on the cleared
    # param — but keep the session: an enrollment for the code the user just scanned can still be
    # in flight through the cloud, which delivers on a later tick. Ending the session here is what
    # made a scanned code fail with nothing shown on either side (the phone waited forever, the
    # device said nothing). A cancel is different: it clears every session the user could have
    # scanned from.
    authority.expire()
    cloudlog.event("sunnylinkd.local_auth.window_expired")

  authority.prune_sessions()

  if not requested:
    if published is not None:
      _publish_qr(None, params)
    return None

  qr = arm_local_pairing()
  _clear_request(params)
  _publish_qr(qr, params)
  if qr is None:
    return None
  cloudlog.event("sunnylinkd.local_auth.window_armed")
  return qr


def cloud_enroll(raw_enrollment: str) -> dict[str, Any]:
  """Stage an enrollment that arrived through the cloud settings-write transport.

  Only ever called with a payload the cloud delivered; raises AuthorizationError for anything
  that does not validate. Nothing is durable until the pinned TLS peer proves the key.
  """
  authority = get_authority()
  if authority is None:
    raise AuthorizationError("enrollment unavailable")
  grant = authority.enroll(raw_enrollment, Origin.CLOUD)
  return {"app_id": grant.app_id, "app_name": grant.app_name, "revision": grant.revision}


def cloud_revoke(raw_revocation: str) -> dict[str, Any]:
  """Apply a phone's signed self-revocation of its own grant, same provenance as enrollment."""
  authority = get_authority()
  if authority is None:
    raise AuthorizationError("revocation unavailable")
  return {"app_id": authority.revoke_by_self_proof(raw_revocation, Origin.CLOUD)}


def claim_cloud_commands(params: Params | None = None) -> None:
  """Apply the two commands the cloud may deliver to the local daemon, then always clear them.

  The cloud daemon only stores them (`local_params.CLOUD_COMMANDS`); the payload is validated and
  staged here. A rejected payload is still cleared, so a bad command cannot be retried or replayed.
  """
  params = params or _params
  for key, apply in ((CLOUD_ENROLL_KEY, cloud_enroll), (CLOUD_REVOKE_KEY, cloud_revoke)):
    value = _take(params, key)
    if value is None:
      continue
    try:
      summary = apply(value)
    except AuthorizationError as e:
      cloudlog.warning(f"sunnylinkd.local_auth.{key}_rejected: {e}")
    except Exception:
      cloudlog.exception(f"sunnylinkd.local_auth.{key}_failed")
    else:
      # An enrollment is staged here and only becomes durable when the phone's pinned TLS dial
      # proves its key, but the event still records that the command landed. Without it a
      # successful arrival is invisible and a rejected one looks like nothing happened at all.
      app_name = summary.get("app_name") if isinstance(summary, dict) else None
      cloudlog.event(f"sunnylinkd.local_auth.{key}_accepted", app_name=app_name)


def _take(params: Params, key: str) -> str | None:
  try:
    value = params.get(key)
    params.remove(key)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.command_unreadable")
    return None
  if isinstance(value, bytes):
    value = value.decode("utf-8", errors="replace")
  return value if isinstance(value, str) and value else None


def confirm_enrollment_tls(grant_key_id: str) -> dict[str, Any]:
  """Commit the pending grant once the pinned TLS peer proved possession of its key."""
  authority = get_authority()
  if authority is None:
    raise AuthorizationError("enrollment unavailable")
  pending = authority.pending
  if pending is None or pending.key_id != grant_key_id:
    raise AuthorizationError("no pending enrollment for this key")
  committed = authority.confirm(pending, grant_key_id)
  return {"app_id": committed.app_id, "app_name": committed.app_name, "revision": committed.revision}


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
  """The UI asks the daemon to drop one phone; the daemon applies it through its live authority."""
  params = params or _params
  if not isinstance(app_key_id, str) or not app_key_id:
    return
  try:
    params.put(REVOKE_KEY, app_key_id, block=True)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.revoke_request_failed")


def request_revoke_all(params: Params | None = None) -> None:
  params = params or _params
  try:
    params.put_bool(REVOKE_ALL_KEY, True, block=True)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.revoke_all_request_failed")


def service_revoke_requests(params: Params | None = None) -> bool:
  """Apply (and always clear) a pending UI revoke request, so one bad request cannot stick."""
  params = params or _params

  revoke_all_requested = False
  try:
    revoke_all_requested = bool(params.get_bool(REVOKE_ALL_KEY))
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.revoke_all_unreadable")

  if revoke_all_requested:
    removed = 0
    try:
      removed = revoke_all()
    except Exception:
      cloudlog.exception("sunnylinkd.local_auth.revoke_all_failed")
    finally:
      try:
        params.remove(REVOKE_ALL_KEY)
        params.remove(REVOKE_KEY)  # every grant is gone, so a single request has nothing left
      except Exception:
        cloudlog.exception("sunnylinkd.local_auth.revoke_all_clear_failed")
    if removed:
      cloudlog.event("sunnylinkd.local_auth.grants_revoked", count=removed)
    return bool(removed)

  try:
    requested = params.get(REVOKE_KEY)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.revoke_request_unreadable")
    return False
  if isinstance(requested, bytes):
    requested = requested.decode("utf-8", errors="replace")
  app_key_id = requested if isinstance(requested, str) else ""
  if not app_key_id:
    return False

  revoked = False
  try:
    revoked = revoke_local_app(app_key_id)
  except Exception:
    cloudlog.exception("sunnylinkd.local_auth.revoke_failed")
  finally:
    try:
      params.remove(REVOKE_KEY)
    except Exception:
      cloudlog.exception("sunnylinkd.local_auth.revoke_clear_failed")
  if revoked:
    cloudlog.event("sunnylinkd.local_auth.grant_revoked", app_id=app_key_id)
  return revoked


def grants() -> list[dict[str, str]]:
  authority = get_authority()
  if authority is None:
    return []
  return [grant.to_dict() for grant in authority.grants.values()]


def read_granted_apps() -> list[dict[str, str]]:
  """Read-only view of the enrolled phones for the device UI, fresh from Params.

  Deliberately does not build the authority: the settings UI is another process.
  """
  raw = _read_registry()
  entries = raw.get("grants") if isinstance(raw, dict) else None
  if not isinstance(entries, list):
    return []
  rows = []
  for entry in entries:
    if not isinstance(entry, dict):
      continue
    app_id = entry.get("app_id")
    app_name = entry.get("app_name")
    if isinstance(app_id, str) and app_id and isinstance(app_name, str):
      rows.append({"app_id": app_id, "app_name": app_name})
  return rows


def pending_enrollment() -> dict[str, str] | None:
  authority = get_authority()
  if authority is None:
    return None
  pending = authority.pending
  return pending.to_dict() if pending is not None else None
