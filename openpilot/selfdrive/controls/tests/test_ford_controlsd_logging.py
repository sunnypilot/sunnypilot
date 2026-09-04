import ast
import io
import json
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest

from openpilot.common.logging_extra import SwagFormatter, SwagLogger
from openpilot.selfdrive.controls.lib.ford_path import FordPathController, FordPscmObserverPathController
from openpilot.selfdrive.controls.lib.ford_shared_path import FordSharedPathController


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
      eval(compile(expression, str(source_path), 'eval'), {'cloudlog': logger, 'self': controls})
      record = json.loads(stream.getvalue())
    finally:
      handler.close()
    self.assertEqual(record['level'], 'INFO')
    self.assertEqual(record['msg']['event'], event)
    return record['msg']

  def test_startup_logs_selected_controller_without_crashing(self):
    for controller in (FordPathController(), FordPscmObserverPathController(), FordSharedPathController()):
      with self.subTest(controller=type(controller).__name__):
        record = self.emit_controls_event('Ford path controller selected', SimpleNamespace(ford_path_controller=controller))
        self.assertEqual(record['controller'], type(controller).__name__)

  def test_periodic_diagnostics_log_without_crashing(self):
    controller = FordSharedPathController()
    for active in (False, True):
      controller.update(None, 0.0, active=active)
      controls = SimpleNamespace(ford_path_controller=controller, sm=SimpleNamespace(logMonoTime={'modelV2': 123456789}))
      record = self.emit_controls_event('Ford shared path experiment', controls)
      self.assertEqual(record['model_mono_time'], 123456789)
      self.assertEqual(record['status'], controller.diagnostics['status'])
      self.assertEqual(record['command'], list(controller.diagnostics['command']))
      self.assertEqual(record['horizon_s'], controller.diagnostics['horizon_s'])

  def test_temporal_model_pose_diagnostics_log_and_clear(self):
    controller = FordSharedPathController()
    model = SimpleNamespace(position=SimpleNamespace(t=[0.0, 2.0], x=[0.0, 20.0], y=[0.0, -10.0]),
                            orientation=SimpleNamespace(z=[0.0, -1.0]))
    controller.update(model, 0.0, current_curvature=-0.019, v_ego=2.1, v_ego_raw=2.1)
    controls = SimpleNamespace(ford_path_controller=controller, sm=SimpleNamespace(logMonoTime={'modelV2': 123456789}))
    record = self.emit_controls_event('Ford shared path experiment', controls)
    self.assertEqual(record['model_offset'], controller.diagnostics['model_offset'])
    self.assertEqual(record['model_heading'], controller.diagnostics['model_heading'])
    self.assertEqual(record['predicted_heading'], controller.diagnostics['predicted_heading'])
    self.assertEqual(record['heading_residual'], controller.diagnostics['heading_residual'])
    self.assertEqual(record['arc'], controller.diagnostics['arc'])
    self.assertEqual(record['command'], list(controller.diagnostics['command']))

    for active in (True, False):
      controller.update(None, 0.0, active=active)
      record = self.emit_controls_event('Ford shared path experiment', controls)
      self.assertIsNone(record['model_offset'])
      self.assertIsNone(record['heading_residual'])


if __name__ == '__main__':
  unittest.main()
