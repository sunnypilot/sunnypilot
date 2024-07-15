#pragma once

#include "selfdrive/ui/sunnypilot/qt/onroad/developer_ui/sp_priv_ui_elements.h"

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
