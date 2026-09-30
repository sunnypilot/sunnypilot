import json
import threading
import time
import unittest
import unittest.mock
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from openpilot.sunnypilot.sunnydrive import sunnydrived
from openpilot.sunnypilot.sunnydrive import pairing
from openpilot.sunnypilot.sunnydrive.sunnydrived import SunnydriveServer


class SunnydriveApiTest(unittest.TestCase):
  class FakeParams:
    def __init__(self):
      self.values = {"DongleId": "comma-test-12345678", "IsOffroad": True, "SunnydriveAutoPairPrompt": True}

    def get(self, key):
      return self.values.get(key)

    def get_bool(self, key):
      return bool(self.values.get(key))

    def put(self, key, value, block=False):
      self.values[key] = value

    def remove(self, key):
      self.values.pop(key, None)

  def test_slide_approval_pairing(self):
    params = self.FakeParams()
    request = pairing.request_pairing("phone_abcdefghijklmnop", "Second phone", params)
    replacement = pairing.request_pairing("phone_abcdefghijklmnop", "Second phone", params)
    self.assertNotEqual(replacement, request)
    request = replacement
    self.assertEqual(len(pairing.pairing_requests(params)), 1)
    self.assertTrue(pairing.approve_request(request, params))
    approved = pairing.consume_request(request, params)
    self.assertEqual(approved["status"], "approved")
    self.assertTrue(pairing.authorized(approved["token"], params))
    self.assertEqual(pairing.consume_request(request, params)["status"], "expired")

    params.values["SunnydriveAutoPairPrompt"] = False
    with self.assertRaisesRegex(PermissionError, "turned off"):
      pairing.request_pairing("phone_switched_off_123456", "Off", params)
    params.values["SunnydriveAutoPairPrompt"] = True

    params.values["IsOffroad"] = False   # pairing works onroad too
    self.assertTrue(pairing.approve_request(pairing.request_pairing("phone_onroad_123456789", "Onroad", params), params))

  def test_subscribed_services_exist(self):   # a renamed service crashes the sample loop and freezes telemetry
    from openpilot.cereal.services import SERVICE_LIST
    self.assertEqual([name for name in sunnydrived.SERVICES if name not in SERVICE_LIST], [])

  def test_discovery_is_metadata_only(self):
    packet = sunnydrived.DISCOVERY_PREFIX + b'{"v":1,"nonce":"12345678","clientId":"phone_1234567890123456"}'
    with patch.object(pairing, "device_id", return_value="comma-id"), \
         patch.object(pairing, "device_name", return_value="comma test"), \
         patch.object(pairing, "is_paired", return_value=False), \
         patch.object(pairing, "is_offroad", return_value=True):
      reply = sunnydrived.discovery_response(packet)
    body = json.loads(reply[len(sunnydrived.DISCOVERY_PREFIX):])
    self.assertEqual(set(body), {"v", "nonce", "deviceId", "name", "httpPort", "apiVersion", "paired", "offroad"})
    self.assertNotIn("token", body)

  def test_settings_follow_sunnylink_safety_rules(self):
    with patch("openpilot.common.params.Params") as params_class, patch.object(sunnydrived, "_setting_engaged", return_value=False) as engaged:
      params_class.return_value.get_bool.return_value = False
      params_class.return_value.get_type.return_value = 1
      sunnydrived.sunnylink_set("AlphaLongitudinalEnabled", True)
      params_class.return_value.put.assert_called_once()
      with self.assertRaisesRegex(PermissionError, "onroad or engaged"):
        sunnydrived.sunnylink_set("Mads", True)
      engaged.return_value = True
      with self.assertRaisesRegex(PermissionError, "onroad or engaged"):
        sunnydrived.sunnylink_set("AlphaLongitudinalEnabled", True)
      params_class.return_value.put.assert_called_once()
      params_class.return_value.get.return_value = b"1"   # TorqueParamsOverrideEnabled satisfies the schema's onroad alternative
      params_class.return_value.get_type.return_value = 3
      sunnydrived.sunnylink_set("TorqueParamsOverrideFriction", 0.1)
      self.assertEqual(params_class.return_value.put.call_count, 2)
      params_class.return_value.remove.assert_not_called()

  def test_live_frames_start_at_keyframe(self):
    def msg(key, data):
      frame = SimpleNamespace(idx=SimpleNamespace(flags=0x8 if key else 0), header=b"H" if key else b"", data=data)
      return SimpleNamespace(which=lambda: "livestreamCabinEncodeData", livestreamCabinEncodeData=frame)
    params = unittest.mock.MagicMock()
    with patch.object(sunnydrived.messaging, "sub_sock"), \
         patch.object(sunnydrived.messaging, "recv_one", side_effect=[msg(False, b"p0"), None, msg(True, b"k1"), msg(False, b"p2")]):
      frames = sunnydrived.live_frames("driver", params)
      self.assertEqual([next(frames) for _ in range(3)], [None, (True, b"Hk1"), (False, b"p2")])
    self.assertEqual([c.args for c in params.put_bool.call_args_list], [("LivestreamRequestKeyframe", True), ("LivestreamRequestKeyframe", False)])

  def test_route_list_cache(self):
    with TemporaryDirectory() as folder, patch.object(sunnydrived, "REALDATA", Path(folder)):
      sunnydrived._connect_routes.cache_clear()
      try:
        self.assertEqual(sunnydrived.connect_routes(), [])
        self.assertEqual(sunnydrived.connect_routes(), [])
        self.assertEqual(sunnydrived._connect_routes.cache_info().hits, 1)
      finally:
        sunnydrived._connect_routes.cache_clear()

  def test_api_only(self):
    server = SunnydriveServer(("127.0.0.1", 0))
    server.publish_telemetry({"timestampMs": 123})
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
      base = f"http://127.0.0.1:{server.server_address[1]}"
      request = Request(base + "/telemetry", headers={"Origin": "https://ai.sunnypilot.sunnydrive"})
      with urlopen(request, timeout=2) as response:
        self.assertEqual(json.load(response), server.telemetry)
        self.assertEqual(response.headers["Access-Control-Allow-Origin"], "https://ai.sunnypilot.sunnydrive")
      with urlopen(base + "/telemetry/stream", timeout=2) as first, urlopen(base + "/telemetry/stream", timeout=2) as second:
        self.assertEqual(first.readline(), b'data: {"timestampMs":123}\n')
        self.assertEqual(second.readline(), b'data: {"timestampMs":123}\n')
        first.readline()
        second.readline()
        server.publish_telemetry({"timestampMs": 456})
        self.assertEqual(first.readline(), b'data: {"timestampMs":456}\n')
        self.assertEqual(second.readline(), b'data: {"timestampMs":456}\n')
      for path in ("/", "/index.html", "/replay", "/youtube-playlists"):
        with self.assertRaises(HTTPError) as error:
          urlopen(base + path, timeout=2)
        self.assertEqual(error.exception.code, 404)
    finally:
      server.shutdown()
      server.server_close()
      thread.join(timeout=2)

  def test_unpaired_phone_cannot_read_api(self):
    server = SunnydriveServer(("127.0.0.1", 0), allow_loopback=False)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
      base = f"http://127.0.0.1:{server.server_address[1]}"
      with patch.object(pairing, "authorized", return_value=False):
        with self.assertRaises(HTTPError) as error:
          urlopen(base + "/telemetry", timeout=2)
        self.assertEqual(error.exception.code, 401)
      with patch.object(pairing, "device_id", return_value="comma-id"), \
           patch.object(pairing, "device_name", return_value="comma test"), \
           patch.object(pairing, "is_paired", return_value=False), \
           patch.object(pairing, "is_offroad", return_value=True):
        with urlopen(base + "/pair/info?client_id=phone_1234567890123456", timeout=2) as response:
          self.assertEqual(json.load(response)["deviceId"], "comma-id")
      with patch.object(pairing, "authorized", return_value=True):
        with urlopen(base + "/telemetry?auth=paired", timeout=2) as response:
          self.assertIn("timestampMs", json.load(response))
      with patch.object(pairing, "authorized", return_value=True) as authorized:   # unpairing cuts an open stream within a second
        with urlopen(base + "/telemetry/stream?auth=paired", timeout=5) as stream:
          self.assertTrue(stream.readline().startswith(b"data: "))
          stream.readline()   # the event's blank line
          authorized.return_value = False
          time.sleep(1.1)
          server.publish_telemetry({"timestampMs": 789})
          self.assertEqual(stream.read(), b"")
    finally:
      server.shutdown()
      server.server_close()
      thread.join(timeout=2)


if __name__ == "__main__":
  unittest.main()
