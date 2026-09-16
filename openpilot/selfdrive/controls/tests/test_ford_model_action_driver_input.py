"""Exercise Ford's actual driver-input filter together with path feedback."""
from types import SimpleNamespace

import pytest

from opendbc.car.ford.values import CarControllerParams
from opendbc.car.interfaces import CarStateBase
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from openpilot.selfdrive.controls.tests.test_ford_model_action_feedback import adapter_tick, status


def pressed(state, torque):
  # Ford CarState.update uses this shared filter with minimum count 5.
  return CarStateBase.update_steering_pressed(state, abs(torque) > CarControllerParams.STEER_DRIVER_ALLOWANCE, 5)


@pytest.mark.parametrize('sign', [-1., 1.])
def test_twenty_ms_torque_spike_does_not_drop_feedback_before_ford_detects_driver_input(sign):
  state = SimpleNamespace(steering_pressed_cnt=0)
  controller, steady = FordModelActionController(), FordModelActionController()
  # Route 15a at 196.19 s: two 1.0625 Nm samples, steeringPressed remained false.
  torques = [0.]*50+[sign*1.0625]*2+[0.]*20
  for i, torque in enumerate(torques):
    now = 1.+i*.01
    driver = pressed(state, torque)
    assert not driver
    actual = adapter_tick(controller, now, speed=3.2, driver_pressed=driver, driver_torque=torque)
    expected = adapter_tick(steady, now, speed=3.2)
    assert actual == expected
    assert controller.core.correction == steady.core.correction
    assert controller.diagnostics['feedback_enabled']
  assert controller.core.correction > 0.


@pytest.mark.parametrize('sign', [-1., 1.])
def test_sustained_driver_input_clears_feedback_on_the_first_filtered_pressed_sample(sign):
  state = SimpleNamespace(steering_pressed_cnt=0)
  controller = FordModelActionController()
  for i in range(50):
    adapter_tick(controller, 1.+i*.01, speed=3.2)
  assert controller.core.correction > 0.
  detected = False
  for i in range(12):
    torque = sign*1.0625
    driver = pressed(state, torque)
    adapter_tick(controller, 1.5+i*.01, speed=3.2, driver_pressed=driver, driver_torque=torque)
    assert controller.diagnostics['feedback_enabled'] == (not driver)
    if driver:
      detected = True
      assert controller.core.correction == controller.core.proportional == controller.core.offset_proportional == 0.
  assert detected


def test_pscm_override_remains_immediate_before_driver_filter_triggers():
  controller = FordModelActionController()
  for i in range(50):
    adapter_tick(controller, 1.+i*.01, speed=3.2)
  adapter_tick(controller, 1.5, speed=3.2, driver_pressed=False, driver_torque=1.0625,
               pscm_status=status(1.5, limit=3))
  assert not controller.diagnostics['feedback_enabled']
  assert controller.core.correction == controller.core.proportional == controller.core.offset_proportional == 0.
