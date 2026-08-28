"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.system.params_migration import _migrate_model_bundle_slots, run_migration


class TestAssistedDistanceMilestoneReset(OpenpilotTestCase):
  def test_resets_existing_distances_once(self):
    class ParamsStub:
      def __init__(self):
        self.values = {
          "MadsDrivenDistanceMeters": 123.0,
          "FullAssistDrivenDistanceMeters": 456.0,
          "OnroadScreenOffBrightness": 0,
          "OnroadScreenOffTimer": 15,
          "AssistedDistanceMilestoneResetVersion": "0",
        }

      def get(self, key, return_default=False):
        return self.values.get(key)

      def put(self, key, value, block=False):
        self.values[key] = value

    params = ParamsStub()

    run_migration(params)

    assert params.get("MadsDrivenDistanceMeters") == 0.0
    assert params.get("FullAssistDrivenDistanceMeters") == 0.0

    params.put("MadsDrivenDistanceMeters", 12.0, block=True)
    params.put("FullAssistDrivenDistanceMeters", 34.0, block=True)
    run_migration(params)

    assert params.get("MadsDrivenDistanceMeters") == 12.0
    assert params.get("FullAssistDrivenDistanceMeters") == 34.0


class TestModelBundleSlotMigration(OpenpilotTestCase):
  """Pre-split, a chestnut user's big-model selection lived in the single ActiveBundle.
  The migration seeds both slots; per-source validation later drops whichever does not
  match its own manifest."""

  def test_seeds_usbgpu_slot_from_active_bundle(self):
    params = Params()
    bundle = {"ref": "big", "minimumSelectorVersion": 18}
    params.put("ModelManager_ActiveBundle", bundle, block=True)
    _migrate_model_bundle_slots(params)
    assert params.get("ModelManager_ActiveBundleUSBGPU") == bundle
    assert params.get("ModelManager_ActiveBundle") == bundle

  def test_noop_when_usbgpu_slot_already_set(self):
    params = Params()
    params.put("ModelManager_ActiveBundle", {"ref": "small"}, block=True)
    params.put("ModelManager_ActiveBundleUSBGPU", {"ref": "big"}, block=True)
    _migrate_model_bundle_slots(params)
    assert params.get("ModelManager_ActiveBundleUSBGPU") == {"ref": "big"}

  def test_noop_when_no_selection(self):
    params = Params()
    _migrate_model_bundle_slots(params)
    assert params.get("ModelManager_ActiveBundleUSBGPU") is None
