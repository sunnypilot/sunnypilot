/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include <QPainterPath>

#include "selfdrive/ui/sunnypilot/qt/onroad/hud.h"

#include "selfdrive/ui/qt/util.h"


HudRendererSP::HudRendererSP() {}

void HudRendererSP::updateState(const UIState &s) {
  HudRenderer::updateState(s);

  const SubMaster &sm = *(s.sm);
  const auto cs = sm["controlsState"].getControlsState();
  const auto car_state = sm["carState"].getCarState();
  const auto car_control = sm["carControl"].getCarControl();
  const auto radar_state = sm["radarState"].getRadarState();
  const auto is_gps_location_external = sm.rcv_frame("gpsLocationExternal") > 1;
  const auto gpsLocation = is_gps_location_external ? sm["gpsLocationExternal"].getGpsLocationExternal() : sm["gpsLocation"].getGpsLocation();
  const auto ltp = sm["liveTorqueParameters"].getLiveTorqueParameters();
  const auto car_params = sm["carParams"].getCarParams();
  const auto lp_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();
  const auto lmd = sm["liveMapDataSP"].getLiveMapDataSP();

  float speedConv = is_metric ? MS_TO_KPH : MS_TO_MPH;
  speedLimit = lp_sp.getSpeedLimit().getResolver().getSpeedLimit() * speedConv;
  speedLimitOffset = lp_sp.getSpeedLimit().getResolver().getSpeedLimitOffset() * speedConv;
  speedLimitValid = speedLimit > 0;
  speedLimitLastValid = speedLimitLast > 0;
  speedLimitMode = static_cast<SpeedLimitMode>(s.scene.speed_limit_mode);
  roadName = s.scene.road_name;
  if (sm.updated("liveMapDataSP")) {
    roadNameStr = QString::fromStdString(lmd.getRoadName());
    speedLimitAheadValid = lmd.getSpeedLimitAheadValid();
    speedLimitAhead = lmd.getSpeedLimitAhead() * speedConv;
    speedLimitAheadDistance = lmd.getSpeedLimitAheadDistance();
    if (speedLimitAheadDistance < speedLimitAheadDistancePrev && speedLimitAheadValidFrame < SPEED_LIMIT_AHEAD_VALID_FRAME_THRESHOLD) {
      speedLimitAheadValidFrame++;
    } else if (speedLimitAheadDistance > speedLimitAheadDistancePrev && speedLimitAheadValidFrame > 0) {
      speedLimitAheadValidFrame--;
    }
  }
  speedLimitAheadDistancePrev = speedLimitAheadDistance;

  if (speedLimitValid) {
    speedLimitLast = speedLimit;
  }

  static int reverse_delay = 0;
  bool reverse_allowed = false;
  if (int(car_state.getGearShifter()) != 4) {
    reverse_delay = 0;
    reverse_allowed = false;
  } else {
    reverse_delay += 50;
    if (reverse_delay >= 1000) {
      reverse_allowed = true;
    }
  }

  reversing = reverse_allowed;

  latActive = car_control.getLatActive();
  steerOverride = car_state.getSteeringPressed();

  devUiInfo = s.scene.dev_ui_info;

  speedUnit = is_metric ? tr("km/h") : tr("mph");
  lead_d_rel = radar_state.getLeadOne().getDRel();
  lead_v_rel = radar_state.getLeadOne().getVRel();
  lead_status = radar_state.getLeadOne().getStatus();
  steerControlType = car_params.getSteerControlType();
  actuators = car_control.getActuators();
  torqueLateral = steerControlType == cereal::CarParams::SteerControlType::TORQUE;
  angleSteers = car_state.getSteeringAngleDeg();
  desiredCurvature = cs.getDesiredCurvature();
  curvature = cs.getCurvature();
  roll = sm["liveParameters"].getLiveParameters().getRoll();
  memoryUsagePercent = sm["deviceState"].getDeviceState().getMemoryUsagePercent();
  gpsAccuracy = is_gps_location_external ? gpsLocation.getHorizontalAccuracy() : 1.0;  // External reports accuracy, internal does not.
  altitude = gpsLocation.getAltitude();
  vEgo = car_state.getVEgo();
  aEgo = car_state.getAEgo();
  steeringTorqueEps = car_state.getSteeringTorqueEps();
  bearingAccuracyDeg = gpsLocation.getBearingAccuracyDeg();
  bearingDeg = gpsLocation.getBearingDeg();
  torquedUseParams = ltp.getUseParams();
  latAccelFactorFiltered = ltp.getLatAccelFactorFiltered();
  frictionCoefficientFiltered = ltp.getFrictionCoefficientFiltered();
  liveValid = ltp.getLiveValid();

  standstillTimer = s.scene.standstill_timer;
  isStandstill = car_state.getStandstill();
  longOverride = car_control.getCruiseControl().getOverride();
  smartCruiseControlVisionEnabled = lp_sp.getSmartCruiseControl().getVision().getEnabled();
  smartCruiseControlVisionActive = lp_sp.getSmartCruiseControl().getVision().getActive();
}

void HudRendererSP::draw(QPainter &p, const QRect &surface_rect) {
  HudRenderer::draw(p, surface_rect);
  if (!reversing) {
    // Smart Cruise Control
    int x_offset = -260;
    int y1_offset = -80;
    // int y2_offset = -140;  // reserved for 2 icons

    bool scc_vision_active_pulse = pulseElement(smartCruiseControlVisionFrame);
    if ((smartCruiseControlVisionEnabled && !smartCruiseControlVisionActive) || (smartCruiseControlVisionActive && scc_vision_active_pulse)) {
      drawSmartCruiseControlOnroadIcon(p, surface_rect, x_offset, y1_offset, "SCC-V");
    }

    if (smartCruiseControlVisionActive) {
      smartCruiseControlVisionFrame++;
    } else {
      smartCruiseControlVisionFrame = 0;
    }

    // Bottom Dev UI
    if (devUiInfo == 2) {
      QRect rect_bottom(surface_rect.left(), surface_rect.bottom() - 60, surface_rect.width(), 61);
      p.setPen(Qt::NoPen);
      p.setBrush(QColor(0, 0, 0, 100));
      p.drawRect(rect_bottom);
      drawBottomDevUI(p, rect_bottom.left(), rect_bottom.center().y());
    }

    // Right Dev UI
    if (devUiInfo != 0) {
      QRect rect_right(surface_rect.right() - (UI_BORDER_SIZE * 2), UI_BORDER_SIZE * 1.5, 184, 170);
      drawRightDevUI(p, surface_rect.right() - 184 - UI_BORDER_SIZE * 2, UI_BORDER_SIZE * 2 + rect_right.height());
    }

    // Standstill Timer
    if (standstillTimer) {
      drawStandstillTimer(p, surface_rect.right() / 12 * 10, surface_rect.bottom() / 12 * 1.53);
    }

    // Speed Limit
    if (speedLimitMode != SpeedLimitMode::OFF) {
      drawSpeedLimitSigns(p);
      drawUpcomingSpeedLimit(p);
    }

    // Road Name
    drawRoadName(p, surface_rect);
  }
}

void HudRendererSP::drawText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});
  p.setPen(color);
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

bool HudRendererSP::pulseElement(int frame) {
  if (frame % UI_FREQ < (UI_FREQ / 2.5)) {
    return false;
  }

  return true;
}

void HudRendererSP::drawSmartCruiseControlOnroadIcon(QPainter &p, const QRect &surface_rect, int x_offset, int y_offset, std::string name) {
  int x = surface_rect.center().x();
  int y = surface_rect.height() / 4;

  QString text = QString::fromStdString(name);
  QFont font = InterFont(36, QFont::Bold);
  p.setFont(font);

  QFontMetrics fm(font);

  int padding_v = 5;
  int box_width = 160;
  int box_height = fm.height() + padding_v * 2;

  QRectF bg_rect(x - (box_width / 2) + x_offset,
                 y - (box_height / 2) + y_offset,
                 box_width, box_height);

  QPainterPath boxPath;
  boxPath.addRoundedRect(bg_rect, 10, 10);

  int text_w = fm.horizontalAdvance(text);
  qreal baseline_y = bg_rect.top() + padding_v + fm.ascent();
  qreal text_x = bg_rect.center().x() - (text_w / 2.0);

  QPainterPath textPath;
  textPath.addText(QPointF(text_x, baseline_y), font, text);
  boxPath = boxPath.subtracted(textPath);

  p.setPen(Qt::NoPen);
  p.setBrush(longOverride ? QColor(0x91, 0x9b, 0x95, 0xf1) : QColor(0, 0xff, 0, 0xff));
  p.drawPath(boxPath);
}

int HudRendererSP::drawRightDevUIElement(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color) {

  p.setFont(InterFont(28, QFont::Bold));
  x += 92;
  y += 80;
  drawText(p, x, y, label);

  p.setFont(InterFont(30 * 2, QFont::Bold));
  y += 65;
  drawText(p, x, y, value, color);

  p.setFont(InterFont(28, QFont::Bold));

  if (units.length() > 0) {
    p.save();
    x += 120;
    y -= 25;
    p.translate(x, y);
    p.rotate(-90);
    drawText(p, 0, 0, units);
    p.restore();
  }

  return 130;
}

void HudRendererSP::drawRightDevUI(QPainter &p, int x, int y) {
  int rh = 5;
  int ry = y;

  UiElement dRelElement = DeveloperUi::getDRel(lead_status, lead_d_rel);
  rh += drawRightDevUIElement(p, x, ry, dRelElement.value, dRelElement.label, dRelElement.units, dRelElement.color);
  ry = y + rh;

  UiElement vRelElement = DeveloperUi::getVRel(lead_status, lead_v_rel, is_metric, speedUnit);
  rh += drawRightDevUIElement(p, x, ry, vRelElement.value, vRelElement.label, vRelElement.units, vRelElement.color);
  ry = y + rh;

  UiElement steeringAngleDegElement = DeveloperUi::getSteeringAngleDeg(angleSteers, latActive, steerOverride);
  rh += drawRightDevUIElement(p, x, ry, steeringAngleDegElement.value, steeringAngleDegElement.label, steeringAngleDegElement.units, steeringAngleDegElement.color);
  ry = y + rh;

  UiElement actuatorsOutputLateralElement = DeveloperUi::getActuatorsOutputLateral(steerControlType, actuators, desiredCurvature, vEgo, roll, latActive, steerOverride);
  rh += drawRightDevUIElement(p, x, ry, actuatorsOutputLateralElement.value, actuatorsOutputLateralElement.label, actuatorsOutputLateralElement.units, actuatorsOutputLateralElement.color);
  ry = y + rh;

  UiElement actualLateralAccelElement = DeveloperUi::getActualLateralAccel(curvature, vEgo, roll, latActive, steerOverride);
  rh += drawRightDevUIElement(p, x, ry, actualLateralAccelElement.value, actualLateralAccelElement.label, actualLateralAccelElement.units, actualLateralAccelElement.color);
}

int HudRendererSP::drawBottomDevUIElement(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color) {
  p.setFont(InterFont(38, QFont::Bold));
  QFontMetrics fm(p.font());
  QRect init_rect = fm.boundingRect(label + " ");
  QRect real_rect = fm.boundingRect(init_rect, 0, label + " ");
  real_rect.moveCenter({x, y});

  QRect init_rect2 = fm.boundingRect(value);
  QRect real_rect2 = fm.boundingRect(init_rect2, 0, value);
  real_rect2.moveTop(real_rect.top());
  real_rect2.moveLeft(real_rect.right() + 10);

  QRect init_rect3 = fm.boundingRect(units);
  QRect real_rect3 = fm.boundingRect(init_rect3, 0, units);
  real_rect3.moveTop(real_rect.top());
  real_rect3.moveLeft(real_rect2.right() + 10);

  p.setPen(Qt::white);
  p.drawText(real_rect, Qt::AlignLeft | Qt::AlignVCenter, label);

  p.setPen(color);
  p.drawText(real_rect2, Qt::AlignRight | Qt::AlignVCenter, value);
  p.drawText(real_rect3, Qt::AlignLeft | Qt::AlignVCenter, units);
  return 430;
}

void HudRendererSP::drawBottomDevUI(QPainter &p, int x, int y) {
  int rw = 90;

  UiElement aEgoElement = DeveloperUi::getAEgo(aEgo);
  rw += drawBottomDevUIElement(p, rw, y, aEgoElement.value, aEgoElement.label, aEgoElement.units, aEgoElement.color);

  UiElement vEgoLeadElement = DeveloperUi::getVEgoLead(lead_status, lead_v_rel, vEgo, is_metric, speedUnit);
  rw += drawBottomDevUIElement(p, rw, y, vEgoLeadElement.value, vEgoLeadElement.label, vEgoLeadElement.units, vEgoLeadElement.color);

  if (torqueLateral && torquedUseParams) {
    UiElement frictionCoefficientFilteredElement = DeveloperUi::getFrictionCoefficientFiltered(frictionCoefficientFiltered, liveValid);
    rw += drawBottomDevUIElement(p, rw, y, frictionCoefficientFilteredElement.value, frictionCoefficientFilteredElement.label, frictionCoefficientFilteredElement.units, frictionCoefficientFilteredElement.color);

    UiElement latAccelFactorFilteredElement = DeveloperUi::getLatAccelFactorFiltered(latAccelFactorFiltered, liveValid);
    rw += drawBottomDevUIElement(p, rw, y, latAccelFactorFilteredElement.value, latAccelFactorFilteredElement.label, latAccelFactorFilteredElement.units, latAccelFactorFilteredElement.color);
  } else {
    UiElement steeringTorqueEpsElement = DeveloperUi::getSteeringTorqueEps(steeringTorqueEps);
    rw += drawBottomDevUIElement(p, rw, y, steeringTorqueEpsElement.value, steeringTorqueEpsElement.label, steeringTorqueEpsElement.units, steeringTorqueEpsElement.color);

    UiElement bearingDegElement = DeveloperUi::getBearingDeg(bearingAccuracyDeg, bearingDeg);
    rw += drawBottomDevUIElement(p, rw, y, bearingDegElement.value, bearingDegElement.label, bearingDegElement.units, bearingDegElement.color);
  }

  UiElement altitudeElement = DeveloperUi::getAltitude(gpsAccuracy, altitude);
  rw += drawBottomDevUIElement(p, rw, y, altitudeElement.value, altitudeElement.label, altitudeElement.units, altitudeElement.color);
}

void HudRendererSP::drawStandstillTimer(QPainter &p, int x, int y) {
  if (isStandstill) {
    standstillElapsedTime += 1.0 / UI_FREQ;

    int minute = static_cast<int>(standstillElapsedTime / 60);
    int second = static_cast<int>(standstillElapsedTime - (minute * 60));

    // stop sign for standstill timer
    const int size = 190;  // size
    const float angle = M_PI / 8.0;

    QPolygon octagon;
    for (int i = 0; i < 8; i++) {
      float curr_angle = angle + i * M_PI / 4.0;
      int point_x = x + size / 2 * cos(curr_angle);
      int point_y = y + size / 2 * sin(curr_angle);
      octagon << QPoint(point_x, point_y);
    }

    p.setPen(QPen(Qt::white, 6));
    p.setBrush(QColor(255, 90, 81, 200)); // red pastel
    p.drawPolygon(octagon);

    QString time_str = QString("%1:%2").arg(minute, 1, 10, QChar('0')).arg(second, 2, 10, QChar('0'));
    p.setFont(InterFont(55, QFont::Bold));
    p.setPen(Qt::white);
    QRect timerTextRect = p.fontMetrics().boundingRect(QString(time_str));
    timerTextRect.moveCenter({x, y});
    p.drawText(timerTextRect, Qt::AlignCenter, QString(time_str));
  } else {
    standstillElapsedTime = 0.0;
  }
}

void HudRendererSP::drawSpeedLimitSigns(QPainter &p) {
  bool hasSpeedLimit = speedLimitValid || speedLimitLastValid;
  int speedLimitFinal = std::nearbyint(speedLimitValid ? speedLimit : speedLimitLast);
  int speedLimitOffsetFinal = speedLimitFinal + std::nearbyint(speedLimitOffset);
  bool overspeed = hasSpeedLimit && speedLimitOffsetFinal < std::nearbyint(speed);
  bool speedLimitWarningEnabled = speedLimitMode == SpeedLimitMode::WARNING;  // TODO-SP: update to include SpeedLimitMode::ASSIST
  QString speedLimitStr = hasSpeedLimit ? QString::number(speedLimitFinal) : "---";

  // Offset display text
  QString speedLimitSubText = "";
  if (speedLimitOffset != 0) {
    speedLimitSubText = (speedLimitOffset > 0 ? "" : "-") + QString::number(std::nearbyint(speedLimitOffset));
  }

  float speedLimitSubTextFactor = is_metric ? 0.5 : 0.6;
  if (speedLimitSubText.size() >= 3) {
    speedLimitSubTextFactor = 0.475;
  }

  // Position next to MAX speed box
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;
  QRect sign_rect(sign_x, sign_y, sign_width, sign_height);

  int alpha = 255;
  QColor red_color = QColor(255, 0, 0, alpha);
  QColor speed_color = (speedLimitWarningEnabled && overspeed) ? red_color :
                       (!speedLimitValid && speedLimitLastValid ? QColor(0x91, 0x9b, 0x95, 0xf1) : QColor(0, 0, 0, alpha));

  if (is_metric) {
    // EU Vienna Convention style circular sign
    QRect vienna_rect = sign_rect;
    int circle_size = std::min(vienna_rect.width(), vienna_rect.height());
    QRect circle_rect(vienna_rect.x(), vienna_rect.y(), circle_size, circle_size);

    if (vienna_rect.width() > vienna_rect.height()) {
      circle_rect.moveLeft(vienna_rect.x() + (vienna_rect.width() - circle_size) / 2);
    } else if (vienna_rect.height() > vienna_rect.width()) {
      circle_rect.moveTop(vienna_rect.y() + (vienna_rect.height() - circle_size) / 2);
    }

    // White background circle
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, alpha));
    p.drawEllipse(circle_rect);

    // Red border ring with color coding
    QRect red_ring = circle_rect;

    p.setBrush(red_color);
    p.drawEllipse(red_ring);

    // Center white circle for text
    int ring_size = circle_size * 0.12;
    QRect center_circle = red_ring.adjusted(ring_size, ring_size, -ring_size, -ring_size);
    p.setBrush(QColor(255, 255, 255, alpha));
    p.drawEllipse(center_circle);

    // Speed value, smaller font for 3+ digits
    int font_size = (speedLimitStr.size() >= 3) ? 70 : 85;
    p.setFont(InterFont(font_size, QFont::Bold));

    p.setPen(speed_color);
    p.drawText(center_circle, Qt::AlignCenter, speedLimitStr);

    // Offset value in small circular box
    if (!speedLimitSubText.isEmpty() && hasSpeedLimit) {
      int offset_circle_size = circle_size * 0.4;
      int overlap = offset_circle_size * 0.25;
      QRect offset_circle_rect(
        circle_rect.right() - offset_circle_size/1.25 + overlap,
        circle_rect.top() - offset_circle_size/1.75 + overlap,
        offset_circle_size,
        offset_circle_size
      );

      p.setPen(QPen(QColor(77, 77, 77, 255), 6));
      p.setBrush(QColor(0, 0, 0, alpha));
      p.drawEllipse(offset_circle_rect);

      p.setFont(InterFont(offset_circle_size * speedLimitSubTextFactor, QFont::Bold));
      p.setPen(QColor(255, 255, 255, alpha));
      p.drawText(offset_circle_rect, Qt::AlignCenter, speedLimitSubText);
    }
  } else {
    // US/Canada MUTCD style sign
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, alpha));
    p.drawRoundedRect(sign_rect, 32, 32);

    // Inner border with violation color coding
    QRect inner_rect = sign_rect.adjusted(10, 10, -10, -10);
    QColor border_color = QColor(0, 0, 0, alpha);

    p.setPen(QPen(border_color, 4));
    p.setBrush(QColor(255, 255, 255, alpha));
    p.drawRoundedRect(inner_rect, 22, 22);

    // "SPEED LIMIT" text
    p.setFont(InterFont(40, QFont::DemiBold));
    p.setPen(QColor(0, 0, 0, alpha));
    p.drawText(inner_rect.adjusted(0, 10, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("SPEED"));
    p.drawText(inner_rect.adjusted(0, 50, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("LIMIT"));

    // Speed value with color coding
    p.setFont(InterFont(90, QFont::Bold));

    p.setPen(speed_color);
    p.drawText(inner_rect.adjusted(0, 80, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedLimitStr);

    // Offset value in small box
    if (!speedLimitSubText.isEmpty() && hasSpeedLimit) {
      int offset_box_size = sign_rect.width() * 0.4;
      int overlap = offset_box_size * 0.25;
      QRect offset_box_rect(
        sign_rect.right() - offset_box_size/1.5 + overlap,
        sign_rect.top() - offset_box_size/1.25 + overlap,
        offset_box_size,
        offset_box_size
      );

      int corner_radius = offset_box_size * 0.2;
      p.setPen(QPen(QColor(77, 77, 77, 255), 6));
      p.setBrush(QColor(0, 0, 0, alpha));
      p.drawRoundedRect(offset_box_rect, corner_radius, corner_radius);

      p.setFont(InterFont(offset_box_size * speedLimitSubTextFactor, QFont::Bold));
      p.setPen(QColor(255, 255, 255, alpha));
      p.drawText(offset_box_rect, Qt::AlignCenter, speedLimitSubText);
    }
  }
}

void HudRendererSP::drawUpcomingSpeedLimit(QPainter &p) {
  bool speed_limit_ahead = speedLimitAheadValid && speedLimitAhead > 0 && speedLimitAhead != speedLimit && speedLimitAheadValidFrame > 0;
  if (!speed_limit_ahead) {
    return;
  }

  auto roundToInterval = [&](float distance, int interval, int threshold) {
    int base = static_cast<int>(distance / interval) * interval;
    return (distance - base >= threshold) ? base + interval : base;
  };

  auto outputDistance = [&] {
    if (is_metric) {
      if (speedLimitAheadDistance < 50) return tr("Near");
      if (speedLimitAheadDistance >= 1000) return QString::number(speedLimitAheadDistance * METER_TO_KM, 'f', 1) + tr("km");

      int rounded = (speedLimitAheadDistance < 200) ? std::max(10, roundToInterval(speedLimitAheadDistance, 10, 5)) : roundToInterval(speedLimitAheadDistance, 100, 50);
      return QString::number(rounded) + tr("m");
    } else {
      float distance_ft = speedLimitAheadDistance * METER_TO_FOOT;
      if (distance_ft < 100) return tr("Near");
      if (distance_ft >= 900) return QString::number(speedLimitAheadDistance * METER_TO_MILE, 'f', 1) + tr("mi");

      int rounded = (distance_ft < 500) ? std::max(50, roundToInterval(distance_ft, 50, 25)) : roundToInterval(distance_ft, 100, 50);
      return QString::number(rounded) + tr("ft");
    }
  };

  QString speedStr = QString::number(std::nearbyint(speedLimitAhead));
  QString distanceStr = outputDistance();

  // Position below current speed limit sign
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;

  const int ahead_width = 170;
  const int ahead_height = 160;
  const int ahead_x = sign_x + (sign_width - ahead_width) / 2;
  const int ahead_y = sign_y + sign_height + 10;

  QRect ahead_rect(ahead_x, ahead_y, ahead_width, ahead_height);
  p.setPen(QPen(QColor(255, 255, 255, 100), 3));
  p.setBrush(QColor(0, 0, 0, 180));
  p.drawRoundedRect(ahead_rect, 16, 16);

  // "AHEAD" label
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(QColor(200, 200, 200, 255));
  p.drawText(ahead_rect.adjusted(0, 4, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("AHEAD"));

  // Speed value
  p.setFont(InterFont(70, QFont::Bold));
  p.setPen(QColor(255, 255, 255, 255));
  p.drawText(ahead_rect.adjusted(0, 38, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedStr);

  // Distance
  p.setFont(InterFont(40, QFont::Normal));
  p.setPen(QColor(180, 180, 180, 255));
  p.drawText(ahead_rect.adjusted(0, 110, 0, 0), Qt::AlignTop | Qt::AlignHCenter, distanceStr);
}

void HudRendererSP::drawRoadName(QPainter &p, const QRect &surface_rect) {
  if (!roadName || roadNameStr.isEmpty()) return;

  // Measure text to size container
  p.setFont(InterFont(46, QFont::DemiBold));
  QFontMetrics fm(p.font());

  int text_width = fm.horizontalAdvance(roadNameStr);
  int padding = 40;
  int rect_width = text_width + padding;

  // Constrain to reasonable bounds
  int min_width = 200;
  int max_width = surface_rect.width() - 40;
  rect_width = std::max(min_width, std::min(rect_width, max_width));

  // Center at top of screen
  QRect road_rect(surface_rect.width() / 2 - rect_width / 2, -4, rect_width, 60);

  p.setPen(Qt::NoPen);
  p.setBrush(QColor(0, 0, 0, 120));
  p.drawRoundedRect(road_rect, 12, 12);

  p.setPen(QColor(255, 255, 255, 200));

  // Truncate if still too long
  QString truncated = fm.elidedText(roadNameStr, Qt::ElideRight, road_rect.width() - 20);
  p.drawText(road_rect, Qt::AlignCenter, truncated);
}
