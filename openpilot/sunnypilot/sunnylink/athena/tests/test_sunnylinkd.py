"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import shutil
import tempfile
from unittest import mock

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.sunnylink.athena import sunnylinkd
from openpilot.sunnypilot.sunnylink.athena.local_params import ENROLL, REVOKE

# The local daemon owns this payload's contents; to the cloud transport it is one opaque value.
ENROLLMENT_JSON = '{"v":2,"purpose":"sunnylink-local-enroll"}'


class TestCloudRpcSurface(OpenpilotTestCase):
  """The cloud daemon serves settings and must never expose or mutate local trust."""

  def setup_method(self):
    self.saved_params = []
    self.original_save = sunnylinkd.save_param_from_base64_encoded_string
    sunnylinkd.save_param_from_base64_encoded_string = self._record  # ty: ignore[invalid-assignment]
    self.daemon = sunnylinkd.Sunnylinkd()

  def teardown_method(self):
    sunnylinkd.save_param_from_base64_encoded_string = self.original_save  # ty: ignore[invalid-assignment]

  def _record(self, key, value, compression=False):
    self.saved_params.append((key, value, compression))

  def test_methods_are_the_cloud_surface_only(self):
    methods = self.daemon.methods()
    self.assertTrue("getParams" in methods)
    self.assertTrue("saveParams" in methods)
    # Local serving is another process: no local pairing or alias RPC is registered here.
    for name in ("pairLocalApp", "updateLocalAppAlias", "unpairLocalApp"):
      self.assertNotIn(name, methods)

  def test_saveParams_blocked(self):
    blocked_params = {
      "GithubUsername": "attacker",
      "GithubSshKeys": "ssh-rsa attacker_key",
    }

    self.daemon.saveParams(blocked_params)

    assert len(self.saved_params) == 0

  def test_saveParams_allowed(self):
    self.daemon.saveParams({
      "SpeedLimitOffset": "5",
      "MyCustomParam": "123",
    })

    assert len(self.saved_params) == 2
    keys_saved = [p[0] for p in self.saved_params]
    assert "SpeedLimitOffset" in keys_saved
    assert "MyCustomParam" in keys_saved

  def test_saveParams_mixed(self):
    self.daemon.saveParams({
      "GithubUsername": "attacker",
      "SpeedLimitOffset": "10",
    })

    assert len(self.saved_params) == 1
    assert self.saved_params[0][0] == "SpeedLimitOffset"
    assert self.saved_params[0][1] == "10"

  def test_saveParams_cannot_modify_local_trust(self):
    self.daemon.saveParams({
      "SunnylinkLocalApps": "attacker registry",
      "SunnylinkLocalAppsMeta": "attacker metadata",
      "SunnylinkLocalPairingRequest": "1",
      "SunnylinkLocalPairingQr": "attacker qr",
      "SunnylinkLocalRevoke": "attacker revoke request",
      "SunnylinkLocalFutureKey": "attacker key",
      "_sec_SunnylinkLocalFuture": "attacker secret",
    })
    self.assertEqual(self.saved_params, [])

  def test_saveParams_delivers_only_the_two_local_commands(self):
    self.daemon.saveParams({ENROLL: "ZW5yb2xs", REVOKE: "cmV2b2tl", "SunnylinkLocalApps": "attacker"})
    self.assertEqual(self.saved_params, [(ENROLL, "ZW5yb2xs", False), (REVOKE, "cmV2b2tl", False)])

  def test_getParams_never_exposes_local_parameters(self):
    response = self.daemon.getParams(["SunnylinkLocalApps", "SunnylinkLocalAppsMeta",
                                      "SunnylinkLocalPairingRequest", "SunnylinkLocalPairingQr",
                                      "SunnylinkLocalRevoke", ENROLL, REVOKE])
    self.assertEqual(response, {"params": "[]"})

  def test_getParams_serves_ordinary_settings(self):
    response = self.daemon.getParams(["SunnylinkEnabled"])
    self.assertTrue("SunnylinkEnabled" in response)

  def test_getParamsAllKeys_excludes_local_params(self):
    keys = self.daemon.getParamsAllKeys()
    for key in ("SunnylinkLocalApps", "SunnylinkLocalAppsMeta", "SunnylinkLocalPairingQr",
                "SunnylinkLocalEnabled", ENROLL, REVOKE):
      self.assertNotIn(key, keys)
    self.assertTrue("SpeedLimitValueOffset" in keys)


class TestCloudCommandTransport(OpenpilotTestCase):
  """How an app's local command reaches the device: the cloud settings-write stores it.

  The two commands are ordinary declared params on the cloud path, so the encoding the app
  already uses (standard base64 of a UTF-8 JSON payload) is decoded by the same helper that
  every other remotely written param goes through.
  """

  def setup_method(self):
    self.dir = tempfile.mkdtemp(prefix="sunnylink_params_")
    self.addCleanup(shutil.rmtree, self.dir, ignore_errors=True)
    self.daemon = sunnylinkd.Sunnylinkd(params=Params(self.dir))
    patcher = mock.patch("openpilot.sunnypilot.sunnylink.utils.Params", lambda: Params(self.dir))
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_the_enrollment_lands_as_json_in_its_param(self):
    self.daemon.saveParams({ENROLL: base64.b64encode(ENROLLMENT_JSON.encode()).decode("ascii")})
    self.assertEqual(ENROLLMENT_JSON, Params(self.dir).get(ENROLL))

  def test_the_revocation_lands_as_json_in_its_param(self):
    self.daemon.saveParams({REVOKE: base64.b64encode(b'{"v":2}').decode("ascii")})
    self.assertEqual('{"v":2}', Params(self.dir).get(REVOKE))

  def test_a_compressed_command_also_arrives_readable(self):
    import gzip
    self.daemon.saveParams({ENROLL: base64.b64encode(gzip.compress(ENROLLMENT_JSON.encode())).decode("ascii")},
                           compression=True)
    self.assertEqual(ENROLLMENT_JSON, Params(self.dir).get(ENROLL))

  def test_the_cloud_may_not_write_any_other_local_param(self):
    with mock.patch.object(sunnylinkd, "save_param_from_base64_encoded_string") as save:
      self.daemon.saveParams({"SunnylinkLocalApps": base64.b64encode(b"{}").decode("ascii")})
    save.assert_not_called()
