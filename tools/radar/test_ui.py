from tools.radar.ui import camera_motion_display_state


def test_camera_motion_display_state_uses_direct_camera_signals():
  assert camera_motion_display_state({"CLASSIFICATION": 4, "ABS_SPEED": 0}) == 4
  assert camera_motion_display_state({"CLASSIFICATION": 0, "ABS_SPEED": -1.5}) == 1
  assert camera_motion_display_state({"CLASSIFICATION": 0, "ABS_SPEED": 1.5}) == 1
  assert camera_motion_display_state({"CLASSIFICATION": 0, "ABS_SPEED": -1.55}) == 2
  assert camera_motion_display_state({"CLASSIFICATION": 0, "ABS_SPEED": 1.55}) == 2
