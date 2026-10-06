"""Run with the road-segmentation environment: python tools/yolo/check_road_overlay.py."""
import numpy as np
from yolo_web import draw_comma_overlay


def check():
  line = lambda y: {"x": [10, 20, 50], "y": [y, y, y]}
  sample = {
    "roadCamera": {"width": 1280, "height": 720, "ground": [640, -1000, 0, 360, 0, 1000, 1, 0, 0]},
    "wideRoadCamera": {"width": 1280, "height": 720, "ground": [640, -500, 0, 360, 0, 500, 1, 0, 0]},
    "model": {"path": line(0), "laneLines": [line(-1), line(1)], "laneLineProbs": [1, 1],
              "roadEdges": [line(-3), line(3)]},
  }
  road = np.zeros((720, 1280, 3), np.uint8)
  assert draw_comma_overlay(road, sample, "road")
  assert tuple(road[460, 340]) == (0, 128, 255)  # model y=-3 is the left edge
  assert tuple(road[460, 540]) == (255, 255, 255)  # left lane
  assert tuple(road[460, 640]) == (0, 0, 0)  # comma trajectory is not rendered
  wide = np.zeros((360, 640, 3), np.uint8)
  assert draw_comma_overlay(wide, sample, "wideRoad")
  assert tuple(wide[205, 245]) == (0, 128, 255)  # wide calibration + video resizing
  untouched = road.copy()
  assert not draw_comma_overlay(road, {}, "road")
  assert np.array_equal(road, untouched)
  invisible = np.zeros_like(road)
  assert draw_comma_overlay(invisible, sample, "road", 0)
  assert not invisible.any()
  half = np.zeros_like(road)
  assert draw_comma_overlay(half, sample, "road", .5)
  assert np.allclose(half[460, 540], np.array([255, 255, 255]) * .5, atol=1)
  print("Road/wide projection, video scaling, missing calibration, and opacity checks passed.")


if __name__ == "__main__":
  check()
