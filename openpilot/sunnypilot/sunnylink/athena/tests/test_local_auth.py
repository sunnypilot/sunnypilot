"""Q: what does the device need to remember so that a later dial proves the phone is still the same installation?

A grant — the phone's public key, pinned at enrollment — plus nothing that expires. There is no
session nonce and no scan ceremony: enrollment is a self-signed statement the app pushes over the
existing cloud settings-write transport (the app already knows the exact list of the user's devices
from the signed-in cloud device lookup, so it enrolls each one it has never enrolled — on login,
and again for newly-seen-online devices on manual refresh). The grant commits only when that phone
proves possession of the private key on a pinned-TLS dial. Manual Pair is just the same idempotent
push. An explicit unpair anywhere drops the grant, so the next dial re-authenticates from scratch.
The device remembers grants, not refusals: a phone-side skip list stops the same install from
re-enrolling an unpaired phone, but a fresh install has no memory of it.

This file pins that contract: staging is not authority (only a stored grant opens a session), the
TLS peer match is the commit, and the phone's own signature is the only thing that can enroll or
un-enroll it.
"""
import json
from unittest import mock

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec

from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.athena.local_auth import (
  AuthorizationError,
  Grant,
  LocalAuthority,
  Origin,
  decode64,
  encode64,
  key_id,
  statement,
  MAX_GRANTS,
  VERSION,
)

# The fields an enrollment carries. The signature binds them in this order.
ENROLL_FIELDS = ("cloud_device_id", "comma_device_id", "device_key_id",
                 "public_key", "key_id", "app_name")


def _spki(key) -> str:
  return encode64(key.public_key().public_bytes(
    serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo))


class TestV3Enrollment(OpenpilotTestCase):
  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.writes: list[dict] = []
    self.authority = LocalAuthority("cloud-device", "comma-device",
                                    self.device_key, self.writes.append)
    self.app_id = key_id(self.app_key.public_key())

  def enrollment(self, authority=None, key=None, **overrides) -> str:
    authority = authority or self.authority
    key = key or self.app_key
    public = _spki(key)
    data = {"v": VERSION, "cloud_device_id": authority.cloud_device_id,
            "comma_device_id": authority.comma_device_id, "device_key_id": authority.device_key_id,
            "public_key": public, "key_id": key_id(key.public_key()), "app_name": "Test phone"}
    data.update(overrides)
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(key.sign(proof, ec.ECDSA(hashes.SHA256())))
    return json.dumps(data)

  def committed(self, raw=None, authority=None):
    authority = authority or self.authority
    grant = authority.enroll(raw or self.enrollment(), Origin.CLOUD)
    return authority.confirm(grant, grant.app_id)

  def assert_session_denied(self, authority, grant, peer):
    with self.assertRaises(AuthorizationError):
      authority.session(grant, peer)

  def test_a_staged_enrollment_is_not_yet_authorized(self):
    grant = self.authority.enroll(self.enrollment(), Origin.CLOUD)
    self.assertEqual(self.app_id, grant.app_id)
    self.assert_session_denied(self.authority, grant, grant.app_id)
    # Nothing durable either: the grant does not exist until the TLS dial.
    self.assertEqual([], self.writes)
    self.assertIsNotNone(self.authority.pending)

  def test_confirming_without_a_matching_enrollment_refuses(self):
    stranger = Grant("no-such-phone", _spki(self.app_key), "Nobody")
    with self.assertRaises(AuthorizationError):
      self.authority.confirm(stranger, stranger.app_id)

  def test_the_grant_commits_only_after_the_tls_dial(self):
    grant = self.committed()
    session = self.authority.session(grant, grant.app_id)
    self.assertEqual("ok", session.invoke("getParams", lambda: "ok"))
    self.assertEqual([{"v": VERSION, "grants": [grant.to_dict()]}], self.writes)

  def test_confirming_with_the_wrong_tls_peer_refuses(self):
    grant = self.authority.enroll(self.enrollment(), Origin.CLOUD)
    with self.assertRaises(AuthorizationError):
      self.authority.confirm(grant, grant.app_id + "-other")
    self.assert_session_denied(self.authority, grant, grant.app_id)

  def test_enrolling_over_the_local_lan_is_impossible(self):
    """The staged path is cloud-only: a phone on the LAN cannot enroll itself mid-session."""
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(self.enrollment(), Origin.LOCAL)
    self.assertIsNone(self.authority.pending)

  def test_there_is_no_pairing_window_to_arm(self):
    """Pairing needs no on-screen step anymore: the authority has no window surface at all."""
    for name in ("arm", "window", "recent", "expire", "prune"):
      self.assertFalse(hasattr(self.authority, name), name)

  def test_a_v2_enrollment_is_rejected(self):
    """The QR-era payload shape is not valid anymore: legacy code was replaced, not kept."""
    data = json.loads(self.enrollment())
    data["v"] = 2
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(json.dumps(data), Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_a_pairing_session_field_is_rejected(self):
    data = json.loads(self.enrollment())
    data["pairing_session"] = "some-old-nonce"
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(json.dumps(data), Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_a_malformed_envelope_is_rejected(self):
    for raw in ("not json", "[1, 2]", json.dumps({"v": VERSION, "v2": VERSION}),
                "x" * 4097, json.dumps({"v": "3"}), json.dumps({"v": True})):
      with self.assertRaises(AuthorizationError):
        self.authority.enroll(raw, Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_the_device_ignores_a_request_that_does_not_name_it(self):
    """A push meant for another car stages nothing here."""
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(self.enrollment(comma_device_id="some-other-car"), Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_an_enrollment_cannot_be_replayed_against_another_car(self):
    other = LocalAuthority("cloud-other", "comma-other",
                           ec.generate_private_key(ec.SECP256R1()), lambda registry: None)
    with self.assertRaises(AuthorizationError):
      other.enroll(self.enrollment(), Origin.CLOUD)
    self.assertIsNone(other.pending)

  def test_same_installation_key_can_enroll_on_another_device(self):
    """One phone, two cars: the same installation key enrolls independently on each device."""
    other = LocalAuthority("cloud-other", "comma-other",
                           ec.generate_private_key(ec.SECP256R1()), lambda registry: None)
    grant = self.committed(self.enrollment(authority=other), authority=other)
    other.session(grant, grant.app_id)
    # …and that enrollment grants nothing on this car.
    self.assert_session_denied(self.authority, grant, grant.app_id)

  def test_idempotent_reenroll_returns_the_stored_grant(self):
    """Manual Pair on an already-paired phone is the same push: no duplicate, no new write."""
    grant = self.committed()
    again = self.authority.enroll(self.enrollment(), Origin.CLOUD)
    self.assertEqual(grant, again)
    self.assertEqual(1, len(self.writes))
    self.authority.session(again, again.app_id)

  def test_a_second_pending_enrollment_is_refused(self):
    self.authority.enroll(self.enrollment(), Origin.CLOUD)
    other_key = ec.generate_private_key(ec.SECP256R1())
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(self.enrollment(key=other_key), Origin.CLOUD)
    # The first phone's enrollment is undisturbed and still committable.
    self.assertEqual(self.app_id, self.authority.pending.app_id)

  def test_a_signature_that_covers_anything_else_is_rejected(self):
    """The signature binds every field: changing anything after signing voids the enrollment."""
    for field in ENROLL_FIELDS:
      raw = json.loads(self.enrollment())
      raw[field] = "tampered"
      with self.assertRaises(AuthorizationError):
        self.authority.enroll(json.dumps(raw), Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_staging_a_second_phone_does_not_disturb_the_first(self):
    first = self.committed()
    other_key = ec.generate_private_key(ec.SECP256R1())
    second = self.authority.enroll(self.enrollment(key=other_key), Origin.CLOUD)
    self.authority.session(first, first.app_id)
    self.assert_session_denied(self.authority, second, second.app_id)
    self.authority.confirm(second, second.app_id)
    self.authority.session(second, second.app_id)

  def test_grants_stop_at_the_limit(self):
    for _ in range(MAX_GRANTS):
      key = ec.generate_private_key(ec.SECP256R1())
      grant = self.authority.enroll(self.enrollment(key=key), Origin.CLOUD)
      self.authority.confirm(grant, grant.app_id)
    extra = ec.generate_private_key(ec.SECP256R1())
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(self.enrollment(key=extra), Origin.CLOUD)
    self.assertIsNone(self.authority.pending)

  def test_the_statement_can_be_read_backwards_from_the_wire(self):
    proof = statement("enroll", "cloud", "comma", "device-key", "key", "key-id", "Name")
    self.assertEqual(b"sunnylink-local\nenroll\ncloud\ncomma\ndevice-key\nkey\nkey-id\nName\n", proof)


class TestAuthorizedSession(OpenpilotTestCase):
  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.writes: list[dict] = []
    self.authority = LocalAuthority("cloud-device", "comma-device",
                                    self.device_key, self.writes.append)
    self.app_id = key_id(self.app_key.public_key())
    grant = self.authority.enroll(self._enrollment(), Origin.CLOUD)
    self.grant = self.authority.confirm(grant, grant.app_id)

  def _enrollment(self) -> str:
    public = _spki(self.app_key)
    data = {"v": VERSION, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
            "device_key_id": self.authority.device_key_id, "public_key": public,
            "key_id": self.app_id, "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
    return json.dumps(data)

  def test_a_stranger_is_not_authorized(self):
    stranger = Grant("no-such-phone", _spki(self.app_key), "Nobody")
    with self.assertRaises(AuthorizationError):
      self.authority.session(stranger, stranger.app_id)

  def test_a_known_installation_but_unknown_dial_is_not_authorized(self):
    with self.assertRaises(AuthorizationError):
      self.authority.session(self.grant, self.app_id + "-other")

  def test_a_second_car_does_not_share_this_cars_grants(self):
    other = LocalAuthority("cloud-other", "comma-other",
                           ec.generate_private_key(ec.SECP256R1()), lambda registry: None)
    with self.assertRaises(AuthorizationError):
      other.session(self.grant, self.app_id)

  def test_a_wrong_key_for_a_paired_app_id_is_not_authorized(self):
    impostor = Grant(self.app_id, _spki(ec.generate_private_key(ec.SECP256R1())), "Test phone")
    with self.assertRaises(AuthorizationError):
      self.authority.session(impostor, self.app_id)

  def test_an_unpaired_installation_is_not_authorized(self):
    self.authority.revoke(self.app_id)
    with self.assertRaises(AuthorizationError):
      self.authority.session(self.grant, self.app_id)

  def test_a_restarted_authority_keeps_its_grants(self):
    restarted = LocalAuthority("cloud-device", "comma-device",
                               self.device_key, lambda registry: None, registry=self.writes[-1])
    session = restarted.session(self.grant, self.app_id)
    self.assertEqual("ok", session.invoke("getParams", lambda: "ok"))

  def test_a_closed_session_refuses_calls(self):
    session = self.authority.session(self.grant, self.app_id)
    session.close()
    with self.assertRaises(AuthorizationError):
      session.invoke("getParams", lambda: "ok")

  def test_a_method_outside_the_local_surface_is_refused(self):
    session = self.authority.session(self.grant, self.app_id)
    with self.assertRaises(AuthorizationError):
      session.invoke("startLocalProxy", mock.Mock())

  def test_revoking_mid_session_kills_the_session(self):
    session = self.authority.session(self.grant, self.app_id)
    self.authority.revoke(self.app_id)
    with self.assertRaises(AuthorizationError):
      session.invoke("getParams", mock.Mock())


class TestGrantPersistence(OpenpilotTestCase):
  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.writes: list[dict] = []

  def _committed(self, authority=None):
    authority = authority or LocalAuthority(
      "cloud-device", "comma-device", self.device_key, self.writes.append)
    public = _spki(self.app_key)
    data = {"v": VERSION, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
            "device_key_id": authority.device_key_id, "public_key": public,
            "key_id": key_id(self.app_key.public_key()), "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
    grant = authority.enroll(json.dumps(data), Origin.CLOUD)
    return authority.confirm(grant, grant.app_id)

  def test_grants_reload_from_the_persisted_document(self):
    grant = self._committed()
    restarted = LocalAuthority("cloud-device", "comma-device",
                               self.device_key, lambda registry: None, registry=self.writes[-1])
    session = restarted.session(grant, grant.app_id)
    self.assertEqual("ok", session.invoke("getParams", lambda: "ok"))

  def test_a_registry_with_the_wrong_shape_is_ignored(self):
    key = _spki(self.app_key)
    entry = {"app_id": key_id(self.app_key.public_key()), "public_key": key, "app_name": "A"}
    bad_registries = [
      None, [], "registry", {"v": VERSION}, {"v": 999, "grants": []},
      {"v": VERSION, "grants": [{"app_id": "x"}]},
      {"v": VERSION, "grants": [{"app_id": "x", "public_key": "!!!", "app_name": "A"}]},
      {"v": VERSION, "grants": "not-a-list"},
      {"v": VERSION, "grants": [entry], "extra": True},
      {"v": VERSION, "grants": [dict(entry, app_id="somebody-else")]},
      {"v": VERSION, "grants": [entry, dict(entry)]},
    ]
    for bad in bad_registries:
      restarted = LocalAuthority("cloud-device", "comma-device", self.device_key,
                                 lambda registry: None, registry=bad)
      self.assertEqual({}, restarted.grants, bad)

  def test_more_grants_than_fit_are_ignored(self):
    entries = []
    for _ in range(MAX_GRANTS + 1):
      key = ec.generate_private_key(ec.SECP256R1())
      public = _spki(key)
      entries.append({"app_id": key_id(key.public_key()), "public_key": public, "app_name": "A"})
    restarted = LocalAuthority("cloud-device", "comma-device", self.device_key,
                               lambda registry: None,
                               registry={"v": VERSION, "grants": entries})
    self.assertEqual({}, restarted.grants)


class TestRevocation(OpenpilotTestCase):
  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.app_key = ec.generate_private_key(ec.SECP256R1())
    self.writes: list[dict] = []
    self.authority = LocalAuthority("cloud-device", "comma-device",
                                    self.device_key, self.writes.append)
    self.app_id = key_id(self.app_key.public_key())
    proof = statement("revoke", "cloud-device", "comma-device", self.app_id)
    self.revocation = json.dumps({"v": VERSION, "cloud_device_id": "cloud-device",
                                  "comma_device_id": "comma-device", "key_id": self.app_id,
                                  "signature": encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))})
    public = _spki(self.app_key)
    data = {"v": VERSION, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
            "device_key_id": self.authority.device_key_id, "public_key": public,
            "key_id": self.app_id, "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
    grant = self.authority.enroll(json.dumps(data), Origin.CLOUD)
    self.grant = self.authority.confirm(grant, grant.app_id)

  def test_an_installation_can_revoke_itself(self):
    self.assertEqual(self.app_id, self.authority.revoke_by_self_proof(self.revocation, Origin.CLOUD))
    with self.assertRaises(AuthorizationError):
      self.authority.session(self.grant, self.app_id)
    self.assertEqual({}, self.authority.grants)

  def test_a_revoked_installation_can_enroll_again(self):
    """Unpair is not a ban: the next auto-enroll push stages again, the next dial commits."""
    self.authority.revoke_by_self_proof(self.revocation, Origin.CLOUD)
    public = _spki(self.app_key)
    data = {"v": VERSION, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
            "device_key_id": self.authority.device_key_id, "public_key": public,
            "key_id": self.app_id, "app_name": "Test phone"}
    proof = statement("enroll", *(str(data[field]) for field in ENROLL_FIELDS))
    data["signature"] = encode64(self.app_key.sign(proof, ec.ECDSA(hashes.SHA256())))
    grant = self.authority.enroll(json.dumps(data), Origin.CLOUD)
    self.authority.confirm(grant, grant.app_id)
    self.authority.session(grant, grant.app_id)

  def test_revoking_over_the_local_lan_is_impossible(self):
    with self.assertRaises(AuthorizationError):
      self.authority.revoke_by_self_proof(self.revocation, Origin.LOCAL)
    self.authority.session(self.grant, self.app_id)

  def test_cloud_revocations_for_other_devices_are_ignored(self):
    payload = json.loads(self.revocation)
    payload["comma_device_id"] = "some-other-car"
    with self.assertRaises(AuthorizationError):
      self.authority.revoke_by_self_proof(json.dumps(payload), Origin.CLOUD)
    self.authority.session(self.grant, self.app_id)

  def test_revoking_an_unknown_key_is_a_noop(self):
    other_key = ec.generate_private_key(ec.SECP256R1())
    other_id = key_id(other_key.public_key())
    proof = statement("revoke", "cloud-device", "comma-device", other_id)
    raw = json.dumps({"v": VERSION, "cloud_device_id": "cloud-device", "comma_device_id": "comma-device",
                      "key_id": other_id,
                      "signature": encode64(other_key.sign(proof, ec.ECDSA(hashes.SHA256())))})
    self.assertEqual(other_id, self.authority.revoke_by_self_proof(raw, Origin.CLOUD))
    self.assertEqual(1, len(self.authority.grants))

  def test_a_forged_proof_for_an_enrolled_key_is_refused(self):
    forged = json.loads(self.revocation)
    forged["signature"] = encode64(ec.generate_private_key(ec.SECP256R1()).sign(
      statement("revoke", "cloud-device", "comma-device", self.app_id), ec.ECDSA(hashes.SHA256())))
    with self.assertRaises(AuthorizationError):
      self.authority.revoke_by_self_proof(json.dumps(forged), Origin.CLOUD)
    self.authority.session(self.grant, self.app_id)

  def test_a_revocation_is_not_an_enrollment(self):
    with self.assertRaises(AuthorizationError):
      self.authority.enroll(self.revocation, Origin.CLOUD)


class TestDeviceProof(OpenpilotTestCase):
  """The device proves itself to the dialing phone: it answers the phone's challenge."""

  def setup_method(self):
    self.device_key = ec.generate_private_key(ec.SECP256R1())
    self.authority = LocalAuthority("cloud-device", "comma-device",
                                    self.device_key, lambda registry: None)

  def test_the_device_signs_the_phones_challenge(self):
    from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
    challenge = encode64(b"\x00" * 32)
    proof = self.authority.authenticate_device("phone-key", challenge)
    self.assertEqual("cloud-device", proof["cloud_device_id"])
    self.assertEqual("comma-device", proof["comma_device_id"])
    self.assertEqual("phone-key", proof["phone_key_id"])
    expected = statement("authenticate-device", "cloud-device", "comma-device",
                         self.authority.device_key_id, "phone-key", challenge)
    self.device_key.public_key().verify(
      decode64(proof["signature"]), expected, ECDSA(hashes.SHA256()))

  def test_a_short_challenge_is_refused(self):
    with self.assertRaises(AuthorizationError):
      self.authority.authenticate_device("phone-key", encode64(b"\x00" * 31))
    with self.assertRaises(AuthorizationError):
      self.authority.authenticate_device("phone-key", "!!!")
