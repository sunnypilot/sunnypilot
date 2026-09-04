import ast
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from openpilot.common.logging_extra import SwagFormatter, SwagLogger
from openpilot.selfdrive.controls.lib.ford_path import FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_virtual_angle import FordVirtualAngleController


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
    for active in (False, True):
      controller.update(0.01, current_curvature=0.005, speed=10.0, now=1.0,
                        measurement_time=1.0, reference_time=1.0, active=active)
      controls = SimpleNamespace(ford_path_controller=controller, sm=SimpleNamespace(logMonoTime={'modelV2': 123456789, 'carState': 123450000}))
      record = self.emit_controls_event('Ford virtual angle experiment', controls)
      self.assertEqual(record['model_mono_time'], 123456789)
      self.assertEqual(record['reference_mono_time'], 123456789)
      self.assertEqual(record['measurement_mono_time'], 123450000)
      self.assertEqual(record['status'], controller.diagnostics['status'])
      self.assertEqual(record['command'], list(controller.diagnostics['command']))
      if active:
        self.assertEqual(record['response_delay'], 0.2)
        self.assertEqual(record['reference'], 0.01)
        self.assertEqual(record['measured'], 0.005)
        self.assertTrue(all(key in record for key in ('p', 'i', 'd', 'pending_feedback', 'integrator_frozen')))

  def test_actual_ford_branch_uses_selected_reference_and_disables_invalid_output(self):
    source_path = Path(__file__).resolve().parents[1] / 'controlsd.py'
    source = ast.parse(source_path.read_text())
    controls_class = next(n for n in source.body if isinstance(n, ast.ClassDef) and n.name == 'Controls')
    state_control = next(n for n in controls_class.body if isinstance(n, ast.FunctionDef) and n.name == 'state_control')
    branch = next(n for n in state_control.body if isinstance(n, ast.If) and ast.unparse(n.test) == "self.CP.brand == 'ford'")
    code = compile(ast.Module(body=[branch], type_ignores=[]), str(source_path), 'exec')

    class Subscriptions:
      frame = 1  # periodic logging is covered separately
      valid = {'lateralManeuverPlan': False, 'modelV2': True}
      logMonoTime = {'carState': 995_000_000, 'modelV2': 980_000_000, 'lateralManeuverPlan': 990_000_000}

      def all_checks(self, services):
        return all(self.valid.get(service, True) for service in services)

    for maneuver in (False, True):
      sm = Subscriptions()
      sm.valid = dict(sm.valid, lateralManeuverPlan=maneuver)
      controller = FordVirtualAngleController()
      controller.update = Mock(wraps=controller.update)
      controls = SimpleNamespace(CP=SimpleNamespace(brand='ford'), sm=sm, ford_virtual_angle=True, ford_path_controller=controller,
                                 desired_curvature=0.007, curvature=0.002, steer_limited_by_safety=True)
      cs = SimpleNamespace(vEgo=8.0, canValid=True, steeringPressed=False)
      cc = SimpleNamespace(latActive=True)
      actuator = SimpleNamespace(curvature=0.007)
      environment = {'self': controls, 'CS': cs, 'CC': cc, 'actuators': actuator, 'model_v2': object(),
                     'time': SimpleNamespace(monotonic=lambda: 1.0)}
      exec(code, environment)
      self.assertTrue(controls.ford_path.valid)
      self.assertTrue(cc.latActive)
      self.assertEqual(controller.update.call_args.args, (0.007,))
      args = controller.update.call_args.kwargs
      self.assertEqual(args['current_curvature'], 0.002)
      self.assertAlmostEqual(args['measurement_time'], 0.995)
      self.assertAlmostEqual(args['reference_time'], 0.99 if maneuver else 0.98)
      self.assertTrue(args['limited'])
      self.assertEqual(actuator.curvature, 0.0)
      self.assertTrue(controller.diagnostics['integrator_frozen'])

      # A stale selected reference must cancel the transmitted lateral request,
      # rather than send an active zero path or silently switch controllers.
      sm.logMonoTime = dict(sm.logMonoTime, **{'lateralManeuverPlan' if maneuver else 'modelV2': 500_000_000})
      exec(code, environment)
      self.assertFalse(controls.ford_path.valid)
      self.assertFalse(cc.latActive)
      self.assertFalse(controller.history)


if __name__ == '__main__':
  unittest.main()
