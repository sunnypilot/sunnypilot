#!/usr/bin/env python3
import time

from openpilot.cereal import messaging
from openpilot.common.constants import CV


def line_graph(values, statuses, active_bucket: int, low: float = .15, high: float = .65, height: int = 11, step: int = 7) -> str:
  width = step * (len(values) - 1) + 1
  dot_height = height * 4
  dots = set()
  value_rows = [round((high - max(low, min(high, value))) / (high - low) * (dot_height - 1)) for value in values]
  marker_rows = [min(row // 4, height - 1) for row in value_rows]
  rows = [row * 4 + 1 for row in marker_rows]

  for i in range(len(rows) - 1):
    x0, x1 = i * step * 2, (i + 1) * step * 2
    for x in range(x0, x1 + 1):
      row = round(rows[i] + (rows[i + 1] - rows[i]) * (x - x0) / (x1 - x0))
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
  for i, (row, status) in enumerate(zip(marker_rows, statuses, strict=True)):
    grid[row][i * step] = "◆" if i == active_bucket else markers[str(status)]

  chart = []
  for row, cells in enumerate(grid):
    value = high - row * (high - low) / (height - 1)
    chart.append(f" {value:.2f}s │{''.join(cells)}")
  chart.append("       └" + "─" * width)
  labels = [" " for _ in range(width)]
  for i in range(len(values)):
    label = f"{i * 10}+" if i == len(values) - 1 else f"{i * 10}"
    start = min(i * step, width - len(label))
    labels[start:start + len(label)] = label
  chart.append("        " + "".join(labels) + " mph")
  chart.append("        ● READY   ○ LEARNING   × UNSTABLE   ◆ ACTIVE")
  return "\n".join(chart)


def main() -> None:
  sm = messaging.SubMaster(["carState", "liveCalibration", "liveDelay"])
  next_redraw = 0.0
  print("\033[2J", end="")
  while True:
    sm.update(500)
    now = time.monotonic()
    if not sm.alive["liveDelay"] or now < next_redraw:
      continue
    next_redraw = now + .25

    ld = sm["liveDelay"]
    edges = [edge * CV.MS_TO_MPH for edge in ld.speedBucketEdges]
    print("\033[H", end="")
    speed = sm["carState"].vEgo * CV.MS_TO_MPH
    calibration = sm["liveCalibration"].calStatus
    print(f"speed {speed:5.1f} mph   calibration {calibration}   status {ld.status}   applied {ld.lateralDelay:.3f} s\n")
    print("LAG ESTIMATE BY SPEED BUCKET")
    print(line_graph(ld.lateralDelayBuckets, ld.statusBuckets, ld.speedBucket), "\n")
    print("    range       estimate   applied    std    blocks   progress   starts in   state      last reset")
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
      print(row + "\033[K")


if __name__ == "__main__":
  main()
