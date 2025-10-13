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
  int chevron_info;
  bool blindspot_ui;
  bool rainbow_mode;
} UISceneSP;
