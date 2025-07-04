#pragma once

#include <QPainter>

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif

class HudRenderer : public QObject {
  Q_OBJECT

public:
  HudRenderer();
  virtual ~HudRenderer() = default;
  virtual void updateState(const UIState &s);
  virtual void draw(QPainter &p, const QRect &surface_rect);

protected:
  void drawSetSpeed(QPainter &p, const QRect &surface_rect);
  void drawCurrentSpeed(QPainter &p, const QRect &surface_rect);
  void drawText(QPainter &p, int x, int y, const QString &text, int alpha = 255);
  void drawSpeedLimitSigns(QPainter &p, const QRect &rect);
  void drawVisionTurnControl(QPainter &p, const QRect &surface_rect);
  QColor interpColor(float x, const std::vector<float> &x_vals, const std::vector<QColor> &colors);

  // Additional drawing methods from implementation
  void drawUpcomingSpeedLimit(QPainter &p, const QRect &surface_rect);
  void drawSLCStateIndicator(QPainter &p, const QRect &surface_rect);
  void drawRoadName(QPainter &p, const QRect &surface_rect);

  // Display flags
  bool show_slc = false;
  bool over_speed_limit = false;

  // Speed Limit Control (SLC)
  float slc_speed_limit = 0.0;
  float slc_speed_offset = 0.0;
  cereal::LongitudinalPlanSP::SpeedLimitControlState slc_state = cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE;
  float dist_to_speed_limit = 0.0;

  // Speed violation levels
  int speed_violation_level = 0;

  // Upcoming speed limit data
  bool speed_limit_ahead_valid = false;
  float speed_limit_ahead = 0.0;
  float speed_limit_ahead_distance = 0.0;

  // Road information
  QString road_name;

  float speed = 0;
  float set_speed = 0;
  bool is_cruise_set = false;
  bool is_cruise_available = true;
  bool is_metric = false;
  bool v_ego_cluster_seen = false;
  int status = STATUS_DISENGAGED;
};
