import ast
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.common.logging_extra import SwagFormatter, SwagLogger
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController
from openpilot.selfdrive.controls.lib.ford_path import FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.tests.test_ford_model_action import circle


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
    for controller in (FordPathController(), FordPscmObserverPathController(), FordModelActionController()):
      with self.subTest(controller=type(controller).__name__):
        record = self.emit_controls_event('Ford path controller selected', SimpleNamespace(ford_path_controller=controller))
        self.assertEqual(record['controller'], type(controller).__name__)

  def test_candidate_diagnostics_identify_the_experiment_and_do_not_claim_calibration(self):
    controller = FordModelActionController()
    for active, valid in ((False, True), (True, True), (True, False)):
      controller.update(circle(.01), .005, yaw_rate=.05, speed=20., now=1.,
                        measurement_time=1., model_time=1., reference_time=1., active=active, valid=valid)
      controls = SimpleNamespace(ford_path_controller=controller, desired_curvature=.005, curvature=.0025,
                                 sm=SimpleNamespace(logMonoTime={'modelV2': 123456789, 'carState': 123450000}))
      record = self.emit_controls_event('Ford C2-free path tracking', controls)
      self.assertEqual(record['hypothesis'], 'model-action-c0-c1-v1')
      self.assertIs(record['calibration_approved'], False)
      self.assertEqual(record['command'][2:], [0., 0.])
      self.assertEqual(record['status'], controller.diagnostics['status'])
