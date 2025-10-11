/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/onroad/model.h"


void ModelRendererSP::update_model(const cereal::ModelDataV2::Reader &model, const cereal::RadarState::LeadData::Reader &lead) {
  ModelRenderer::update_model(model, lead);
  const auto &model_position = model.getPosition();
  const auto &lane_lines = model.getLaneLines();
  float max_distance = std::clamp(*(model_position.getX().end() - 1), MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE);
  int max_idx = get_path_length_idx(lane_lines[0], max_distance);
  // update blindspot vertices
  float max_distance_barrier = 100;
  int max_idx_barrier = std::min(max_idx, get_path_length_idx(lane_lines[0], max_distance_barrier));
  mapLineToPolygon(model.getLaneLines()[1], 0.2, -0.05, &left_blindspot_vertices, max_idx_barrier);
  mapLineToPolygon(model.getLaneLines()[2], 0.2, -0.05, &right_blindspot_vertices, max_idx_barrier);
}

void ModelRendererSP::draw(QPainter &painter, const QRect &surface_rect) {
  auto *s = uiState();
  auto &sm = *(s->sm);

  if (sm.rcv_frame("liveCalibration") < s->scene.started_frame ||
      sm.rcv_frame("modelV2") < s->scene.started_frame) {
    return;
  }

  clip_region = surface_rect.adjusted(-CLIP_MARGIN, -CLIP_MARGIN, CLIP_MARGIN, CLIP_MARGIN);
  experimental_mode = sm["selfdriveState"].getSelfdriveState().getExperimentalMode();
  longitudinal_control = sm["carParams"].getCarParams().getOpenpilotLongitudinalControl();
  path_offset_z = sm["liveCalibration"].getLiveCalibration().getHeight()[0];

  painter.save();

  const auto &model = sm["modelV2"].getModelV2();
  const auto &radar_state = sm["radarState"].getRadarState();
  const auto &lead_one = radar_state.getLeadOne();

  update_model(model, lead_one);
  drawLaneLines(painter);

  bool blindspot = Params().getBool("BlindSpot");
  bool rocketfuel = s->scene.rocket_fuel;
  bool rainbow = Params().getBool("RainbowMode");

  bool left_blindspot = sm["carState"].getCarState().getLeftBlindspot();
  bool right_blindspot = sm["carState"].getCarState().getRightBlindspot();
  float accel = sm["carControl"].getCarControl().getActuators().getAccel();

  if (blindspot) {
    drawBlindspot(painter, surface_rect, left_blindspot, right_blindspot);
  }

  if (rainbow) {
    drawRainbowPath(painter, surface_rect);
  } else {
    ModelRenderer::drawPath(painter, model, surface_rect);
  }

  if (rocketfuel) {
    drawRocketFuel(painter, surface_rect, accel);
  }

  if (longitudinal_control && sm.alive("radarState")) {
    update_leads(radar_state, model.getPosition());
    const auto &lead_two = radar_state.getLeadTwo();
    if (lead_one.getStatus()) {
      drawLead(painter, lead_one, lead_vertices[0], surface_rect);
    }
    if (lead_two.getStatus() && (std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0)) {
      drawLead(painter, lead_two, lead_vertices[1], surface_rect);
    }
  }
  drawLeadStatus(painter, surface_rect.height(), surface_rect.width());

  painter.restore();
}

void ModelRendererSP::drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, const QRect &surface_rect) {
  ModelRenderer::drawPath(painter, model, surface_rect);
}

void ModelRendererSP::drawBlindspot(QPainter &painter, const QRect &surface_rect,
                                     bool left_blindspot, bool right_blindspot) {
  if (left_blindspot && !left_blindspot_vertices.isEmpty()) {
    QLinearGradient gradient(0, 0, surface_rect.width(), 0); // Horizontal gradient from left to right
    gradient.setColorAt(0.0, QColor(255, 165, 0, 102)); // Orange with alpha
    gradient.setColorAt(1.0, QColor(255, 255, 0, 102)); // Yellow with alpha
    painter.setBrush(gradient);
    painter.drawPolygon(left_blindspot_vertices);
  }

  if (right_blindspot && !right_blindspot_vertices.isEmpty()) {
    QLinearGradient gradient(surface_rect.width(), 0, 0, 0); // Horizontal gradient from right to left
    gradient.setColorAt(0.0, QColor(255, 165, 0, 102)); // Orange with alpha
    gradient.setColorAt(1.0, QColor(255, 255, 0, 102)); // Yellow with alpha
    painter.setBrush(gradient);
    painter.drawPolygon(right_blindspot_vertices);
  }
}

void ModelRendererSP::drawRainbowPath(QPainter &painter, const QRect &surface_rect) {
  // Simple time-based animation
  float time_offset = std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count() / 1000.0f;

  // simple linear gradient from bottom to top
  QLinearGradient bg(0, surface_rect.height(), 0, 0);

  // evenly spaced colors across the spectrum
  // The animation shifts the entire spectrum smoothly
  float animation_speed = 40.0f; // speed vroom vroom
  float hue_offset = fmod(time_offset * animation_speed, 360.0f);

  // 6-8 color stops for smooth transitions more color makes it laggy
  const int num_stops = 7;
  for (int i = 0; i < num_stops; i++) {
    float position = static_cast<float>(i) / (num_stops - 1);

    float hue = fmod(hue_offset + position * 360.0f, 360.0f);
    float saturation = 0.9f;
    float lightness = 0.6f;

    // Alpha fades out towards the far end of the path
    float alpha = 0.8f * (1.0f - position * 0.3f);

    QColor color = QColor::fromHslF(hue / 360.0f, saturation, lightness, alpha);
    bg.setColorAt(position, color);
  }

  painter.setBrush(bg);
  painter.drawPolygon(track_vertices);
}

void ModelRendererSP::drawRocketFuel(QPainter &painter, const QRect &surface_rect, float accel) {
  int widgetHeight = surface_rect.height();
  float halfHeightAbs = std::abs(accel) * widgetHeight / 2.0f;
  const float scannerWidth = 15;
  QRect scannerRect;

  if (accel > 0) {
    painter.setBrush(QColor(0, 245, 0, 200));
    scannerRect = QRect(0, widgetHeight / 2 - halfHeightAbs, scannerWidth, halfHeightAbs);
  } else {
    painter.setBrush(QColor(245, 0, 0, 200));
    scannerRect = QRect(0, widgetHeight / 2, scannerWidth, halfHeightAbs);
  }

  painter.drawRect(scannerRect);
}
