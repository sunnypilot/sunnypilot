#include "selfdrive/ui/sunnypilot/qt/onroad/developer_ui/sp_priv_developer_ui.h"

#include <cmath>

#include "common/util.h"

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

UiElement DeveloperUi::getSteeringAngleDeg(float angle_steers, bool mads_enabled, bool lat_active) {
  QString value = QString("%1%2%3").arg(QString::number(angle_steers, 'f', 1)).arg("°").arg("");
  QColor color = (mads_enabled && lat_active) ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  // Red if large steering angle
  // Orange if moderate steering angle
  if (std::fabs(angle_steers) > 180) {
    color = QColor(255, 0, 0, 255);
  } else if (std::fabs(angle_steers) > 90) {
    color = QColor(255, 188, 0, 255);
  }

  return UiElement(value, "REAL STEER", "", color);
}

UiElement DeveloperUi::getActualLateralAccel(float curvature, float v_ego, float roll, bool mads_enabled, bool lat_active) {
  double actualLateralAccel = (curvature * pow(v_ego, 2)) - (roll * 9.81);

  QString value = QString::number(actualLateralAccel, 'f', 2);
  QColor color = (mads_enabled && lat_active) ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "ACTUAL LAT", "m/s²", color);
}

UiElement DeveloperUi::getSteeringAngleDesiredDeg(bool mads_enabled, bool lat_active, float steer_angle_desired, float angle_steers) {
  QString value = (mads_enabled && lat_active) ? QString("%1%2%3").arg(QString::number(steer_angle_desired, 'f', 1)).arg("°").arg("") : "-";
  QColor color = QColor(255, 255, 255, 255);

  if (mads_enabled && lat_active) {
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

UiElement DeveloperUi::getMemoryUsagePercent(int memory_usage_percent) {
  QString value = QString("%1%2").arg(QString::number(memory_usage_percent, 'd', 0)).arg("%");
  QColor color = (memory_usage_percent > 85) ? QColor(255, 188, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "RAM", "", color);
}

UiElement DeveloperUi::getAEgo(float a_ego) {
  QString value = QString::number(a_ego, 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ACC.", "m/s²", color);
}

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

UiElement DeveloperUi::getFrictionCoefficientFiltered(float friction_coefficient_filtered, bool live_valid) {
  QString value = QString::number(friction_coefficient_filtered, 'f', 3);
  QColor color = live_valid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "FRIC.", "", color);
}

UiElement DeveloperUi::getLatAccelFactorFiltered(float lat_accel_factor_filtered, bool live_valid) {
  QString value = QString::number(lat_accel_factor_filtered, 'f', 3);
  QColor color = live_valid ? QColor(0, 255, 0, 255) : QColor(255, 255, 255, 255);

  return UiElement(value, "L.A.", "m/s²", color);
}

UiElement DeveloperUi::getSteeringTorqueEps(float steering_torque_eps) {
  QString value = QString::number(std::fabs(steering_torque_eps), 'f', 1);
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "E.T.", "N·dm", color);
}

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

UiElement DeveloperUi::getAltitude(float gps_accuracy, float altitude) {
  QString value = (gps_accuracy != 0.00) ? QString::number(altitude, 'f', 1) : "-";
  QColor color = QColor(255, 255, 255, 255);

  return UiElement(value, "ALT.", "m", color);
}
