#pragma once

#include <QPainter>
#include <QPolygonF>

#ifdef SUNNYPILOT
#include "selfdrive/ui/sunnypilot/ui.h"
#else
#include "selfdrive/ui/ui.h"
#endif

constexpr int CLIP_MARGIN = 500;
constexpr float MIN_DRAW_DISTANCE = 10.0;
constexpr float MAX_DRAW_DISTANCE = 100.0;

inline int get_path_length_idx(const cereal::XYZTData::Reader &line, const float path_height) {
  const auto &line_x = line.getX();
  int max_idx = 0;
  for (int i = 1; i < line_x.size() && line_x[i] <= path_height; ++i) {
    max_idx = i;
  }
  return max_idx;
}

class ModelRenderer {
public:
  virtual ~ModelRenderer() = default;

  ModelRenderer() {}
  void setTransform(const Eigen::Matrix3f &transform) { car_space_transform = transform; }
  void draw(QPainter &painter, const QRect &surface_rect);
  void LongFuel(QPainter &p, int height, int width);
  void LateralFuel(QPainter &p, int height, int width);

protected:
  bool mapToScreen(float in_x, float in_y, float in_z, QPointF *out);
  void mapLineToPolygon(const cereal::XYZTData::Reader &line, float y_off, float z_off,
                        QPolygonF *pvd, int max_idx, bool allow_invert = true);
  void drawLead(QPainter &painter, const cereal::RadarState::LeadData::Reader &lead_data, const QPointF &vd, const QRect &surface_rect);
  void update_leads(const cereal::RadarState::Reader &radar_state, const cereal::XYZTData::Reader &line);
  virtual void update_model(const cereal::ModelDataV2::Reader &model, const cereal::RadarState::LeadData::Reader &lead);
  void drawLaneLines(QPainter &painter);
  void drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, int height, int width);
  virtual void drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, const QRect &surface_rect) {
    drawPath(painter, model, surface_rect.height(), surface_rect.width());
  }

  // Gauge helper methods
  void drawGaugeBackground(QPainter &painter, qreal centerX, qreal centerY);
  void drawGaugeArc(QPainter &painter, qreal centerX, qreal centerY,
                    float value, bool isPositive, const QString &label);
  QColor getIndicatorColor(float absoluteValue, float lowThreshold, float highThreshold);
  int calculateSpanAngle(float absoluteValue, float maxValue);


  void updatePathGradient(QLinearGradient &bg);
  QColor blendColors(const QColor &start, const QColor &end, float t);

  bool longitudinal_control = false;
  bool experimental_mode = false;
  float blend_factor = 1.0f;
  bool prev_allow_throttle = true;
  float lane_line_probs[4] = {};
  float road_edge_stds[2] = {};
  float path_offset_z = 1.22f;
  QPolygonF track_vertices;
  QPolygonF lane_line_vertices[4] = {};
  QPolygonF road_edge_vertices[2] = {};
  QPointF lead_vertices[2] = {};
  Eigen::Matrix3f car_space_transform = Eigen::Matrix3f::Zero();
  QRectF clip_region;

  // Gauge configuration constants
  static constexpr qreal GAUGE_SIZE = 140.0;
  static constexpr qreal BACKGROUND_SIZE_MULTIPLIER = 1.4;
  static constexpr qreal GAUGE_PEN_WIDTH = 30.0;
  static constexpr qreal BORDER_PEN_WIDTH = 2.0;
  static constexpr int SEMICIRCLE_SPAN = 180 * 16;
  static constexpr int QUARTER_CIRCLE_SPAN = 90 * 16;
  static constexpr int STARTING_ANGLE = 90 * 16;
  static constexpr qreal MIN_THRESHOLD = 0.01;

  // Color constants - Note: QColor cannot be constexpr, use inline static const instead
  inline static const QColor BACKGROUND_COLOR = QColor(0, 0, 0, 80);
  inline static const QColor BORDER_COLOR = QColor(0, 0, 0, 100);
  inline static const QColor GAUGE_BACKGROUND_COLOR = QColor(50, 50, 50);
  inline static const QColor LOW_INDICATOR_COLOR = QColor(23, 241, 66, 200);
  inline static const QColor MODERATE_INDICATOR_COLOR = QColor(255, 166, 0, 200);
  inline static const QColor HIGH_INDICATOR_COLOR = QColor(245, 0, 0, 200);
};
