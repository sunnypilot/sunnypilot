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
  void drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color);
  // Drawing helpers
  void drawSpeedLimitSigns(QPainter &p, const QRect &rect);



  // image assets
  QPixmap left_img;
  QPixmap right_img;
  QPixmap map_img;

  // navigation speed limits
  float nav_speed_limit = 0.0;
  bool has_us_speed_limit = false;
  bool has_eu_speed_limit = false;
  // Display flags
  bool show_slc = false;
  bool over_speed_limit = false;
  //bool show_vtc = false;
  //bool show_turn_speed = false;

  // Speed Limit Control (SLC)
  float slc_speed_limit = 0.0;
  float slc_speed_offset = 0.0;
  int slc_state = 0;
  int slc_distance = 0;
  bool is_map_speed_limit = false;

  float speed = 0;
  float set_speed = 0;
  bool is_cruise_set = false;
  bool is_cruise_available = true;
  bool is_metric = false;
  bool v_ego_cluster_seen = false;
  int status = STATUS_DISENGAGED;
};
