import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, cast
from unittest import mock

from openpilot.common.params import Params

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.athena import local_auth_daemon
from openpilot.sunnypilot.sunnylink.athena.local_auth import (
  AuthorizationError,
  Grant,
  LocalAuthority,
  Origin,
  encode64,
  key_id,
  statement,
)

# `<repo>/openpilot/common/params_keys.h` from this file.
PARAMS_KEYS_H = Path(__file__).resolve().parents[4] / "common" / "params_keys.h"

# The fields an enrollment signs, in the order the statement joins them.
ENROLL_FIELDS = ("cloud_device_id", "comma_device_id", "device_key_id",
                 "pairing_session", "public_key", "key_id", "app_name")


class _ParamsStore:
  """Dict-backed stand-in for the Params surface this module uses.

  It deliberately models a JSON-typed param the way libparams does: a dict put in comes back
  out as the same dict. That contract is exactly what `_persist_registry` and `_read_registry`
  have to agree on, so a mismatched pair (a second base64 decode, say) fails here instead of
  only on a device.
  """

  def __init__(self, initial: dict[str, Any] | None = None):
    self.values: dict[str, Any] = dict(initial or {})
    self.removed: list[str] = []
    self.fail_reads = False

  def get(self, key: str, block: bool = False, return_default: bool = False) -> Any:
    if self.fail_reads:
      raise RuntimeError("params unavailable")
    return self.values.get(key)

  def get_bool(self, key: str, block: bool = False) -> bool:
    if self.fail_reads:
      raise RuntimeError("params unavailable")
    return bool(self.values.get(key))

  def put(self, key: str, value: Any, block: bool = False) -> None:
    self.values[key] = value

  def put_bool(self, key: str, value: bool, block: bool = False) -> None:
    self.values[key] = bool(value)

  def remove(self, key: str) -> None:
    self.values.pop(key, None)
    self.removed.append(key)


class TestLocalAuthDaemon(OpenpilotTestCase):
  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.private_pem = self.device_key.private_bytes(
      serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    self.store = _ParamsStore({"SunnylinkDongleId": "cloud-device", "DongleId": "comma-device"})

    local_auth_daemon.reset_authority()
    self.addCleanup(local_auth_daemon.reset_authority)
    patchers = [
      mock.patch.object(local_auth_daemon, "_params", self.store),
      mock.patch.object(local_auth_daemon.BaseApi, "get_key_pair", return_value=("ES256", self.private_pem, "pub")),
    ]
    for patcher in patchers:
      patcher.start()
      self.addCleanup(patcher.stop)

  def enrollment(self, authority) -> str:
    authority.arm()
    public = encode64(self.app_key.public_key().public_bytes(
      serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo))
    nonce = authority.window.nonce
    data = {"v": 2, "cloud_device_id": authority.cloud_device_id, "comma_device_id": authority.comma_device_id,
            "device_key_id": authority.device_key_id, "pairing_session": nonce,
            "public_key": public, "key_id": key_id(self.app_key.public_key()), "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
    return json.dumps(data)

  def enrolled(self) -> dict[str, str]:
    """Enroll one phone end to end: cloud enrollment staged, then TLS-confirmed."""
    summary = local_auth_daemon.cloud_enroll(self.enrollment(local_auth_daemon.get_authority()))
    return local_auth_daemon.confirm_enrollment_tls(summary["app_id"])

  def revocation(self, authority, app_key=None) -> str:
    """What the app pushes when it unpairs: a self-signed request to drop its own grant."""
    key = app_key or self.app_key
    app_id = key_id(key.public_key())
    proof = statement("revoke", authority.cloud_device_id, authority.comma_device_id, app_id)
    return json.dumps({"v": 2, "cloud_device_id": authority.cloud_device_id,
                       "comma_device_id": authority.comma_device_id, "key_id": app_id,
                       "signature": encode64(key.sign(proof, ec.ECDSA(hashes.SHA256())))})

  def registry(self) -> dict[str, Any]:
    return self.store.values[local_auth_daemon.LOCAL_APPS_KEY]

  def test_a_late_cloud_enrollment_from_an_expired_code_still_enrolls(self):
    """The path an app's push actually takes: the gateway stored the settings-write, the local
    half claims it on a later tick, and by then the scanned code has left the device screen. This
    is what used to be dropped with only a log line, leaving the app waiting forever."""
    authority = local_auth_daemon.get_authority()
    raw = self.enrollment(authority)          # the app scanned the armed code
    authority.expire()                        # the code stops being displayed …
    self.store.put(local_auth_daemon.CLOUD_ENROLL_KEY, raw)

    local_auth_daemon.claim_cloud_commands(cast(Params, self.store))

    pending = local_auth_daemon.pending_enrollment()
    assert pending is not None, "the late enrollment was not staged"
    self.assertEqual(key_id(self.app_key.public_key()), pending["key_id"])
    self.assertEqual("Test phone", pending["app_name"])
    # Claimed exactly once, whether or not it validated.
    self.assertIsNone(self.store.get(local_auth_daemon.CLOUD_ENROLL_KEY))

  def test_a_cloud_enrollment_for_a_code_past_its_grace_is_refused(self):
    authority = local_auth_daemon.get_authority()
    raw = self.enrollment(authority)
    window = authority.recent[-1]
    authority.expire()
    self.store.put(local_auth_daemon.CLOUD_ENROLL_KEY, raw)

    with mock.patch.object(authority, "clock", lambda: window.usable_until + 1):
      local_auth_daemon.claim_cloud_commands(cast(Params, self.store))

    self.assertIsNone(local_auth_daemon.pending_enrollment())
    self.assertIsNone(self.store.get(local_auth_daemon.CLOUD_ENROLL_KEY))

  def test_cloud_enroll_stages_and_tls_confirm_persists(self):
    summary = local_auth_daemon.cloud_enroll(self.enrollment(local_auth_daemon.get_authority()))
    # Staged: nothing durable until the TLS peer proves possession.
    self.assertNotIn(local_auth_daemon.LOCAL_APPS_KEY, self.store.values)
    committed = local_auth_daemon.confirm_enrollment_tls(summary["app_id"])
    self.assertEqual(summary["app_id"], committed["app_id"])
    registry = self.registry()
    self.assertEqual(2, registry["v"])
    self.assertEqual(1, len(registry["grants"]))
    self.assertEqual(summary["app_id"], registry["grants"][0]["app_id"])

  def test_grants_reload_from_the_persisted_registry(self):
    """The write and read halves must agree: a grant has to survive a daemon restart."""
    summary = self.enrolled()

    local_auth_daemon.reset_authority()
    grants = local_auth_daemon.grants()

    self.assertEqual(1, len(grants))
    self.assertEqual(summary["app_id"], grants[0]["app_id"])
    self.assertEqual("Test phone", grants[0]["app_name"])

  def test_registry_round_trip_is_the_json_param_itself(self):
    self.enrolled()
    registry = self.registry()
    # Stored as the JSON param, not the base64 cloud-transport form: reading it back through the
    # same module must return the identical structure.
    self.assertIsInstance(registry, dict)
    self.assertEqual({"v", "grants"}, set(registry))
    self.assertIs(local_auth_daemon._read_registry(), registry)

  def test_revocation_persists_removal(self):
    summary = self.enrolled()
    self.assertTrue(local_auth_daemon.revoke_local_app(summary["app_id"]))
    self.assertEqual([], self.registry()["grants"])
    self.assertFalse(local_auth_daemon.revoke_local_app("unknown"))

  def test_cloud_revoke_drops_the_phones_own_grant(self):
    """Unpairing from an app that is not on the LAN: no live session carries `unpairLocalApp`,
    so without this the device would keep authorizing that phone forever."""
    summary = self.enrolled()

    result = local_auth_daemon.cloud_revoke(self.revocation(local_auth_daemon.get_authority()))

    self.assertEqual(summary["app_id"], result["app_id"])
    self.assertEqual([], self.registry()["grants"])
    # Persisted: a restart must not resurrect the grant.
    local_auth_daemon.reset_authority()
    self.assertEqual([], local_auth_daemon.grants())

  def test_a_forged_proof_for_an_enrolled_key_is_refused(self):
    self.enrolled()
    authority = local_auth_daemon.get_authority()
    forged = json.loads(self.revocation(authority))
    forged["signature"] = encode64(ec.generate_private_key(ec.SECP256R1()).sign(
      statement("revoke", authority.cloud_device_id, authority.comma_device_id, forged["key_id"]),
      ec.ECDSA(hashes.SHA256())))
    with self.assertRaises(AuthorizationError):
      local_auth_daemon.cloud_revoke(json.dumps(forged))
    self.assertEqual(1, len(self.registry()["grants"]))

  def test_a_proof_from_another_key_cannot_remove_a_grant(self):
    self.enrolled()
    other = ec.generate_private_key(ec.SECP256R1())
    # A key that is not enrolled has no grant to drop, so this is a no-op — never a way to
    # remove someone else's phone.
    result = local_auth_daemon.cloud_revoke(
      self.revocation(local_auth_daemon.get_authority(), app_key=other))
    self.assertEqual(key_id(other.public_key()), result["app_id"])
    self.assertEqual(1, len(self.registry()["grants"]))

  def test_cloud_revoke_requires_the_right_device(self):
    self.enrolled()
    payload = json.loads(self.revocation(local_auth_daemon.get_authority()))
    payload["comma_device_id"] = "some-other-car"
    with self.assertRaises(AuthorizationError):
      local_auth_daemon.cloud_revoke(json.dumps(payload))
    self.assertEqual(1, len(self.registry()["grants"]))

  def test_the_revoke_adapter_requires_cloud_origin(self):
    """Same provenance rule as enrollment: an ordinary local RPC must never be able to reach it."""
    self.enrolled()
    authority = local_auth_daemon.get_authority()
    with self.assertRaises(AuthorizationError):
      authority.revoke_by_self_proof(self.revocation(authority), Origin.LOCAL)
    self.assertEqual(1, len(self.registry()["grants"]))

  def test_registry_key_is_declared_in_params_keys(self):
    """Every param this adapter stores must be registered, or Params raises UnknownKeyName.

    That failure is not cosmetic: get_authority() is on the daemon's connection path, so an
    undeclared key used to take sunnylinkd (and the cloud link with it) down.
    """
    declared = PARAMS_KEYS_H.read_text()
    for key in (local_auth_daemon.LOCAL_APPS_KEY, local_auth_daemon.LOCAL_APPS_META_KEY,
                local_auth_daemon.PAIRING_REQUEST_KEY, local_auth_daemon.PAIRING_QR_KEY,
                local_auth_daemon.REVOKE_KEY, local_auth_daemon.REVOKE_ALL_KEY):
      self.assertTrue(f'"{key}"' in declared)

  def test_read_registry_ignores_a_value_that_is_not_the_registry(self):
    self.store.values[local_auth_daemon.LOCAL_APPS_KEY] = "not a registry"
    self.assertIsNone(local_auth_daemon._read_registry())
    self.assertEqual([], local_auth_daemon.grants())

  def test_authority_fault_fails_closed_without_raising(self):
    """A broken trust store must never propagate out of get_authority(): sunnylinkd calls it
    from its connection loop, where an exception ends the process."""
    self.store.fail_reads = True
    self.assertIsNone(local_auth_daemon.get_authority())
    self.assertEqual([], local_auth_daemon.grants())
    self.assertFalse(local_auth_daemon.revoke_local_app("anything"))
    with self.assertRaises(AuthorizationError):
      local_auth_daemon.cloud_enroll("{}")

  def test_no_identity_key_fails_closed(self):
    with mock.patch.object(local_auth_daemon.BaseApi, "get_key_pair", return_value=(None, None, None)):
      local_auth_daemon.reset_authority()
      self.assertIsNone(local_auth_daemon.get_authority())
      self.assertIsNone(local_auth_daemon.arm_local_pairing())
      with self.assertRaises(AuthorizationError):
        local_auth_daemon.cloud_enroll("{}")


class TestRegistryThroughRealParams(OpenpilotTestCase):
  """The same round trip against the real Params/libparams, in a temporary params directory.

  The double above pins the logic; this proves the actual C library stores and returns the
  registry the way the module expects (JSON-typed param: a dict in, the same dict out), which is
  where the persistence bug lived. It needs `libparams_c` built from a `params_keys.h` that
  declares `SunnylinkLocalApps`.
  """

  def setup_method(self):
    self.dir = tempfile.mkdtemp(prefix="sunnylink_params_")
    self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.private_pem = self.device_key.private_bytes(
      serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    self.params = Params(self.dir)
    self.params.put("SunnylinkDongleId", "cloud-device", block=True)
    self.params.put("DongleId", "comma-device", block=True)

    local_auth_daemon.reset_authority()
    self.addCleanup(local_auth_daemon.reset_authority)
    patchers = [
      mock.patch.object(local_auth_daemon, "_params", self.params),
      mock.patch.object(local_auth_daemon.BaseApi, "get_key_pair", return_value=("ES256", self.private_pem, "pub")),
    ]
    for patcher in patchers:
      patcher.start()
      self.addCleanup(patcher.stop)

  def test_grant_survives_a_write_and_reload_through_libparams(self):
    authority = local_auth_daemon.get_authority()
    self.assertIsNotNone(authority)
    authority.arm()
    nonce = authority.window.nonce
    public = encode64(self.app_key.public_key().public_bytes(
      serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo))
    app_id = key_id(self.app_key.public_key())
    data = {"v": 2, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
            "device_key_id": authority.device_key_id, "pairing_session": nonce, "public_key": public,
            "key_id": app_id, "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))

    summary = local_auth_daemon.cloud_enroll(json.dumps(data))
    local_auth_daemon.confirm_enrollment_tls(summary["app_id"])

    # A daemon restart is what used to lose every grant.
    local_auth_daemon.reset_authority()
    grants = local_auth_daemon.grants()
    self.assertEqual(1, len(grants))
    self.assertEqual(summary["app_id"], grants[0]["app_id"])
    self.assertEqual("Test phone", grants[0]["app_name"])
    self.assertEqual([{"app_id": summary["app_id"], "app_name": "Test phone"}],
                     local_auth_daemon.read_granted_apps())

    # And a revocation persists through the same store.
    self.assertTrue(local_auth_daemon.revoke_local_app(summary["app_id"]))
    local_auth_daemon.reset_authority()
    self.assertEqual([], local_auth_daemon.grants())
    self.assertEqual([], local_auth_daemon.read_granted_apps())


class TestGrantMetadata(OpenpilotTestCase):
  """Display metadata for enrolled phones: cosmetic, and never a source of authority."""

  def setup_method(self):
    self.store = _ParamsStore()
    patcher = mock.patch.object(local_auth_daemon, "_params", self.store)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_alias_and_last_seen_round_trip(self):
    local_auth_daemon.set_grant_alias("key-a", "Nayan's phone")
    local_auth_daemon.note_grant_seen("key-a")

    meta = local_auth_daemon.read_grant_meta()
    self.assertEqual("Nayan's phone", meta["key-a"]["alias"])
    self.assertIsInstance(meta["key-a"]["last_seen"], float)

  def test_a_blank_alias_clears_back_to_the_enrolled_name(self):
    local_auth_daemon.set_grant_alias("key-a", "Named")
    local_auth_daemon.set_grant_alias("key-a", "   ")
    self.assertEqual("", local_auth_daemon.read_grant_meta()["key-a"]["alias"])

  def test_an_oversized_alias_is_refused(self):
    with self.assertRaises(AuthorizationError):
      local_auth_daemon.set_grant_alias("key-a", "x" * 81)
    self.assertEqual({}, local_auth_daemon.read_grant_meta())

  def test_metadata_never_grants_anything(self):
    # A metadata entry for a key with no grant is inert: the authority is the only judge.
    local_auth_daemon.set_grant_alias("un-enrolled-key", "attacker")
    self.assertEqual([], local_auth_daemon.grants())
    self.assertEqual({"un-enrolled-key": {"alias": "attacker"}}, local_auth_daemon.read_grant_meta())

  def test_unreadable_metadata_never_raises(self):
    self.store.values[local_auth_daemon.LOCAL_APPS_META_KEY] = "not a metadata document"
    self.assertEqual({}, local_auth_daemon.read_grant_meta())
    self.store.fail_reads = True
    self.assertEqual({}, local_auth_daemon.read_grant_meta())
    # on the session path, so it must swallow the fault rather than break a connection
    local_auth_daemon.note_grant_seen("key-a")

  def test_revoking_a_phone_drops_its_metadata(self):
    local_auth_daemon.set_grant_alias("key-a", "Nayan's phone")
    local_auth_daemon.clear_grant_meta("key-a")
    self.assertEqual({}, local_auth_daemon.read_grant_meta())


class TestGrantedAppsView(OpenpilotTestCase):
  """The device UI's read-only view of enrolled phones."""

  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.private_pem = self.device_key.private_bytes(
      serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    self.store = _ParamsStore({"SunnylinkDongleId": "cloud-device", "DongleId": "comma-device"})
    local_auth_daemon.reset_authority()
    self.addCleanup(local_auth_daemon.reset_authority)
    patcher = mock.patch.object(local_auth_daemon, "_params", self.store)
    patcher.start()
    self.addCleanup(patcher.stop)

  def write_registry(self, grants: list[Any]) -> None:
    self.store.values[local_auth_daemon.LOCAL_APPS_KEY] = {"v": 2, "grants": grants}

  def test_lists_app_id_and_name_without_building_the_authority(self):
    self.write_registry([{"app_id": "key-a", "app_name": "Nayan's phone", "public_key": "x", "key_id": "key-a",
                          "revision": "r"}])
    with mock.patch.object(local_auth_daemon, "_build_authority",
                           side_effect=AssertionError("the UI must not load the identity key")):
      rows = local_auth_daemon.read_granted_apps()
    self.assertEqual([{"app_id": "key-a", "app_name": "Nayan's phone"}], rows)

  def test_skips_entries_that_cannot_be_displayed(self):
    self.write_registry([{"app_id": "key-a"}, "junk", {"app_name": "no id"}, {"app_id": "", "app_name": "blank"},
                         {"app_id": "key-b", "app_name": "B"}])
    self.assertEqual([{"app_id": "key-b", "app_name": "B"}], local_auth_daemon.read_granted_apps())

  def test_no_registry_is_an_empty_list(self):
    self.assertEqual([], local_auth_daemon.read_granted_apps())


class TestRevokeRequests(OpenpilotTestCase):
  """Revoking from the device UI is a request the daemon applies through its live authority."""

  def setup_method(self):
    self.store = _ParamsStore()
    patcher = mock.patch.object(local_auth_daemon, "_params", self.store)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_request_and_service_round_trip(self):
    revoked: list[str] = []
    with mock.patch.object(local_auth_daemon, "revoke_local_app",
                           side_effect=lambda key: revoked.append(key) or True):
      local_auth_daemon.request_revoke("key-a")
      self.assertEqual("key-a", self.store.values[local_auth_daemon.REVOKE_KEY])
      self.assertTrue(local_auth_daemon.service_revoke_requests())
    self.assertEqual(["key-a"], revoked)
    # The request is consumed, so it cannot be applied twice on a later tick.
    self.assertNotIn(local_auth_daemon.REVOKE_KEY, self.store.values)
    self.assertFalse(local_auth_daemon.service_revoke_requests())

  def test_a_failed_revoke_still_clears_the_request(self):
    with mock.patch.object(local_auth_daemon, "revoke_local_app", side_effect=RuntimeError("boom")):
      local_auth_daemon.request_revoke("key-a")
      self.assertFalse(local_auth_daemon.service_revoke_requests())
    self.assertNotIn(local_auth_daemon.REVOKE_KEY, self.store.values)

  def test_unreadable_request_never_raises(self):
    self.store.values[local_auth_daemon.REVOKE_KEY] = "key-a"
    self.store.fail_reads = True
    self.assertFalse(local_auth_daemon.service_revoke_requests())

  def test_blank_requests_are_ignored(self):
    self.assertFalse(local_auth_daemon.request_revoke(""))
    self.assertEqual({}, self.store.values)

  def test_revoke_all_request_clears_every_grant_once(self):
    cleared: list[int] = []
    with mock.patch.object(local_auth_daemon, "revoke_all", side_effect=lambda: cleared.append(1) or 3):
      local_auth_daemon.request_revoke_all()
      self.assertTrue(self.store.values[local_auth_daemon.REVOKE_ALL_KEY])
      self.assertTrue(local_auth_daemon.service_revoke_requests())
    # Consumed, so a later tick does not revoke a phone the user pairs afterwards.
    self.assertNotIn(local_auth_daemon.REVOKE_ALL_KEY, self.store.values)
    self.assertEqual(1, len(cleared))
    self.assertFalse(local_auth_daemon.service_revoke_requests())

  def test_a_failed_revoke_all_still_clears_the_request(self):
    with mock.patch.object(local_auth_daemon, "revoke_all", side_effect=RuntimeError("boom")):
      local_auth_daemon.request_revoke_all()
      self.assertFalse(local_auth_daemon.service_revoke_requests())
    self.assertNotIn(local_auth_daemon.REVOKE_ALL_KEY, self.store.values)

  def test_revoke_all_takes_precedence_over_a_single_request(self):
    calls: list[str] = []
    with mock.patch.object(local_auth_daemon, "revoke_all", side_effect=lambda: calls.append("all") or 2), \
         mock.patch.object(local_auth_daemon, "revoke_local_app", side_effect=lambda key: calls.append(key) or True):
      local_auth_daemon.request_revoke("key-a")
      local_auth_daemon.request_revoke_all()
      local_auth_daemon.service_revoke_requests()
    # One action, and no leftover request that could revoke a phone paired afterwards.
    self.assertEqual(["all"], calls)
    self.assertNotIn(local_auth_daemon.REVOKE_KEY, self.store.values)
    self.assertNotIn(local_auth_daemon.REVOKE_ALL_KEY, self.store.values)


class TestRevokeAllThroughTheAuthority(OpenpilotTestCase):
  """`revoke_all` on the core: one durable write, and the grants really go away."""

  def setup_method(self):
    self.store = _ParamsStore()
    self.writes: list[dict] = []

    def persist(registry: dict) -> None:
      self.writes.append(registry)
      self.store.values[local_auth_daemon.LOCAL_APPS_KEY] = registry

    self.authority = LocalAuthority(
      cloud_device_id="cloud-device", comma_device_id="comma-device",
      device_private_key=ec.generate_private_key(ec.SECP256R1()),
      persist=persist,
      registry=None,
    )

  def test_revoke_all_writes_once_and_empties_the_registry(self):
    for key in ("key-a", "key-b"):
      self.authority.grants[key] = Grant(key, "spki", key, "Phone", "rev")
    self.assertEqual(2, self.authority.revoke_all())
    self.assertEqual({}, self.authority.grants)
    # One write for the whole action, and the persisted document is an empty registry.
    self.assertEqual([{"v": 2, "grants": []}], self.writes)

  def test_revoke_all_with_nothing_enrolled_writes_nothing(self):
    self.assertEqual(0, self.authority.revoke_all())
    self.assertEqual([], self.writes)


class TestPairingWindowParams(OpenpilotTestCase):
  def setup_method(self):
    self.store = _ParamsStore()
    patcher = mock.patch.object(local_auth_daemon, "_params", self.store)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_clear_pairing_params_does_not_touch_the_authority(self):
    """The UI's cancel is params-only: that process has no window to cancel, and building an
    authority there would load the device identity key for nothing."""
    self.store.values[local_auth_daemon.PAIRING_REQUEST_KEY] = True
    self.store.values[local_auth_daemon.PAIRING_QR_KEY] = "qr"
    with mock.patch.object(local_auth_daemon, "get_authority",
                           side_effect=AssertionError("must not build an authority")):
      local_auth_daemon.clear_pairing_params(cast(Params, self.store))
    self.assertNotIn(local_auth_daemon.PAIRING_REQUEST_KEY, self.store.values)
    self.assertNotIn(local_auth_daemon.PAIRING_QR_KEY, self.store.values)
