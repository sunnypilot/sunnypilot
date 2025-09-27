/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include <cmath>

#include "common/util.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/developer_ui/developer_ui.h"


// Add Relative Distance to Primary Lead Car
// Unit: Meters
UiElement DeveloperUi::getDRel(bool lead_status, float lead_d_rel) {
  QString value = lead_status ? QString::number(lead_d_rel, 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Orange if close, Red if very close
    if (lead_d_rel < 5) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_d_rel < 15) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "REL DIST", "m", color);
}

// Add Relative Velocity vs Primary Lead Car
// Unit: kph if metric, else mph
UiElement DeveloperUi::getVRel(bool lead_status, float lead_v_rel, bool is_metric, const QString &speed_unit) {
  QString value = lead_status ? QString::number(lead_v_rel * (is_metric ? MS_TO_KPH : MS_TO_MPH), 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Red if approaching faster than 10mph
    // Orange if approaching (negative)
    if (lead_v_rel < -4.4704) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_v_rel < 0) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "REL SPEED", speed_unit, color);
}

// Add Real Steering Angle
// Unit: Degrees
UiElement DeveloperUi::getSteeringAngleDeg(float angle_steers, bool lat_active, bool steer_override) {
  QString value = QString("%1%2%3").arg(QString::number(angle_steers, 'f', 1)).arg("°").arg("");
  QColor color = lat_active ? (steer_override ? QColor(0x91, 0x9b, 0x95, 0xff) : QColor(0, 255, 0, 255)) : QColor(255, 255, 255, 255);

  // Red if large steering angle
  // Orange if moderate steering angle
  if (std::fabs(angle_steers) > 180) {
    color = QColor(255, 0, 0, 255);
  } else if (std::fabs(angle_steers) > 90) {
    color = QColor(255, 188, 0, 255);
  }

  return UiElement(value, "REAL STEER", "", color);
}

// Add Actual Lateral Acceleration (roll compensated) when using Torque
// Unit: m/s²
UiElement DeveloperUi::getActualLateralAccel(float curvature, float v_ego, float roll, bool lat_active, bool steer_override) {
  double actualLateralAccel = (curvature * pow(v_ego, 2)) - (roll * 9.81);

  QString value = QString::number(actualLateralAccel, 'f', 2);
  QColor color = lat_active ? (steer_override ? QColor(0x91, 0x9b, 0x95, 0xff) : QColor(0, 255, 0, 255)) : QColor(255, 255, 255, 255);

  return UiElement(value, "ACTUAL L.A.", "m/s²", color);
}

// Add Desired Steering Angle when using PID
// Unit: Degrees
UiElement DeveloperUi::getSteeringAngleDesiredDeg(bool lat_active, float steer_angle_desired, float angle_steers) {
  QString value = lat_active ? QString("%1%2%3").arg(QString::number(steer_angle_desired, 'f', 1)).arg("°").arg("") : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lat_active) {
    // Red if large steering angle
    // Orange if moderate steering angle
    if (std::fabs(angle_steers) > 180) {
      color = QColor(255, 0, 0, 255);
    } else if (std::fabs(angle_steers) > 90) {
      color = QColor(255, 188, 0, 255);
    } else {
      color = QColor(0, 255, 0, 255);
    }
  }

  return UiElement(value, "DESIRED STEER", "", color);
}

// Add Device Memory (RAM) Usage
// Unit: Percent
UiElement DeveloperUi::getMemoryUsagePercent(int memory_usage_percent) {
  QString value = QString("%1%2").arg(QString::number(memory_usage_percent, 'd', 0)).arg("%");
  QColor color = (memory_usage_percent > 85) ? QColor(255, 188, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "RAM", "", color);
}

// Add Vehicle Current Acceleration
// Unit: m/s²
UiElement DeveloperUi::getAEgo(float a_ego) {
  QString value = QString::number(a_ego, 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ACC.", "m/s²", color);
}

// Add Relative Velocity to Primary Lead Car
// Unit: kph if metric, else mph
UiElement DeveloperUi::getVEgoLead(bool lead_status, float lead_v_rel, float v_ego, bool is_metric, const QString &speed_unit) {
  QString value = lead_status ? QString::number((lead_v_rel + v_ego) * (is_metric ? MS_TO_KPH : MS_TO_MPH), 'f', 0) : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (lead_status) {
    // Red if approaching faster than 10mph
    // Orange if approaching (negative)
    if (lead_v_rel < -4.4704) {
      color = QColor(255, 0, 0, 255);
    } else if (lead_v_rel < 0) {
      color = QColor(255, 188, 0, 255);
    }
  }

  return UiElement(value, "L.S.", speed_unit, color);
}

// Add Friction Coefficient Raw from torqued
// Unit: None
UiElement DeveloperUi::getFrictionCoefficientFiltered(float friction_coefficient_filtered, bool live_valid) {
  QString value = QString::number(friction_coefficient_filtered, 'f', 3);
  QColor color = live_valid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "FRIC.", "", color);
}

// Add Lateral Acceleration Factor Raw from torqued
// Unit: m/s²
UiElement DeveloperUi::getLatAccelFactorFiltered(float lat_accel_factor_filtered, bool live_valid) {
  QString value = QString::number(lat_accel_factor_filtered, 'f', 3);
  QColor color = live_valid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "L.A.", "m/s²", color);
}

// Add Steering Torque from Car EPS
// Unit: Newton Meters
UiElement DeveloperUi::getSteeringTorqueEps(float steering_torque_eps) {
  QString value = QString::number(std::fabs(steering_torque_eps), 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "E.T.", "N·dm", color);
}

// Add Bearing Degree and Direction from Car (Compass)
// Unit: Meters
UiElement DeveloperUi::getBearingDeg(float bearing_accuracy_deg, float bearing_deg) {
  QString value = (bearing_accuracy_deg != 180.00) ? QString("%1%2%3").arg(QString::number(bearing_deg, 'd', 0)).arg("°").arg("") : "-";
  QColor color = QColor(255, 255, 255, 255);
  QString dir_value;

  if (bearing_accuracy_deg != 180.00) {
    if (((bearing_deg >= 337.5) && (bearing_deg <= 360)) || ((bearing_deg >= 0) && (bearing_deg <= 22.5))) {
      dir_value = "N";
    } else if ((bearing_deg > 22.5) && (bearing_deg < 67.5)) {
      dir_value = "NE";
    } else if ((bearing_deg >= 67.5) && (bearing_deg <= 112.5)) {
      dir_value = "E";
    } else if ((bearing_deg > 112.5) && (bearing_deg < 157.5)) {
      dir_value = "SE";
    } else if ((bearing_deg >= 157.5) && (bearing_deg <= 202.5)) {
      dir_value = "S";
    } else if ((bearing_deg > 202.5) && (bearing_deg < 247.5)) {
      dir_value = "SW";
    } else if ((bearing_deg >= 247.5) && (bearing_deg <= 292.5)) {
      dir_value = "W";
    } else if ((bearing_deg > 292.5) && (bearing_deg < 337.5)) {
      dir_value = "NW";
    }
  } else {
    dir_value = "OFF";
  }

  return UiElement(QString("%1 | %2").arg(dir_value).arg(value), "B.D.", "", color);
}

// Add Altitude of Current Location
// Unit: Meters
UiElement DeveloperUi::getAltitude(float gps_accuracy, float altitude) {
  QString value = (gps_accuracy != 0.00) ? QString::number(altitude, 'f', 1) : "-";
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ALT.", "m", color);
}

// Add Actuators Output
// Unit: Degree (angle) or m/s² (torque)
UiElement DeveloperUi::getActuatorsOutputLateral(cereal::CarParams::SteerControlType steerControlType,
                                                 cereal::CarControl::Actuators::Reader &actuators,
                                                 float desiredCurvature, float v_ego, float roll, bool lat_active, bool steer_override) {
  QString label;
  QString value;
  QString unit;

  if (steerControlType == cereal::CarParams::SteerControlType::ANGLE) {
    label = "DESIRED STEER";
    value = QString("%1%2%3").arg(QString::number(actuators.getSteeringAngleDeg(), 'f', 1)).arg("°").arg("");
  } else {
    label = "DESIRED L.A.";
    double desiredLateralAccel = (desiredCurvature * pow(v_ego, 2)) - (roll * 9.81);
    value = QString::number(desiredLateralAccel, 'f', 2);
    unit = "m/s²";
  }

  value = lat_active ? value : "-";
  QColor color = lat_active ? (steer_override ? QColor(0x91, 0x9b, 0x95, 0xff) : QColor(0, 255, 0, 255)) : QColor(255, 255, 255, 255);

  return UiElement(value, label, unit, color);
}
