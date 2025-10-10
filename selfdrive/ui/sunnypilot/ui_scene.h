/**
  * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
  *
  * This file is part of sunnypilot and is licensed under the MIT License.
  * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

typedef struct UISceneSP : UIScene {
  int dev_ui_info = 0;
  bool standstill_timer = false;
  int speed_limit_mode = 0;
  bool road_name = false;
  int onroadScreenOffBrightness, onroadScreenOffTimer = 0;
  bool onroadScreenOffControl;
  int onroadScreenOffTimerParam;
  bool trueVEgoUI;
  bool hideVEgoUI;
  bool turn_signals = false;
  int visual_radar_tracks = 0;
  float visual_radar_tracks_delay = 0;
  int visual_wide_cam = 0;
  int visual_style = 0;
  int visual_style_zoom = 0;
  int visual_style_overhead = 0;
  int visual_style_overhead_zoom = 0;
  int visual_style_overhead_threshold = 20.0;
} UISceneSP;
