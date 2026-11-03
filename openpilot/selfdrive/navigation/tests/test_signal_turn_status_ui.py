"""Display-path tests without a window/GPU; execute the actual widget methods."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

import numpy as np

WORKTREE = Path(__file__).resolve().parents[4]
UI = WORKTREE/'openpilot/selfdrive/ui/mici/onroad'


class Label:
  def __init__(self, *args, **kwargs):
    self.text = ''

  def set_text(self, text):
    self.text = text

  def render(self, rect):
    pass


def load_widget(state):
  def rectangle(x, y, width, height):
    return SimpleNamespace(x=x, y=y, width=width, height=height)
  rl = SimpleNamespace(Color=lambda *args: args, WHITE='white', BLACK='black', Rectangle=rectangle,
                       Vector2=lambda x, y: (x, y), draw_rectangle_rec=Mock(), draw_line_ex=Mock(), draw_circle_v=Mock())
  namespace = {'__name__': 'navigation_ui_test', 'np': np, 'rl': rl, 'time': SimpleNamespace(monotonic=lambda: 100.),
               'Widget': object, 'UnifiedLabel': Label, 'gui_label': Mock(), 'ui_state': state,
               'VisionIpcClient': Mock(), 'VisionStreamType': SimpleNamespace(VISION_STREAM_MAP=1),
               'FontWeight': SimpleNamespace(BOLD=1, MEDIUM=2), 'TextAlignmentVertical': SimpleNamespace(TOP=1),
               'ROUTE_INTENSITY': 128, 'SIZE': 256, 'latest_gps_source': lambda sm: 'gps',
               'CONNECTION_RETRY_INTERVAL': 1., 'EGO': [128, 192], 'CV': SimpleNamespace()}
  tree = ast.parse((UI/'navigation.py').read_text())
  tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
  exec(compile(tree, str(UI/'navigation.py'), 'exec'), namespace)
  return SimpleNamespace(**namespace)


class SM:
  def __init__(self):
    self.valid, self.alive = {'navInstruction': True}, {'navInstruction': True}
    self.car = SimpleNamespace(leftBlinker=False, rightBlinker=True)
    self.instruction = SimpleNamespace(maneuverModifier='right', maneuverDistance=8., timeRemaining=20., distanceRemaining=100.)

  def __getitem__(self, key):
    return self.car if key == 'carState' else self.instruction


def state(status='unavailable', destination=False):
  values = {'MapboxNextTurnEnabled': True, 'MapboxTurnIntent': {'session': 'one', 'direction': 'right'},
            'MapboxTurnContext': {'session': 'one', 'direction': 'right', 'status': status, 'updatedAt': 100.,
                                  'reason': 'explicit_destination' if status == 'blocked' else 'gps_unavailable',
                                  'locationValid': status == 'ready', 'headingValid': status == 'ready',
                                  'distanceM': 8., 'name': 'Example Street', 'routeGeneration': 10}}
  params = SimpleNamespace(get=values.get, get_bool=lambda key: values.get(key) is True)
  return SimpleNamespace(sm=SM(), params=params, nav_destination_set=destination, navigation_enabled=True, is_metric=True), values


class TestSignalTurnStatus(unittest.TestCase):
  def test_all_pending_states_are_visible_and_ready_is_separate(self):
    for status, text in [('searching', 'Finding next right'), ('unavailable', 'Map turn unavailable'),
                         ('passed', 'Turn passed'), ('blocked', 'Signal turn blocked')]:
      ui_state, _ = state(status)
      module = load_widget(ui_state)
      widget = module.NavigationPanel()
      self.assertTrue(widget.signal_turn_active)
      self.assertEqual(widget.signal_status['primary'], text)
      widget._render(module.rl.Rectangle(0, 0, 261, 400))
      module.rl.draw_line_ex.assert_not_called()
      self.assertTrue(any(call.args[1] == text for call in module.gui_label.call_args_list))

  def test_ready_has_direction_arrow_and_explicit_signal_label(self):
    ui_state, _ = state('ready')
    module = load_widget(ui_state)
    widget = module.NavigationPanel()
    widget._render(module.rl.Rectangle(0, 0, 261, 400))
    self.assertGreater(module.rl.draw_line_ex.call_count, 0)
    self.assertIn('Route ready', widget._eta_label.text)

  def test_route_preview_is_not_navigation_active_without_fresh_model_consumption(self):
    ui_state, values = state('ready')
    for value in (None, {'updatedAt': 99., 'supported': True, 'active': True, 'session': 'one'},
                  {'updatedAt': 100., 'supported': True, 'active': True, 'session': 'old'},
                  {'updatedAt': 100., 'supported': False, 'active': False, 'session': 'one'}):
      values['NavModelState'] = value
      widget = load_widget(ui_state).NavigationPanel()
      self.assertEqual(widget.signal_status['primary'], 'Route ready')
    values['NavModelState'] = {'updatedAt': 100., 'supported': True, 'active': True, 'session': 'one', 'routeGeneration': 10}
    widget = load_widget(ui_state).NavigationPanel()
    self.assertEqual(widget.signal_status['primary'], 'Navigation active')

  def test_explicit_destination_keeps_normal_arrow_and_shows_blocked_footer(self):
    ui_state, _ = state('blocked', destination=True)
    module = load_widget(ui_state)
    widget = module.NavigationPanel()
    widget._render(module.rl.Rectangle(0, 0, 261, 400))
    self.assertGreater(module.rl.draw_line_ex.call_count, 0)
    self.assertIn('Destination navigation active', widget._eta_label.text)

  def test_pending_candidate_does_not_claim_navigation_is_active(self):
    ui_state, values = state('ready')
    values['MapboxTurnIntent']['mode'] = 'pending'
    self.assertEqual(load_widget(ui_state).NavigationPanel().signal_status['primary'], 'Turn candidate')

  def test_lane_change_holds_prepared_route_without_claiming_navigation(self):
    ui_state, values = state('ready')
    values['MapboxTurnIntent']['mode'] = 'lane_change'
    status = load_widget(ui_state).NavigationPanel().signal_status
    self.assertEqual(status['primary'], 'Lane change')
    self.assertEqual(status['state'], 'lane_change')

  def test_actual_destination_owned_context_has_priority_without_a_signal_session(self):
    ui_state, values = state('ready', destination=True)
    values['MapboxTurnContext'] = {'status': 'ready', 'updatedAt': 100., 'routeOwner': 'destination', 'routeGeneration': 20}
    widget = load_widget(ui_state).NavigationPanel()
    self.assertEqual(widget.signal_status['secondary'], 'Destination navigation active')

  def test_retained_exit_guidance_remains_visible_after_auto_cancel(self):
    ui_state, values = state('ready')
    ui_state.sm.car.rightBlinker = False
    values['MapboxTurnIntent'] = None
    values['MapboxTurnContext']['retainedAfterSignalCancel'] = True
    widget = load_widget(ui_state).NavigationPanel()
    self.assertTrue(widget.signal_turn_active)
    ui_state.sm.car.leftBlinker = True
    self.assertFalse(load_widget(ui_state).NavigationPanel().signal_turn_active)

  def test_cancel_disable_hazards_stale_or_wrong_session_does_not_claim_ready(self):
    for update in ('off', 'cancel', 'hazards', 'stale', 'different_session'):
      ui_state, values = state('ready')
      if update == 'off':
        values['MapboxNextTurnEnabled'] = False
      elif update == 'cancel':
        ui_state.sm.car.rightBlinker = False
      elif update == 'hazards':
        ui_state.sm.car.leftBlinker = True
      elif update == 'stale':
        values['MapboxTurnContext']['updatedAt'] = 99.
      else:
        values['MapboxTurnContext']['session'] = 'old'
      widget = load_widget(ui_state).NavigationPanel()
      if update in ('off', 'cancel', 'hazards'):
        self.assertFalse(widget.signal_turn_active)
      else:
        self.assertEqual(widget.signal_status['state'], 'unavailable')

  def test_augmented_view_opens_for_signal_without_destination_and_yields_to_alert(self):
    tree = ast.parse((UI/'augmented_road_view.py').read_text())
    assignment = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign) and
                      any(isinstance(target, ast.Name) and target.id == 'show_navigation' for target in node.targets))
    code = compile(ast.Expression(assignment.value), 'actual_navigation_visibility', 'eval')
    for enabled, destination, signal, alert, expected in [(True, False, True, None, True),
        (True, False, False, None, False), (False, False, True, None, False),
        (True, True, False, None, True), (True, False, True, object(), False)]:
      result = eval(code, {'ui_state': SimpleNamespace(navigation_enabled=enabled, nav_destination_set=destination),
                           'self': SimpleNamespace(_navigation=SimpleNamespace(signal_turn_active=signal)), 'alert_to_render': alert})
      self.assertEqual(result, expected)


if __name__ == '__main__':
  unittest.main()
