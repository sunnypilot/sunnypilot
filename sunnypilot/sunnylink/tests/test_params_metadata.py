#!/usr/bin/env python3
import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch

# Add openpilot root to python path
sys.path.append(os.getcwd())

# Mock ALL dependencies before importing sunnylinkd
jsonrpc_mock = MagicMock()


def add_method(func):
  return func


jsonrpc_mock.dispatcher.add_method = add_method

sys.modules["jsonrpc"] = jsonrpc_mock
sys.modules["jsonrpc.dispatcher"] = jsonrpc_mock.dispatcher
sys.modules["openpilot.common.params"] = MagicMock()
sys.modules["openpilot.common.realtime"] = MagicMock()
sys.modules["openpilot.common.swaglog"] = MagicMock()
sys.modules["openpilot.system.hardware.hw"] = MagicMock()
sys.modules["openpilot.system.athena.athenad"] = MagicMock()
sys.modules["websocket"] = MagicMock()
sys.modules["cereal"] = MagicMock()
sys.modules["cereal.messaging"] = MagicMock()
sys.modules["openpilot.sunnypilot.sunnylink.api"] = MagicMock()
sys.modules["openpilot.sunnypilot.sunnylink.utils"] = MagicMock()

# Now import sunnylinkd
from sunnypilot.sunnylink.athena import sunnylinkd


class TestParamsMetadata(unittest.TestCase):
  @patch("sunnypilot.sunnylink.athena.sunnylinkd.Params")
  @patch("sunnypilot.sunnylink.athena.sunnylinkd.get_param_as_byte")
  def test_metadata_parsing(self, mock_get_param, mock_params):
    # Setup mock Params
    mock_params_instance = mock_params.return_value
    mock_params_instance.all_keys.return_value = [b"LongitudinalPersonality", b"BlinkerMinLateralControlSpeed", b"DongleId"]
    mock_params_instance.get_type.return_value.value = 1  # INT

    # Setup mock get_key_metadata
    def get_key_metadata_side_effect(key):
      if key == "LongitudinalPersonality":
        return json.dumps(
          {"enum": "LongitudinalPersonality", "title": "Driving Personality", "description": "Adjusts the driving style of the openpilot longitudinal control."}
        )
      elif key == "BlinkerMinLateralControlSpeed":
        return json.dumps(
          {
            "min": 0,
            "max": 255,
            "step": 1,
            "title": "Blinker Min Lat Control Speed",
            "units": "mph",
            "description": "Minimum speed for lateral control during blinker usage.",
          }
        )
      return None

    mock_params_instance.get_key_metadata.side_effect = get_key_metadata_side_effect

    # Setup mock get_param_as_byte
    mock_get_param.return_value = b"1"

    # Mock cereal.log
    mock_log = MagicMock()
    sunnylinkd.log = mock_log

    # Setup LongitudinalPersonality enum mock
    mock_enum = MagicMock()
    mock_enum.schema.enumerants = {"Aggressive": 0, "Standard": 1, "Relaxed": 2}
    mock_log.LongitudinalPersonality = mock_enum

    # Call the function
    response = sunnylinkd.getParamsAllKeysV1()

    self.assertIn("keys", response)
    params = json.loads(response["keys"])

    # Check LongitudinalPersonality (Enum)
    lp_param = next((p for p in params if p["key"] == "LongitudinalPersonality"), None)
    self.assertIsNotNone(lp_param)

    # Debug print
    print(f"LongitudinalPersonality param: {lp_param}")

    self.assertIn("_extra", lp_param)
    extra = lp_param["_extra"]
    self.assertIsNotNone(extra)
    self.assertEqual(extra.get("title"), "Driving Personality")
    self.assertEqual(extra.get("enum"), "LongitudinalPersonality")

    # Verify options are populated from our mock
    self.assertIn("options", extra)
    options = extra["options"]
    self.assertEqual(len(options), 3)
    self.assertEqual(options[0]["label"], "Aggressive")
    self.assertEqual(options[0]["value"], 0)

    # Check BlinkerMinLateralControlSpeed (Numeric)
    blinker_param = next((p for p in params if p["key"] == "BlinkerMinLateralControlSpeed"), None)
    self.assertIsNotNone(blinker_param)
    extra = blinker_param["_extra"]
    self.assertIsNotNone(extra)
    self.assertEqual(extra.get("title"), "Blinker Min Lat Control Speed")
    self.assertEqual(extra.get("min"), 0)
    self.assertEqual(extra.get("max"), 255)
    self.assertEqual(extra.get("units"), "mph")

    # Check a param without metadata
    other_param = next((p for p in params if p["key"] == "DongleId"), None)
    self.assertIsNotNone(other_param)
    self.assertIsNone(other_param.get("_extra"))


if __name__ == "__main__":
  unittest.main()
