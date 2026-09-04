from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

from opendbc.car.ford.values import FordFlags
from openpilot.selfdrive.controls.lib.ford_path import FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_virtual_angle import (
  FordVirtualAngleController, select_virtual_angle_controller,
)


def car_params(**kwargs):
  values = {'brand': 'ford', 'flags': FordFlags.CANFD, 'carFingerprint': 'FORD_F_150_LIGHTNING_MK1',
                'steerActuatorDelay': 0.2, 'carFw': [SimpleNamespace(ecu='eps', fwVersion=b'RL38-14D003-AA')]}
  values.update(kwargs)
  return SimpleNamespace(**values)


class TestVirtualAngleSelection(unittest.TestCase):
  def test_opt_in_and_exact_vehicle_firmware_scope(self):
    for previous in (FordPathController(), FordPscmObserverPathController()):
      self.assertIs(select_virtual_angle_controller(car_params(), False, previous), previous)
      for overrides in ({'brand': 'tesla'}, {'flags': 0}, {'carFingerprint': 'FORD_F_150_MK14'},
                        {'carFw': []}, {'carFw': [SimpleNamespace(ecu='eps', fwVersion=b'ML3V')]}):
        self.assertIs(select_virtual_angle_controller(car_params(**overrides), True, previous), previous)
      self.assertIsInstance(select_virtual_angle_controller(car_params(), True, previous), FordVirtualAngleController)

  def test_old_setting_cannot_enable_new_controller(self):
    from openpilot.common.params import Params
    with tempfile.TemporaryDirectory(prefix='ford-virtual-params-') as directory:
      params = Params(directory)
      # Simulate a stored key left on an upgraded device; it is no longer registered.
      Path(params.get_param_path('FordSharedPathController')).write_text('1')
      self.assertNotIn(b'FordSharedPathController', params.all_keys())
      self.assertIs(params.get_default_value('FordVirtualAngleController'), False)
      self.assertFalse(params.get_bool('FordVirtualAngleController'))
      previous = FordPathController()
      self.assertIs(select_virtual_angle_controller(car_params(), params.get_bool('FordVirtualAngleController'), previous), previous)
      params.put_bool('FordVirtualAngleController', True, block=True)
      chosen = select_virtual_angle_controller(car_params(), params.get_bool('FordVirtualAngleController'), previous)
      params.put_bool('FordVirtualAngleController', False, block=True)
      self.assertIsInstance(chosen, FordVirtualAngleController)  # only selected at startup


if __name__ == '__main__':
  unittest.main()
