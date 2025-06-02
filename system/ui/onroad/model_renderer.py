import colorsys
import numpy as np
import pyray as rl
from cereal import messaging, car
from dataclasses import dataclass, field
from openpilot.common.params import Params
from openpilot.system.ui.lib.application import DEFAULT_FPS
from openpilot.system.ui.lib.shader_polygon import draw_polygon


CLIP_MARGIN = 500
MIN_DRAW_DISTANCE = 10.0
MAX_DRAW_DISTANCE = 100.0
PATH_COLOR_TRANSITION_DURATION = 0.5  # Seconds for color transition animation
PATH_BLEND_INCREMENT = 1.0 / (PATH_COLOR_TRANSITION_DURATION * DEFAULT_FPS)

THROTTLE_COLORS = [
  rl.Color(13, 248, 122, 102),   # HSLF(148/360, 0.94, 0.51, 0.4)
  rl.Color(114, 255, 92, 89),    # HSLF(112/360, 1.0, 0.68, 0.35)
  rl.Color(114, 255, 92, 0),     # HSLF(112/360, 1.0, 0.68, 0.0)
]

NO_THROTTLE_COLORS = [
  rl.Color(242, 242, 242, 102), # HSLF(148/360, 0.0, 0.95, 0.4)
  rl.Color(242, 242, 242, 89),  # HSLF(112/360, 0.0, 0.95, 0.35)
  rl.Color(242, 242, 242, 0),   # HSLF(112/360, 0.0, 0.95, 0.0)
]


@dataclass
class ModelPoints:
  raw_points: np.ndarray = field(default_factory=lambda: np.empty((0, 3), dtype=np.float32))
  projected_points: np.ndarray = field(default_factory=lambda: np.empty((0, 2), dtype=np.float32))

@dataclass
class LeadVehicle:
  glow: list[float] = field(default_factory=list)
  chevron: list[float] = field(default_factory=list)
  fill_alpha: int = 0


class ModelRenderer:
  def __init__(self):
    self._longitudinal_control = False
    self._experimental_mode = False
    self._blend_factor = 1.0
    self._prev_allow_throttle = True
    self._lane_line_probs = np.zeros(4, dtype=np.float32)
    self._road_edge_stds = np.zeros(2, dtype=np.float32)
    self._lead_vehicles = [LeadVehicle(), LeadVehicle()]
    self._path_offset_z = 1.22

    # Initialize ModelPoints objects
    self._path = ModelPoints()
    self._lane_lines = [ModelPoints() for _ in range(4)]
    self._road_edges = [ModelPoints() for _ in range(2)]
    self._acceleration_x = np.empty((0,), dtype=np.float32)

    # Transform matrix (3x3 for car space to screen space)
    self._car_space_transform = np.zeros((3, 3), dtype=np.float32)
    self._transform_dirty = True
    self._clip_region = None
    self._rect = None
    self._exp_gradient = {
      'start': (0.0, 1.0),  # Bottom of path
      'end': (0.0, 0.0),  # Top of path
      'colors': [],
      'stops': [],
    }

    # Get longitudinal control setting from car parameters
    if car_params := Params().get("CarParams"):
      cp = messaging.log_from_bytes(car_params, car.CarParams)
      self._longitudinal_control = cp.openpilotLongitudinalControl

  def set_transform(self, transform: np.ndarray):
    self._car_space_transform = transform.astype(np.float32)
    self._transform_dirty = True

  def draw(self, rect: rl.Rectangle, sm: messaging.SubMaster):
    # Check if data is up-to-date
    if not sm.valid['modelV2'] or not sm.valid['liveCalibration']:
      return

    # Set up clipping region
    self._rect = rect
    self._clip_region = rl.Rectangle(
      rect.x - CLIP_MARGIN, rect.y - CLIP_MARGIN, rect.width + 2 * CLIP_MARGIN, rect.height + 2 * CLIP_MARGIN
    )

    # Update state
    self._experimental_mode = sm['selfdriveState'].experimentalMode
    self._path_offset_z = sm['liveCalibration'].height[0]
    if sm.updated['carParams']:
      self._longitudinal_control = sm['carParams'].openpilotLongitudinalControl

    model = sm['modelV2']
    radar_state = sm['radarState'] if sm.valid['radarState'] else None
    lead_one = radar_state.leadOne if radar_state else None
    render_lead_indicator = self._longitudinal_control and radar_state is not None

    # Update model data when needed
    model_updated = sm.updated['modelV2']
    if model_updated or sm.updated['radarState'] or self._transform_dirty:
      if model_updated:
        self._update_raw_points(model)

      pos_x_array = self._path.raw_points[:, 0]
      if pos_x_array.size == 0:
        return

      self._update_model(lead_one, pos_x_array)
      if render_lead_indicator:
        self._update_leads(radar_state, pos_x_array)
      self._transform_dirty = False


    # Draw elements
    self._draw_lane_lines()
    self._draw_path(sm)

    if render_lead_indicator and radar_state:
      self._draw_lead_indicator()

  def _update_raw_points(self, model):
    """Update raw 3D points from model data"""
    self._path.raw_points = np.array([model.position.x, model.position.y, model.position.z], dtype=np.float32).T

    for i, lane_line in enumerate(model.laneLines):
      self._lane_lines[i].raw_points = np.array([lane_line.x, lane_line.y, lane_line.z], dtype=np.float32).T

    for i, road_edge in enumerate(model.roadEdges):
      self._road_edges[i].raw_points = np.array([road_edge.x, road_edge.y, road_edge.z], dtype=np.float32).T

    self._lane_line_probs = np.array(model.laneLineProbs, dtype=np.float32)
    self._road_edge_stds = np.array(model.roadEdgeStds, dtype=np.float32)
    self._acceleration_x = np.array(model.acceleration.x, dtype=np.float32)

  def _update_leads(self, radar_state, pos_x_array):
    """Update positions of lead vehicles"""
    self._lead_vehicles = [LeadVehicle(), LeadVehicle()]
    leads = [radar_state.leadOne, radar_state.leadTwo]
    for i, lead_data in enumerate(leads):
      if lead_data and lead_data.status:
        d_rel, y_rel, v_rel = lead_data.dRel, lead_data.yRel, lead_data.vRel
        idx = self._get_path_length_idx(pos_x_array, d_rel)
        z = self._path.raw_points[idx, 2] if idx < len(self._path.raw_points) else 0.0
        point = self._map_to_screen(d_rel, -y_rel, z + self._path_offset_z)
        if point:
          self._lead_vehicles[i] = self._update_lead_vehicle(d_rel, v_rel, point, self._rect)

  def _update_model(self, lead, pos_x_array):
    """Update model visualization data based on model message"""
    max_distance = np.clip(pos_x_array[-1], MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE)
    max_idx = self._get_path_length_idx(pos_x_array, max_distance)

    # Update lane lines using raw points
    for i, lane_line in enumerate(self._lane_lines):
      lane_line.projected_points = self._map_line_to_polygon(
        lane_line.raw_points, 0.025 * self._lane_line_probs[i], 0.0, max_idx
      )

    # Update road edges using raw points
    for road_edge in self._road_edges:
      road_edge.projected_points = self._map_line_to_polygon(road_edge.raw_points, 0.025, 0.0, max_idx)

    # Update path using raw points
    if lead and lead.status:
      lead_d = lead.dRel * 2.0
      max_distance = np.clip(lead_d - min(lead_d * 0.35, 10.0), 0.0, max_distance)
      max_idx = self._get_path_length_idx(pos_x_array, max_distance)

    self._path.projected_points = self._map_line_to_polygon(
      self._path.raw_points, 0.9, self._path_offset_z, max_idx, allow_invert=False
    )

    self._update_experimental_gradient(self._rect.height)

  def _update_experimental_gradient(self, height):
    """Pre-calculate experimental mode gradient colors"""
    if not self._experimental_mode:
      return

    max_len = min(len(self._path.projected_points) // 2, len(self._acceleration_x))

    segment_colors = []
    gradient_stops = []

    i = 0
    while i < max_len:
      track_idx = max_len - i - 1  # flip idx to start from bottom right
      track_y = self._path.projected_points[track_idx][1]
      if track_y < 0 or track_y > height:
        i += 1
        continue

      # Calculate color based on acceleration
      lin_grad_point = (height - track_y) / height

      # speed up: 120, slow down: 0
      path_hue = max(min(60 + self._acceleration_x[i] * 35, 120), 0)
      path_hue = int(path_hue * 100 + 0.5) / 100

      saturation = min(abs(self._acceleration_x[i] * 1.5), 1)
      lightness = self._map_val(saturation, 0.0, 1.0, 0.95, 0.62)
      alpha = self._map_val(lin_grad_point, 0.75 / 2.0, 0.75, 0.4, 0.0)

      # Use HSL to RGB conversion
      color = self._hsla_to_color(path_hue / 360.0, saturation, lightness, alpha)

      gradient_stops.append(lin_grad_point)
      segment_colors.append(color)

      # Skip a point, unless next is last
      i += 1 + (1 if (i + 2) < max_len else 0)

    # Store the gradient in the path object
    self._exp_gradient['colors'] = segment_colors
    self._exp_gradient['stops'] = gradient_stops

  def _update_lead_vehicle(self, d_rel, v_rel, point, rect):
    speed_buff, lead_buff = 10.0, 40.0

    # Calculate fill alpha
    fill_alpha = 0
    if d_rel < lead_buff:
      fill_alpha = 255 * (1.0 - (d_rel / lead_buff))
      if v_rel < 0:
        fill_alpha += 255 * (-1 * (v_rel / speed_buff))
      fill_alpha = min(fill_alpha, 255)

    # Calculate size and position
    sz = np.clip((25 * 30) / (d_rel / 3 + 30), 15.0, 30.0) * 2.35
    x = np.clip(point[0], 0.0, rect.width - sz / 2)
    y = min(point[1], rect.height - sz * 0.6)

    g_xo = sz / 5
    g_yo = sz / 10

    glow = [(x + (sz * 1.35) + g_xo, y + sz + g_yo), (x, y - g_yo), (x - (sz * 1.35) - g_xo, y + sz + g_yo)]
    chevron = [(x + (sz * 1.25), y + sz), (x, y), (x - (sz * 1.25), y + sz)]

    return LeadVehicle(glow=glow,chevron=chevron, fill_alpha=int(fill_alpha))

  def _draw_lane_lines(self):
    """Draw lane lines and road edges"""
    for i, lane_line in enumerate(self._lane_lines):
      if lane_line.projected_points.size == 0:
        continue

      alpha = np.clip(self._lane_line_probs[i], 0.0, 0.7)
      color = rl.Color(255, 255, 255, int(alpha * 255))
      draw_polygon(self._rect, lane_line.projected_points, color)

    for i, road_edge in enumerate(self._road_edges):
      if road_edge.projected_points.size == 0:
        continue

      alpha = np.clip(1.0 - self._road_edge_stds[i], 0.0, 1.0)
      color = rl.Color(255, 0, 0, int(alpha * 255))
      draw_polygon(self._rect, road_edge.projected_points, color)

  def _draw_path(self, sm):
    """Draw path with dynamic coloring based on mode and throttle state."""
    if not self._path.projected_points.size:
      return

    if self._experimental_mode:
      # Draw with acceleration coloring
      if len(self._exp_gradient['colors']) > 2:
        draw_polygon(self._rect, self._path.projected_points, gradient=self._exp_gradient)
      else:
        draw_polygon(self._rect, self._path.projected_points, rl.Color(255, 255, 255, 30))
    else:
      # Draw with throttle/no throttle gradient
      allow_throttle = sm['longitudinalPlan'].allowThrottle or not self._longitudinal_control

      # Start transition if throttle state changes
      if allow_throttle != self._prev_allow_throttle:
        self._prev_allow_throttle = allow_throttle
        self._blend_factor = max(1.0 - self._blend_factor, 0.0)

      # Update blend factor
      if self._blend_factor < 1.0:
        self._blend_factor = min(self._blend_factor + PATH_BLEND_INCREMENT, 1.0)

      begin_colors = NO_THROTTLE_COLORS if allow_throttle else THROTTLE_COLORS
      end_colors = THROTTLE_COLORS if allow_throttle else NO_THROTTLE_COLORS

      # Blend colors based on transition
      blended_colors = self._blend_colors(begin_colors, end_colors, self._blend_factor)
      gradient = {
        'start': (0.0, 1.0),  # Bottom of path
        'end': (0.0, 0.0),  # Top of path
        'colors': blended_colors,
        'stops': [0.0, 0.5, 1.0],
      }
      draw_polygon(self._rect, self._path.projected_points, gradient=gradient)

  def _draw_lead_indicator(self):
    # Draw lead vehicles if available
    for lead in self._lead_vehicles:
      if not lead.glow or not lead.chevron:
        continue

      rl.draw_triangle_fan(lead.glow, len(lead.glow), rl.Color(218, 202, 37, 255))
      rl.draw_triangle_fan(lead.chevron, len(lead.chevron), rl.Color(201, 34, 49, lead.fill_alpha))

  @staticmethod
  def _get_path_length_idx(pos_x_array: np.ndarray, path_height: float) -> int:
    """Get the index corresponding to the given path height"""
    idx = np.searchsorted(pos_x_array, path_height, side='right')
    return int(np.clip(idx - 1, 0, len(pos_x_array) - 1))

  def _map_to_screen(self, in_x, in_y, in_z):
    """Project a point in car space to screen space"""
    input_pt = np.array([in_x, in_y, in_z])
    pt = self._car_space_transform @ input_pt

    if abs(pt[2]) < 1e-6:
      return None

    x, y = pt[0] / pt[2], pt[1] / pt[2]

    clip = self._clip_region
    if not (clip.x <= x <= clip.x + clip.width and clip.y <= y <= clip.y + clip.height):
      return None

    return (x, y)

  def _map_line_to_polygon(self, line: np.ndarray, y_off: float, z_off: float, max_idx: int, allow_invert: bool = True) -> np.ndarray:
    """Convert 3D line to 2D polygon for rendering."""
    if line.shape[0] == 0:
      return np.empty((0, 2), dtype=np.float32)

    # Slice points and filter non-negative x-coordinates
    points = line[:max_idx + 1][line[:max_idx + 1, 0] >= 0]
    if points.shape[0] == 0:
      return np.empty((0, 2), dtype=np.float32)

    # Create left and right 3D points in one array
    n_points = points.shape[0]
    points_3d = np.empty((n_points * 2, 3), dtype=np.float32)
    points_3d[:n_points, 0] = points_3d[n_points:, 0] = points[:, 0]
    points_3d[:n_points, 1] = points[:, 1] - y_off
    points_3d[n_points:, 1] = points[:, 1] + y_off
    points_3d[:n_points, 2] = points_3d[n_points:, 2] = points[:, 2] + z_off

    # Single matrix multiplication for projections
    proj = self._car_space_transform @ points_3d.T
    valid_z = np.abs(proj[2]) > 1e-6
    if not np.any(valid_z):
      return np.empty((0, 2), dtype=np.float32)

    # Compute screen coordinates
    screen = proj[:2, valid_z] / proj[2, valid_z][None, :]
    left_screen = screen[:, :n_points].T
    right_screen = screen[:, n_points:].T

    # Ensure consistent shapes by re-aligning valid points
    valid_points = np.minimum(left_screen.shape[0], right_screen.shape[0])
    if valid_points == 0:
      return np.empty((0, 2), dtype=np.float32)
    left_screen = left_screen[:valid_points]
    right_screen = right_screen[:valid_points]

    if self._clip_region:
      clip = self._clip_region
      bounds_mask = (
        (left_screen[:, 0] >= clip.x) & (left_screen[:, 0] <= clip.x + clip.width) &
        (left_screen[:, 1] >= clip.y) & (left_screen[:, 1] <= clip.y + clip.height) &
        (right_screen[:, 0] >= clip.x) & (right_screen[:, 0] <= clip.x + clip.width) &
        (right_screen[:, 1] >= clip.y) & (right_screen[:, 1] <= clip.y + clip.height)
      )
      if not np.any(bounds_mask):
        return np.empty((0, 2), dtype=np.float32)
      left_screen = left_screen[bounds_mask]
      right_screen = right_screen[bounds_mask]

    if not allow_invert and left_screen.shape[0] > 1:
      keep = np.concatenate(([True], np.diff(left_screen[:, 1]) < 0))
      left_screen = left_screen[keep]
      right_screen = right_screen[keep]
      if left_screen.shape[0] == 0:
        return np.empty((0, 2), dtype=np.float32)

    return np.vstack((left_screen, right_screen[::-1])).astype(np.float32)

  @staticmethod
  def _map_val(x, x0, x1, y0, y1):
    x = max(x0, min(x, x1))
    ra = x1 - x0
    rb = y1 - y0
    return (x - x0) * rb / ra + y0 if ra != 0 else y0

  @staticmethod
  def _hsla_to_color(h, s, l, a):
    r, g, b = [max(0, min(255, int(v * 255))) for v in colorsys.hls_to_rgb(h, l, s)]
    return rl.Color(r, g, b, max(0, min(255, int(a * 255))))

  @staticmethod
  def _blend_colors(begin_colors, end_colors, t):
    if t >= 1.0:
      return end_colors
    if t <= 0.0:
      return begin_colors

    inv_t = 1.0 - t
    return [rl.Color(
      int(inv_t * start.r + t * end.r),
      int(inv_t * start.g + t * end.g),
      int(inv_t * start.b + t * end.b),
      int(inv_t * start.a + t * end.a)
    ) for start, end in zip(begin_colors, end_colors, strict=True)]
