/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/onroad/hud.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/helpers.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/developer_ui/developer_ui.h"

constexpr int SPEED_LIMIT_AHEAD_VALID_FRAME_THRESHOLD = 5;

class HudRendererSP : public HudRenderer {
  Q_OBJECT

public:
  HudRendererSP();
  void updateState(const UIState &s) override;
  void draw(QPainter &p, const QRect &surface_rect) override;

private:
  Params params;
  void drawText(QPainter &p, int x, int y, const QString &text, QColor color = Qt::white);
  void drawRightDevUI(QPainter &p, int x, int y);
  int drawRightDevUIElement(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color);
  int drawBottomDevUIElement(QPainter &p, int x, int y, const QString &value, const QString &label, const QString &units, QColor &color);
  void drawBottomDevUI(QPainter &p, int x, int y);
  void drawStandstillTimer(QPainter &p, int x, int y);
  bool pulseElement(int frame);
  void drawSmartCruiseControlOnroadIcon(QPainter &p, const QRect &surface_rect, int x_offset, int y_offset, std::string name);
  void drawSpeedLimitSigns(QPainter &p);
  void drawUpcomingSpeedLimit(QPainter &p);
  void drawRoadName(QPainter &p, const QRect &surface_rect);

  bool lead_status;
  float lead_d_rel;
  float lead_v_rel;
  bool torqueLateral;
  float angleSteers;
  float desiredCurvature;
  float curvature;
  float roll;
  int memoryUsagePercent;
  int devUiInfo;
  float gpsAccuracy;
  float altitude;
  float vEgo;
  float aEgo;
  float steeringTorqueEps;
  float bearingAccuracyDeg;
  float bearingDeg;
  bool torquedUseParams;
  float latAccelFactorFiltered;
  float frictionCoefficientFiltered;
  bool liveValid;
  QString speedUnit;
  bool latActive;
  bool steerOverride;
  bool reversing;
  cereal::CarParams::SteerControlType steerControlType;
  cereal::CarControl::Actuators::Reader actuators;
  bool standstillTimer;
  bool isStandstill;
  float standstillElapsedTime;
  bool longOverride;
  bool smartCruiseControlVisionEnabled;
  bool smartCruiseControlVisionActive;
  int smartCruiseControlVisionFrame;
  bool smartCruiseControlMapEnabled;
  bool smartCruiseControlMapActive;
  int smartCruiseControlMapFrame;
  float speedLimit;
  float speedLimitLast;
  float speedLimitOffset;
  bool speedLimitValid;
  bool speedLimitLastValid;
  float speedLimitFinalLast;
  bool speedLimitAheadValid;
  float speedLimitAhead;
  float speedLimitAheadDistance;
  float speedLimitAheadDistancePrev;
  int speedLimitAheadValidFrame;
  SpeedLimitMode speedLimitMode = SpeedLimitMode::OFF;
  bool roadName;
  QString roadNameStr;
};
