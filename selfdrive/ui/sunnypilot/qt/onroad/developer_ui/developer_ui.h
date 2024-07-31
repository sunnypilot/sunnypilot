/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#pragma once

#include "selfdrive/ui/sunnypilot/qt/onroad/developer_ui/ui_elements.h"

class DeveloperUi {
public:
  static UiElement getDRel(bool lead_status, float lead_d_rel);
  static UiElement getVRel(bool lead_status, float lead_v_rel, bool is_metric, const QString &speed_unit);
  static UiElement getSteeringAngleDeg(float angle_steers, bool mads_enabled, bool lat_active);
  static UiElement getActualLateralAccel(float curvature, float v_ego, float roll, bool mads_enabled, bool lat_active);
  static UiElement getSteeringAngleDesiredDeg(bool mads_enabled, bool lat_active, float steer_angle_desired, float angle_steers);
  static UiElement getMemoryUsagePercent(int memory_usage_percent);
  static UiElement getAEgo(float a_ego);
  static UiElement getVEgoLead(bool lead_status, float lead_v_rel, float v_ego, bool is_metric, const QString &speed_unit);
  static UiElement getFrictionCoefficientFiltered(float friction_coefficient_filtered, bool live_valid);
  static UiElement getLatAccelFactorFiltered(float lat_accel_factor_filtered, bool live_valid);
  static UiElement getSteeringTorqueEps(float steering_torque_eps);
  static UiElement getBearingDeg(float bearing_accuracy_deg, float bearing_deg);
  static UiElement getAltitude(float gps_accuracy, float altitude);
};
