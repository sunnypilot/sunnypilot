import tempfile
import unittest
from unittest.mock import patch

from opendbc.car.structs import car
from openpilot.cereal import custom
from openpilot.common.params import Params
from openpilot.sunnypilot.selfdrive.car.cruise_ext import CRUISE_BUTTON_TIMER, SpeedLimitAssistState, VCruiseHelperSP
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.automatic_set import AutomaticSet, StableMapLimit
from openpilot.sunnypilot.selfdrive.controls.lib.speed_limit.common import Mode


class TestAutoCruiseReadFailures(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    params = Params(self.temp.name)
    for key, value in (('SpeedLimitMode', 4), ('SpeedLimitOffsetType', 0), ('SpeedLimitValueOffset', -10)):
      params.put(key, value, block=True)
    self.helper = VCruiseHelperSP.__new__(VCruiseHelperSP)
    self.helper.params = params
    self.helper.CP = car.CarParams.new_message(brand='honda', carFingerprint='HONDA_CITY_7G',
                                             openpilotLongitudinalControl=True, pcmCruise=False)
    self.helper.auto_set = AutomaticSet()
    self.helper.auto_button_timers = dict.fromkeys(CRUISE_BUTTON_TIMER, 0)
    self.helper.auto_map = StableMapLimit()
    self.helper.speed_limit_mode = Mode.automatic
    self.helper.mode_read_at = 0.
    self.helper.auto_params_valid = True
    self.helper.auto_offset_type = 0
    self.helper.auto_offset_value = -10
    self.helper.auto_gps_service = 'gpsLocationExternal'
    self.helper.auto_target = 80.
    self.helper.auto_control_ok = True
    self.helper.v_cruise_kph = self.helper.v_cruise_cluster_kph = 50
    self.helper.v_cruise_min = 30
    self.helper.sla_state = SpeedLimitAssistState.disabled
    self.helper.enable_button_timers = CRUISE_BUTTON_TIMER.copy()
    self.cs = car.CarState.new_message(canValid=True, canTimeout=False)
    self.cs.cruiseState.available = True
    self.lp = custom.LongitudinalPlanSP.new_message()
    self.helper.auto_set.engaged = self.helper.auto_set.armed = True

  def test_parameter_read_failure_preserves_driver_takeover(self):
    for key in ('SpeedLimitMode', 'SpeedLimitOffsetType', 'SpeedLimitValueOffset'):
      for event in ('gasPressed', 'brakePressed', 'cancel'):
        with self.subTest(key=key, event=event):
          self.setUp()
          if event == 'cancel':
            self.cs.buttonEvents = [{'type': 'cancel', 'pressed': True}]
          else:
            setattr(self.cs, event, True)
          get = self.helper.params.get

          def read(name, key=key, get=get, **kwargs):
            if name == key:
              raise RuntimeError('injected Params read failure')
            return get(name, **kwargs)

          with patch.object(self.helper.params, 'get', side_effect=read), patch(
            'openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=100.,
          ):
            self.helper.update_speed_limit_assist(True, self.lp)
            self.assertIsNone(self.helper.auto_target)
            self.assertFalse(self.helper.auto_control_ok)
            self.helper.update_automatic_set(self.cs, True)
          self.assertTrue(self.helper.auto_set.takeover)
          self.assertEqual(self.helper.v_cruise_kph, 50.)
          self.cs.gasPressed = self.cs.brakePressed = False
          self.cs.buttonEvents = []
          with patch('openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=101.):
            self.helper.update_speed_limit_assist(True, self.lp)
            self.helper.auto_target = 80.
            self.helper.auto_control_ok = True
            self.helper.update_automatic_set(self.cs, True)
          self.assertEqual(self.helper.v_cruise_kph, 50.)
          self.helper.update_automatic_set(self.cs, False)
          for now in (102., 102.1, 102.7):
            with patch('openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=now):
              self.helper.update_automatic_set(self.cs, True)
          self.assertEqual(self.helper.v_cruise_kph, 80.)

  def test_failed_snapshot_is_not_partially_applied_or_reused(self):
    get = self.helper.params.get

    def read(name, **kwargs):
      if name == 'SpeedLimitOffsetType':
        return 1
      if name == 'SpeedLimitValueOffset':
        raise RuntimeError('injected final read failure')
      return get(name, **kwargs)

    with patch.object(self.helper.params, 'get', side_effect=read), patch(
      'openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=100.,
    ):
      self.helper.update_speed_limit_assist(True, self.lp)
    self.assertEqual(self.helper.auto_offset_type, 0)
    self.assertFalse(self.helper.auto_params_valid)
    with patch('openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=100.1):
      self.helper.update_speed_limit_assist(True, self.lp, plan_fresh=True, control_fresh=True, long_active=True, override=False)
    self.assertFalse(self.helper.auto_control_ok)
    with patch('openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=100.6):
      self.helper.update_speed_limit_assist(True, self.lp)
    self.assertTrue(self.helper.auto_params_valid)

  def test_oversized_integer_offset_does_not_interrupt_pedal(self):
    self.helper.params.put('SpeedLimitValueOffset', 10 ** 400, block=True)
    self.cs.brakePressed = True
    with patch('openpilot.sunnypilot.selfdrive.car.cruise_ext.time.monotonic', return_value=100.):
      self.helper.update_speed_limit_assist(True, self.lp)
      self.helper.update_automatic_set(self.cs, True)
    self.assertFalse(self.helper.auto_params_valid)
    self.assertIsNone(self.helper.auto_target)
    self.assertTrue(self.helper.auto_set.takeover)


if __name__ == '__main__':
  unittest.main()
