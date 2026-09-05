import ast
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from openpilot.cereal import custom
from openpilot.common.logging_extra import SwagFormatter, SwagLogger
from openpilot.selfdrive.controls.lib.ford_path import FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController, PscmStatus
from openpilot.selfdrive.controls.tests.test_ford_path_reference import circle


class TestFordControlsLogging(unittest.TestCase):
  def emit_controls_event(self, event, controls):
    # Execute the actual controlsd call with the real logger and formatter,
    # without launching hardware-dependent Controls or opening logging IPC.
    source_path = Path(__file__).resolve().parents[1] / 'controlsd.py'
    source = ast.parse(source_path.read_text())
    calls = [node for node in ast.walk(source) if isinstance(node, ast.Call)
             and isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name)
             and node.func.value.id == 'cloudlog' and node.args
             and isinstance(node.args[0], ast.Constant) and node.args[0].value == event]
    self.assertEqual(len(calls), 1)
    logger = SwagLogger()
    logger.setLevel(logging.INFO)  # disabled INFO logging would hide this crash
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(SwagFormatter(logger))
    logger.addHandler(handler)
    try:
      expression = ast.Expression(body=calls[0])
      eval(compile(expression, str(source_path), 'eval'), {'cloudlog': logger, 'self': controls, 'reference_service': 'modelV2'})
      record = json.loads(stream.getvalue())
    finally:
      handler.close()
    self.assertEqual(record['level'], 'INFO')
    self.assertEqual(record['msg']['event'], event)
    return record['msg']

  def test_startup_logs_selected_controller_without_crashing(self):
    for controller in (FordPathController(), FordPscmObserverPathController(), FordVirtualAngleController()):
      with self.subTest(controller=type(controller).__name__):
        record = self.emit_controls_event('Ford path controller selected', SimpleNamespace(ford_path_controller=controller))
        self.assertEqual(record['controller'], type(controller).__name__)

  def test_periodic_diagnostics_log_without_crashing(self):
    controller = FordVirtualAngleController()
    for active, valid, pressed in ((False, True, False), (True, True, False), (True, True, True), (True, False, False)):
      controller.reset()
      controller.update(circle(.01), .01, yaw_rate=.05, speed=10.0, now=1.0,
                        measurement_time=1.0, model_time=1.0, reference_time=1.0, active=active,
                        valid=valid, steering_pressed=pressed)
      controls = SimpleNamespace(ford_path_controller=controller, desired_curvature=.01, curvature=.005,
                                 sm=SimpleNamespace(logMonoTime={'modelV2': 123456789, 'carState': 123450000}))
      record = self.emit_controls_event('Ford C2-free path tracking', controls)
      self.assertEqual(record['model_mono_time'], 123456789)
      self.assertEqual(record['measurement_mono_time'], 123450000)
      self.assertEqual(record['reference_service'], 'modelV2')
      self.assertEqual(record['reference_mono_time'], 123456789)
      self.assertEqual(record['status'], controller.diagnostics['status'])
      self.assertEqual(record['hypothesis'], 'model-pose-c0-c1-feedback-v6')
      self.assertEqual(record['command'], list(controller.diagnostics['command']))
      self.assertIs(record['feedback_backoff_active'], False)
      if active and valid:
        self.assertEqual(record['response_delay'], 0.2)
        self.assertEqual(record['desired_curvature'], 0.01)
        self.assertEqual(record['measured_curvature'], 0.005)
        self.assertEqual(record['base_guard'], 'blended')
        self.assertGreater(record['model_share'], 0.)
        self.assertLess(record['model_share'], 1.)
        self.assertEqual(record['heading_target'], record['heading_base'])  # missing PSCM status leaves the base intact
        self.assertTrue(all(key in record for key in ('offset_target', 'heading_target', 'model_heading_target', 'model_heading_horizon',
                                                    'model_age', 'reference_age', 'reference_filter_time', 'model_offset_base', 'model_heading_base',
                                                    'curvature_offset_base', 'curvature_heading_base', 'model_share', 'base_guard')))

  def test_periodic_diagnostics_distinguish_model_curvature_and_blended_bases(self):
    for desired, geometry, guard, share in ((.02, .02, 'model_pose', 1.), (.002, .002, 'curvature_only', 0.),
                                           (.01, .01, 'blended', 2 / 3), (-.02, .02, 'opposed_model', 0.),
                                           (.002, 0., 'opposed_model', 0.), (0., .02, 'zero_request', 0.)):
      with self.subTest(desired=desired, geometry=geometry):
        controller = FordVirtualAngleController()
        controller.update(circle(geometry), desired, yaw_rate=0., speed=10., now=1., measurement_time=1.,
                          model_time=1., reference_time=1., active=True)
        controls = SimpleNamespace(ford_path_controller=controller, desired_curvature=desired, curvature=0.,
                                   sm=SimpleNamespace(logMonoTime={'modelV2': 1_000_000_000, 'carState': 1_000_000_000}))
        record = self.emit_controls_event('Ford C2-free path tracking', controls)
        self.assertEqual(record['base_guard'], guard)
        self.assertAlmostEqual(record['model_share'], share)
        for key in ('model_offset_base', 'model_heading_base', 'curvature_offset_base', 'curvature_heading_base'):
          self.assertEqual(record[key], controller.diagnostics[key])
        self.assertAlmostEqual(record['offset_target'], record['model_offset_base'] + record['curvature_offset_base'])
        self.assertAlmostEqual(record['heading_base'], record['model_heading_base'] + record['curvature_heading_base'])
        self.assertEqual(record['feedback_status'], 'missing_pscm')
        self.assertEqual(record['heading_bias'], 0.)
        self.assertEqual(record['command'][2:], [0., 0.])
        if share == 0.:
          self.assertEqual((record['model_offset_base'], record['model_heading_base']), (0., 0.))
        if share == 1.:
          self.assertEqual((record['curvature_offset_base'], record['curvature_heading_base']), (0., 0.))

  def test_periodic_diagnostics_log_backoff_between_measurements(self):
    controller = FordVirtualAngleController()
    for i in range(50):
      now = 1. + i * .01
      controller.update(circle(.02), .02, yaw_rate=.2, speed=10., now=now, measurement_time=now,
                        model_time=now, reference_time=now, active=True, pscm_status=PscmStatus(now, 2, 0, 2, False))
    cases = ((1.5, .02, 1.5, 'pscm_backoff', True), (1.51, .02, 1.5, 'no_new_measurement', True),
             (1.52, .05, 1.52, 'pscm_limit', False))
    for now, desired, measurement, expected_status, backoff in cases:
      controller.update(circle(.03), desired, yaw_rate=.5, speed=10., now=now, measurement_time=measurement,
                        model_time=now, reference_time=now, active=True, pscm_status=PscmStatus(now, 2, 2, 2, False))
      controls = SimpleNamespace(ford_path_controller=controller, desired_curvature=desired, curvature=.05,
                                 sm=SimpleNamespace(logMonoTime={'modelV2': int(now * 1e9), 'carState': int(measurement * 1e9)}))
      record = self.emit_controls_event('Ford C2-free path tracking', controls)
      self.assertEqual(record['feedback_status'], expected_status)
      self.assertIs(record['feedback_backoff_active'], backoff)
      self.assertEqual(record['heading_bias'], controller.diagnostics['heading_bias'])
      if backoff:
        # The output ceiling is observable separately from the stored integral.
        self.assertLess(record['heading_target'], record['heading_base'] + record['heading_bias'])

  def test_actual_ford_branch_uses_selected_reference_and_disables_invalid_output(self):
    source_path = Path(__file__).resolve().parents[1] / 'controlsd.py'
    source = ast.parse(source_path.read_text())
    controls_class = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Controls')
    state_control = next(n for n in controls_class.body if isinstance(n, ast.FunctionDef) and n.name == 'state_control')
    branch = next(n for n in state_control.body if isinstance(n, ast.If) and ast.unparse(n.test) == "self.CP.brand == 'ford'")
    code = compile(ast.Module(body=[branch], type_ignores=[]), str(source_path), 'exec')

    class Subscriptions:
      frame = 1  # periodic logging is covered separately
      valid = {'lateralManeuverPlan': False, 'modelV2': True, 'carStateSP': True}
      logMonoTime = {'carState': 995_000_000, 'modelV2': 980_000_000, 'lateralManeuverPlan': 990_000_000, 'carStateSP': 998_000_000}
      failed_checks = set()

      def __init__(self):
        self.state_sp = custom.CarStateSP.new_message()
        self.state_sp.fordPscmStatus = {'valid': True, 'canMonoTime': 970_000_000, 'lateralState': 2,
                                      'limit': 1, 'capability': 2, 'denied': False}

      def __getitem__(self, service):
        if service == 'carStateSP':
          return self.state_sp
        raise KeyError(service)

      def all_checks(self, services):
        return all(self.valid.get(service, True) and service not in self.failed_checks for service in services)

    for maneuver in (False, True):
      sm = Subscriptions()
      sm.valid = dict(sm.valid, lateralManeuverPlan=maneuver)
      controller = FordVirtualAngleController()
      controller.update = Mock(wraps=controller.update)
      controls = SimpleNamespace(CP=SimpleNamespace(brand='ford'), sm=sm, ford_virtual_angle=True, ford_path_controller=controller,
                                 desired_curvature=0.007, curvature=0.002, steer_limited_by_safety=True)
      cs = SimpleNamespace(vEgo=8.0, yawRate=-.015, canValid=True, steeringPressed=False, steeringTorque=.75)
      cc = SimpleNamespace(latActive=True)
      actuator = SimpleNamespace(curvature=0.007)
      environment = {'self': controls, 'CS': cs, 'CC': cc, 'actuators': actuator, 'model_v2': circle(.007),
                     'time': SimpleNamespace(monotonic=lambda: 1.0), 'PscmStatus': PscmStatus}
      exec(code, environment)
      self.assertTrue(controls.ford_path.valid)
      self.assertTrue(cc.latActive)
      self.assertIs(controller.update.call_args.args[0], environment['model_v2'])
      self.assertEqual(controller.update.call_args.args[1], controls.desired_curvature)
      args = controller.update.call_args.kwargs
      self.assertEqual(args['yaw_rate'], .015)
      self.assertEqual(args['steering_torque'], .75)
      status = args['pscm_status']
      self.assertAlmostEqual(status.timestamp, .97)
      self.assertEqual((status.lateral_state, status.limit, status.capability, status.denied, status.valid), (2, 1, 2, False, True))
      self.assertAlmostEqual(args['measurement_time'], 0.995)
      self.assertAlmostEqual(args['model_time'], 0.98)
      reference_service = 'lateralManeuverPlan' if maneuver else 'modelV2'
      self.assertAlmostEqual(args['reference_time'], sm.logMonoTime[reference_service] * 1e-9)
      self.assertEqual(actuator.curvature, 0.0)

      # C0 needs the selected action service; C1 independently needs modelV2.
      # Reject stale/failed selected services rather than silently fall back or
      # transmit an active zero path. A non-selected maneuver service is ignored.
      for stale_service in {reference_service, 'modelV2'}:
        with self.subTest(maneuver=maneuver, stale_service=stale_service):
          controller.reset()
          cc.latActive = True
          sm.logMonoTime = dict(Subscriptions.logMonoTime, **{stale_service: 500_000_000})
          exec(code, environment)
          self.assertFalse(controls.ford_path.valid)
          self.assertFalse(cc.latActive)
          self.assertIsNone(controller.reference.path)

      for failed_service in {reference_service, 'modelV2', 'carState', 'vehicleParameters'}:
        with self.subTest(maneuver=maneuver, failed_service=failed_service):
          controller.reset()
          cc.latActive = True
          sm.logMonoTime = Subscriptions.logMonoTime.copy()
          sm.failed_checks = {failed_service}
          exec(code, environment)
          self.assertFalse(controller.update.call_args.kwargs['valid'])
          self.assertFalse(controls.ford_path.valid)
          self.assertFalse(cc.latActive)
          self.assertIsNone(controller.reference.path)

      if not maneuver:
        controller.reset()
        cc.latActive = True
        sm.logMonoTime = dict(Subscriptions.logMonoTime, lateralManeuverPlan=500_000_000)
        sm.failed_checks = {'lateralManeuverPlan'}
        exec(code, environment)
        self.assertTrue(controls.ford_path.valid)
        self.assertTrue(cc.latActive)

      # A missing, stale or invalid optional PSCM status must not disable the
      # existing feedforward request. Feedback receives its own validity/age.
      for fault in ('service', 'missing', 'stale_can'):
        with self.subTest(maneuver=maneuver, pscm_fault=fault):
          controller.reset()
          cc.latActive = True
          sm.logMonoTime = Subscriptions.logMonoTime.copy()
          sm.failed_checks = {'carStateSP'} if fault == 'service' else set()
          sm.state_sp.fordPscmStatus.valid = fault != 'missing'
          sm.state_sp.fordPscmStatus.canMonoTime = 500_000_000 if fault == 'stale_can' else 970_000_000
          exec(code, environment)
          status = controller.update.call_args.kwargs['pscm_status']
          self.assertEqual(status.valid, fault == 'stale_can')
          self.assertAlmostEqual(status.timestamp, .5 if fault == 'stale_can' else .97)
          self.assertTrue(controller.update.call_args.kwargs['valid'])
          self.assertTrue(controls.ford_path.valid)
          self.assertTrue(cc.latActive)


if __name__ == '__main__':
  unittest.main()
