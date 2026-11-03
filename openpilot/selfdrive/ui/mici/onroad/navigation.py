import numpy as np
import pyray as rl
import time

from msgq.visionipc import VisionIpcClient
from openpilot.cereal.visionipc import VisionStreamType
from openpilot.common.constants import CV
from openpilot.selfdrive.navigation.helpers import latest_gps_source
from openpilot.selfdrive.navigation.renderer import EGO, ROUTE_INTENSITY, SIZE
from openpilot.selfdrive.ui.mici.onroad.cameraview import CONNECTION_RETRY_INTERVAL
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import FontWeight, TextAlignmentVertical
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets.label import UnifiedLabel, gui_label

PANEL_WIDTH = 261
STALE_SECONDS = 3
MARKER_MARGIN = 18  # pixels kept below the ego so its marker stays visible

# Recolor the model's grayscale frame for people: dim the white roads and make the grey route pop. Only the route's
# exact level (and its neighbors) is recolored, so antialiased road edges passing through that grey stay grey.
MAP_COLORS = np.repeat(np.round(np.arange(256) * 0.45).astype(np.uint8)[:, None], 3, axis=1)
MAP_COLORS[ROUTE_INTENSITY - 1:ROUTE_INTENSITY + 2] = (72, 235, 132)


def signal_turn_status(enabled, intent, context, now, left_blinker, right_blinker, model_state=None):
  """Distinguish a route lookup from actual navigation inputs consumed by the model."""
  direction = 'left' if left_blinker and not right_blinker else 'right' if right_blinker and not left_blinker else None
  if (direction is None and not left_blinker and not right_blinker and isinstance(context, dict) and
      context.get('retainedAfterSignalCancel') is True and context.get('status') == 'ready'):
    # Auto-cancel during an entered turn does not end its short exit guidance.
    direction = context.get('direction')
    intent = {'session': context.get('session'), 'direction': direction}
  if (enabled is not True or not isinstance(intent, dict) or not intent.get('session') or
      direction not in ('left', 'right') or intent.get('direction') != direction):
    return None
  status, reason = 'unavailable', 'navigation_unavailable'
  if isinstance(context, dict) and context.get('routeOwner') == 'destination':
    return {'state': 'blocked', 'primary': 'Signal turn blocked', 'secondary': 'Destination navigation active'}
  if intent.get('mode') == 'lane_change':
    return {'state': 'lane_change', 'primary': 'Lane change', 'secondary': 'Street route on hold'}
  if isinstance(context, dict) and context.get('session') == intent['session'] and context.get('direction') == direction:
    updated = context.get('updatedAt')
    if isinstance(updated, (int, float)) and not isinstance(updated, bool) and np.isfinite(updated) and 0. <= now-updated <= .35:
      status, reason = context.get('status'), context.get('reason')
  if status == 'ready' and context.get('locationValid') is True and context.get('headingValid') is True:
    distance = context.get('distanceM')
    if isinstance(distance, (int, float)) and not isinstance(distance, bool) and np.isfinite(distance):
      model_updated = model_state.get('updatedAt') if isinstance(model_state, dict) else None
      active = (isinstance(model_updated, (int, float)) and not isinstance(model_updated, bool) and
                np.isfinite(model_updated) and 0. <= now-model_updated <= .5 and
                model_state.get('supported') is True and model_state.get('active') is True and
                model_state.get('session') == intent['session'] and
                isinstance(context.get('routeGeneration'), int) and context['routeGeneration'] > 0 and
                model_state.get('routeGeneration') == context['routeGeneration'])
      pending = intent.get('mode') == 'pending'
      return {'state': 'ready', 'primary': 'Turn candidate' if pending else 'Navigation active' if active else 'Route ready',
              'direction': direction, 'distanceM': distance,
              'secondary': (f"{direction.capitalize()} onto {context.get('name', '')}".strip() if active or pending else 'Waiting for map and model')}
  if status == 'searching':
    return {'state': status, 'primary': f'Finding next {direction}', 'secondary': 'Checking mapped streets'}
  if status == 'passed':
    return {'state': status, 'primary': 'Turn passed', 'secondary': 'Signal again for another turn'}
  if status == 'blocked':
    return {'state': status, 'primary': 'Signal turn blocked',
            'secondary': 'Destination navigation active' if reason == 'explicit_destination' else 'Signal changed'}
  explanations = {'missing_token': 'Map token missing', 'invalid_token': 'Map token unavailable',
                  'navigation_model_required': 'Select a navigation-capable model',
                  'gps_unavailable': 'GPS position unavailable', 'gps_or_car_state_invalid': 'GPS position unavailable',
                  'heading_unavailable': 'Vehicle heading unavailable', 'navigation_unavailable': 'Waiting for navigation',
                  'target_expired': 'Signal again to refresh target', 'no_matching_turn': 'No supported street turn ahead',
                  'ambiguous_approach': 'Approach is uncertain', 'approach_location_mismatch': 'Position does not match approach',
                  'approach_heading_mismatch': 'Heading does not match approach'}
  return {'state': 'unavailable', 'primary': 'Map turn unavailable', 'secondary': explanations.get(reason, 'Map lookup unavailable')}


def format_distance(meters: float) -> str:
  """m / ft under 1000 m / 300 m, km / mi beyond."""
  if ui_state.is_metric:
    return f'{round(meters / 10) * 10} m' if meters < 1000 else f'{meters / 1000:.1f} km'
  return f'{round(meters * CV.METER_TO_FOOT / 50) * 50} ft' if meters < 300 else f'{meters * CV.METER_TO_MILE:.1f} mi'


class NavigationPanel(Widget):
  """Turn instructions around the map frames mapsd publishes for the model."""

  def __init__(self):
    super().__init__()
    self._client = VisionIpcClient('mapsd', VisionStreamType.VISION_STREAM_MAP, True)
    self._last_connect = 0.0
    self._frame_time = 0.0
    self._texture = None
    self._eta_label = UnifiedLabel('', 34, FontWeight.BOLD, rl.WHITE, scroll=True)
    self._accent = rl.Color(155, 230, 185, 255)
    self._muted = rl.Color(162, 175, 185, 255)
    self._signal_status = None
    self._last_signal_poll = -np.inf

  @property
  def signal_status(self):
    now = time.monotonic()
    if now-self._last_signal_poll >= .1:
      self._last_signal_poll = now
      car = ui_state.sm['carState']
      self._signal_status = signal_turn_status(
        ui_state.params.get_bool('MapboxNextTurnEnabled'), ui_state.params.get('MapboxTurnIntent'),
        ui_state.params.get('MapboxTurnContext'), now, car.leftBlinker, car.rightBlinker,
        ui_state.params.get('NavModelState'))
    return self._signal_status

  @property
  def signal_turn_active(self):
    return self.signal_status is not None

  def _update_state(self):
    if not self._client.is_connected():
      if rl.get_time() - self._last_connect < CONNECTION_RETRY_INTERVAL:
        return
      self._last_connect = rl.get_time()
      if not self._client.connect(False) or not self._client.num_buffers:
        return
      self._unload_texture()
      self._texture = rl.load_texture_from_image(rl.Image(None, SIZE, SIZE, 1, rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8))
    frame = self._client.recv(timeout_ms=0)
    if frame is not None:
      gray = np.frombuffer(frame.data, dtype=np.uint8, count=SIZE * SIZE)
      rl.update_texture(self._texture, rl.ffi.cast("void *", rl.ffi.from_buffer(MAP_COLORS[gray])))
      # Without a usable map, mapsd publishes black frames with a zero timestamp.
      self._frame_time = rl.get_time() if self._client.timestamp_sof else 0.0

  @property
  def routing(self):
    return ui_state.sm.valid['navInstruction'] and ui_state.sm.alive['navInstruction']

  @property
  def map_ready(self):
    return self._texture is not None and 0 <= rl.get_time() - self._frame_time < STALE_SECONDS

  def _draw_status(self, rect):
    """What the map is waiting on, in place of the map."""
    statuses = (
      ('GPS fix', latest_gps_source(ui_state.sm) is not None),
      ('Route', self.routing),
      ('Map frames', self.map_ready),
    )
    for i, (name, ok) in enumerate(statuses):
      gui_label(rl.Rectangle(rect.x + 10, rect.y + 12 + i * 28, rect.width - 20, 26), f'{name}: {"yes" if ok else "no"}', 22,
                self._accent if ok else self._muted, FontWeight.MEDIUM, alignment_vertical=TextAlignmentVertical.TOP)

  def _render(self, rect):
    x, y = rect.x, rect.y
    rl.draw_rectangle_rec(rect, rl.Color(7, 13, 18, 255))
    instruction = ui_state.sm['navInstruction']
    signal = self.signal_status
    signal_ready = signal is not None and signal['state'] == 'ready' and not ui_state.nav_destination_set
    notification = signal is not None and signal['state'] != 'ready' and not ui_state.nav_destination_set
    if notification:
      gui_label(rl.Rectangle(x+12, y+18, rect.width-24, 30), signal['primary'], 22, rl.WHITE, FontWeight.BOLD,
                alignment_vertical=TextAlignmentVertical.TOP)
    elif self.routing or signal_ready:
      direction = signal['direction'] if signal_ready else instruction.maneuverModifier
      flip = -1 if 'left' in direction else 1
      # The maneuver arrow on a 1.4x grid, centered in the header's icon box, with round joins for the thick stroke.
      if direction in ('straight', ''):
        shape = [(0, 14), (0, -12), (-6, -5), (0, -12), (6, -5)]
      else:
        shape = [(-flip*9, 14), (-flip*9, -4), (-flip*2, -9), (flip*9, -9), (flip*3, -15), (flip*9, -9), (flip*3, -3)]
      points = [rl.Vector2(x + 31 + 1.4*px, y + 30 + 1.4*py) for px, py in shape]
      for a, b in zip(points[:-1], points[1:], strict=True):
        rl.draw_line_ex(a, b, 7, self._accent)
      for point in points:
        rl.draw_circle_v(point, 3.5, self._accent)
      distance = signal['distanceM'] if signal_ready else instruction.maneuverDistance
      gui_label(rl.Rectangle(x+64, y+11, rect.width-72, 40), format_distance(max(0, distance)), 34, rl.WHITE, FontWeight.BOLD,
                alignment_vertical=TextAlignmentVertical.TOP)
    else:
      gui_label(rl.Rectangle(x+12, y+18, rect.width-24, 30), 'Waiting for route', 26, rl.WHITE, FontWeight.BOLD,
                alignment_vertical=TextAlignmentVertical.TOP)
    map_rect = rl.Rectangle(x+8, y+61, rect.width-16, rect.height-111)
    rl.draw_rectangle_rec(map_rect, rl.BLACK)
    if notification:
      gui_label(rl.Rectangle(map_rect.x+10, map_rect.y+16, map_rect.width-20, 80), signal['secondary'], 24, self._muted,
                FontWeight.MEDIUM, alignment_vertical=TextAlignmentVertical.TOP)
    elif self.map_ready:
      # A 1:1 crop of the model's frame, centered horizontally with the ego near the bottom.
      width, height = min(map_rect.width, SIZE), min(map_rect.height, SIZE)
      source = rl.Rectangle((SIZE - width) // 2, min(SIZE - height, max(0, EGO[1] + MARKER_MARGIN - height)), width, height)
      target = rl.Rectangle(map_rect.x + (map_rect.width - width) / 2, map_rect.y + map_rect.height - height, width, height)
      rl.draw_texture_pro(self._texture, source, target, rl.Vector2(0, 0), 0, rl.WHITE)
    else:
      self._draw_status(map_rect)
    if signal is not None and (notification or ui_state.nav_destination_set):
      self._eta_label.set_text(f"{signal['primary']}: {signal['secondary']}")
      self._eta_label.render(rl.Rectangle(x+9, y+rect.height-45, rect.width-18, 40))
    elif self.routing or signal_ready:
      seconds = max(0, instruction.timeRemaining)
      remaining = max(0, instruction.distanceRemaining)
      self._eta_label.set_text(f"{signal['primary']}: {signal['secondary']}" if signal is not None else
                               f'{max(1, round(seconds / 60))} min / {format_distance(remaining)}')
      self._eta_label.render(rl.Rectangle(x+9, y+rect.height-45, rect.width-18, 40))

  def _unload_texture(self):
    if self._texture:
      rl.unload_texture(self._texture)
      self._texture = None

  def close(self):
    self._unload_texture()
