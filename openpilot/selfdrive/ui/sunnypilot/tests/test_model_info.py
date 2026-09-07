"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from unittest import mock

from openpilot.cereal import custom
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.ui.sunnypilot import model_info
from openpilot.selfdrive.ui.ui_state import ChestnutState
from openpilot.sunnypilot.models.helpers import REQUIRED_JSON_VERSION
from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL


def _raw_bundle(ref: str) -> dict:
  bundle = custom.ModelManagerSP.ModelBundle.new_message()
  bundle.ref = ref
  bundle.minimumSelectorVersion = REQUIRED_JSON_VERSION
  bundle.internalName = ref
  bundle.displayName = ref
  bundle.runner = custom.ModelManagerSP.Runner.tinygrad
  return bundle.to_dict()


class TestCarryingModel(OpenpilotTestCase):
  """What the UI names as driving has to be what stock modeld loads. Under the
  jetlink override that is the default small model, never the stored qcom bundle."""

  def setUp(self):
    super().setUp()
    self.ui_state = mock.MagicMock()
    self.ui_state.chestnut_present = False
    self.ui_state.chestnut_state = ChestnutState.DISCONNECTED
    self.ui_state.chestnut_active = False
    self.ui_state.chestnut_loading = False
    self.ui_state.is_offroad.return_value = True
    self.ui_state.params.get.side_effect = lambda key: {"ModelManager_ActiveBundle": _raw_bundle("custom_small")}.get(key)
    patcher = mock.patch.object(model_info, "ui_state", self.ui_state)
    patcher.start()
    self.addCleanup(patcher.stop)

  def test_override_names_the_default_small_model(self):
    with mock.patch("openpilot.sunnypilot.accelerators.uses_stock_runner", return_value=True):
      assert model_info.carrying_model() == ("qcom", f"{DEFAULT_MODEL} (Default)", f"{DEFAULT_MODEL} (Default)")
      source, active, _ = model_info.model_info()
    assert (source, active) == ("qcom", f"{DEFAULT_MODEL} (Default)")

  def test_without_override_names_the_stored_bundle(self):
    with mock.patch("openpilot.sunnypilot.accelerators.uses_stock_runner", return_value=False):
      assert model_info.carrying_model() == ("qcom", "custom_small", "custom_small")
      source, active, _ = model_info.model_info()
    assert (source, active) == ("qcom", "custom_small")

  def test_link_active_names_the_accelerator_model(self):
    self.ui_state.chestnut_state = ChestnutState.ACTIVE
    with mock.patch("openpilot.sunnypilot.accelerators.uses_stock_runner", return_value=True), \
         mock.patch("openpilot.sunnypilot.accelerators.active_model_name", return_value="big"):
      assert model_info.carrying_model() == ("accelerator", "big", "big")

  def test_fitted_board_is_chestnut_not_jetlink(self):
    # a real chestnut ACTIVE keeps comma's semantics whatever JetlinkModel says
    self.ui_state.chestnut_present = True
    self.ui_state.chestnut_state = ChestnutState.ACTIVE
    self.ui_state.params.get.side_effect = lambda key: {"ModelManager_ActiveBundleChestnut": _raw_bundle("big_custom")}.get(key)
    with mock.patch("openpilot.sunnypilot.accelerators.active_model_name", return_value="jetlink_big"):
      assert model_info.carrying_model() == ("chestnut", "big_custom", "big_custom")
