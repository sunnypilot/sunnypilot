#!/usr/bin/env python3
from collections import deque
import time

from openpilot.cereal import messaging
from openpilot.common.constants import CV


PING_PONG_WINDOW = 30.0
PING_PONG_MIN_WINDOW = 15.0


def ping_pong_metrics(samples: list[tuple[float, float]]) -> tuple[str, float, float, float]:
  duration = samples[-1][0] - samples[0][0] if len(samples) > 1 else 0.0
  if duration < PING_PONG_MIN_WINDOW:
    return "COLLECTING", 0.0, 0.0, duration

  values = [sample[1] for sample in samples]
  smoothed = [sum(values[max(0, i - 5):i + 6]) / len(values[max(0, i - 5):i + 6]) for i in range(len(values))]
  center = sum(smoothed) / len(smoothed)
  residual = [value - center for value in smoothed]
  ordered = sorted(residual)
  amplitude = (ordered[int(.9 * (len(ordered) - 1))] - ordered[int(.1 * (len(ordered) - 1))]) / 2
  hysteresis = max(.01, amplitude * .3)
  state = 0
  reversals = 0
  for value in residual:
    new_state = 1 if value > hysteresis else -1 if value < -hysteresis else state
    if state and new_state != state:
      reversals += 1
    state = new_state
  cycles_per_min = reversals * 30 / duration

  if not 5 <= cycles_per_min <= 20 or amplitude < .03:
    severity = "NONE"
  elif amplitude < .07:
    severity = "MILD"
  elif amplitude < .15:
    severity = "MODERATE"
  else:
    severity = "SEVERE"
  return severity, amplitude, cycles_per_min, duration


def line_graph(values, statuses, active_bucket: int, edges=None, low: float = .15, high: float = .65, height: int = 11, step: int = 8) -> str:
  width = step * len(values) + 1
  dot_height = height * 4
  dots = set()
  value_rows = [round((high - max(low, min(high, value))) / (high - low) * (dot_height - 1)) for value in values]
  marker_rows = [min(row // 4, height - 1) for row in value_rows]
  rows = [row * 4 + 1 for row in marker_rows]
  point_cols = [i * step + step // 2 for i in range(len(rows))]
  point_xs = [col * 2 for col in point_cols]

  knot_xs = [0, *point_xs, width * 2 - 2]
  knot_rows = [rows[0], *rows, rows[-1]]
  for i in range(len(knot_rows) - 1):
    x0, x1 = knot_xs[i], knot_xs[i + 1]
    for x in range(x0, x1 + 1):
      row = round(knot_rows[i] + (knot_rows[i + 1] - knot_rows[i]) * (x - x0) / (x1 - x0))
      dots.add((x, row))

  braille_bits = ((0, 3), (1, 4), (2, 5), (6, 7))
  grid = [[" " for _ in range(width)] for _ in range(height)]
  for cell_row in range(height):
    for cell_col in range(width):
      bits = 0
      for dot_row in range(4):
        for dot_col in range(2):
          if (cell_col * 2 + dot_col, cell_row * 4 + dot_row) in dots:
            bits |= 1 << braille_bits[dot_row][dot_col]
      if bits:
        grid[cell_row][cell_col] = chr(0x2800 + bits)

  markers = {"unestimated": "○", "estimated": "●", "invalid": "×"}
  for i, (col, row, status) in enumerate(zip(point_cols, marker_rows, statuses, strict=True)):
    grid[row][col] = "◆" if i == active_bucket else markers[str(status)]

  chart = []
  for row, cells in enumerate(grid):
    value = high - row * (high - low) / (height - 1)
    chart.append(f" {value:.2f}s │{''.join(cells)}")
  axis_edges = edges if edges is not None else [i * 10 for i in range(len(values))]
  axis = ["─" for _ in range(width)]
  for i in range(1, len(axis_edges)):
    axis[i * step] = "┬"
  chart.append("       └" + "".join(axis))
  labels = [" " for _ in range(width)]
  for i, edge in enumerate(axis_edges):
    label = f"{edge:.0f}+" if i == len(axis_edges) - 1 else f"{edge:.0f}"
    start = min(i * step, width - len(label))
    labels[start:start + len(label)] = label
  chart.append(" edges  " + "".join(labels) + " mph")
  center_labels = [" " for _ in range(width)]
  widths = [axis_edges[i + 1] - edge for i, edge in enumerate(axis_edges[:-1])]
  widths.append(widths[-1] if widths else 0)
  for col, edge, bucket_width in zip(point_cols, axis_edges, widths, strict=True):
    label = f"{edge + bucket_width / 2:.0f}"
    start = max(0, min(col - len(label) // 2, width - len(label)))
    center_labels[start:start + len(label)] = label
  chart.append(" centers" + "".join(center_labels) + " mph (dots)")
  chart.append("        ● READY   ○ LEARNING   × UNSTABLE   ◆ ACTIVE")
  return "\n".join(chart)


def main() -> None:
  sm = messaging.SubMaster(["carControl", "carState", "controlsState", "liveCalibration", "liveDelay"])
  ping_pong_samples: deque[tuple[float, float]] = deque()
  ping_pong_waiting = "lateral inactive"
  last_sample = 0.0
  next_redraw = 0.0
  print("\033[2J", end="")
  while True:
    sm.update(500)
    now = time.monotonic()
    speed_mps = sm["carState"].vEgo
    desired_lat_accel = sm["controlsState"].desiredCurvature * speed_mps ** 2
    if now - last_sample >= .1:
      if not sm["carControl"].latActive:
        ping_pong_waiting = "lateral inactive"
      elif sm["carState"].steeringPressed:
        ping_pong_waiting = "driver steering"
      elif speed_mps < 2:
        ping_pong_waiting = "speed below 5 mph"
      elif abs(desired_lat_accel) > .5:
        ping_pong_waiting = "not a straight segment"
      else:
        ping_pong_waiting = ""
        ping_pong_samples.append((now, sm["controlsState"].curvature * speed_mps ** 2))
        while ping_pong_samples and now - ping_pong_samples[0][0] > PING_PONG_WINDOW:
          ping_pong_samples.popleft()
      if ping_pong_waiting:
        ping_pong_samples.clear()
      last_sample = now

    if not sm.alive["liveDelay"] or now < next_redraw:
      continue
    next_redraw = now + .25

    ld = sm["liveDelay"]
    edges = [edge * CV.MS_TO_MPH for edge in ld.speedBucketEdges]
    speed = sm["carState"].vEgo * CV.MS_TO_MPH
    calibration = sm["liveCalibration"].calStatus
    lines = [f"speed {speed:5.1f} mph   calibration {calibration}   status {ld.status}   applied {ld.lateralDelay:.3f} s"]
    severity, sway, cycles, duration = ping_pong_metrics(list(ping_pong_samples))
    ping_pong = f"PING-PONG {severity:<10}  sway {sway:.3f} m/s²   {cycles:.1f} cycles/min   window {duration:.0f}s"
    if ping_pong_waiting:
      ping_pong = f"PING-PONG WAITING     {ping_pong_waiting}"
    elif severity == "COLLECTING":
      ping_pong = f"PING-PONG COLLECTING  {duration:.0f}/{PING_PONG_MIN_WINDOW:.0f}s of straight driving"
    lines.extend([ping_pong, "", "APPLIED LAG BY SPEED (INTERPOLATED)",
                  *line_graph(ld.lateralDelayAppliedBuckets, ld.statusBuckets, ld.speedBucket, edges).splitlines(), "",
                  "    range       estimate   applied    std    blocks   progress   starts in   state      last reset"])
    for i, (estimate, applied, std, blocks, percent, countdown, status, reason) in enumerate(zip(ld.lateralDelayBuckets,
                                                                                                 ld.lateralDelayAppliedBuckets,
                                                                                                 ld.lateralDelayEstimateStdBuckets,
                                                                                                 ld.validBlocksBuckets,
                                                                                                 ld.calPercBuckets,
                                                                                                 ld.learningCountdownBuckets,
                                                                                                 ld.statusBuckets,
                                                                                                 ld.learningResetReasonBuckets,
                                                                                                 strict=True)):
      speed_range = f"{edges[i]:.0f}-{edges[i + 1]:.0f} mph" if i + 1 < len(edges) else f"{edges[i]:.0f}+ mph"
      active = "*" if i == ld.speedBucket else " "
      status_name = str(status)
      state = {"unestimated": "LEARNING", "estimated": "READY", "invalid": "UNSTABLE"}[status_name]
      row = f" {active} {speed_range:<9}   {estimate:.3f} s   {applied:.3f} s   {std:.3f}"
      waiting = "  --" if status_name == "estimated" else f"{countdown:4.1f}s"
      reset_reason = "--" if status_name == "estimated" else (reason or "--")
      row += f"     {blocks:2}       {percent:3}%        {waiting}     {state:<9}  {reset_reason}"
      lines.append(row)
    print("\033[H" + "\033[K\n".join(lines) + "\033[K\033[J", end="", flush=True)


if __name__ == "__main__":
  main()
