/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/qt/onroad/model.h"

class ModelRendererSP : public ModelRenderer {
public:
  ModelRendererSP() = default;

private:
  void update_model(const cereal::ModelDataV2::Reader &model, const cereal::RadarState::LeadData::Reader &lead) override;
  void drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, const QRect &rect) override;
  void drawBreathingRainbow(QPainter &painter, const QRect &surface_rect, float time_offset);
  void drawFlowingRainbow(QPainter &painter, const QRect &surface_rect, float time_offset, float v_ego);
  void drawDynamicSpectrum(QPainter &painter, const QRect &surface_rect, float time_offset, float v_ego);
  void drawPlasmaRainbow(QPainter &painter, const QRect &surface_rect, float time_offset, float v_ego);
  // Lead status display methods
  void drawLeadStatus(QPainter &painter, int height, int width);
  void drawLeadStatusAtPosition(QPainter &painter,
                               const cereal::RadarState::LeadData::Reader &lead_data,
                               const QPointF &chevron_pos,
                               int height, int width,
                               const QString &label);

  // Lead status display methods
  void drawLeadStatus(QPainter &painter, int height, int width);
  void drawLeadStatusAtPosition(QPainter &painter,
                               const cereal::RadarState::LeadData::Reader &lead_data,
                               const QPointF &chevron_pos,
                               int height, int width,
                               const QString &label);

  QPolygonF left_blindspot_vertices;
  QPolygonF right_blindspot_vertices;

  // Lead status animation
  float lead_status_alpha = 0.0f;
};
