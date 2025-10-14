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
  const auto &car_state = sm["carState"].getCarState();

  update_model(model, lead_one);
  drawLaneLines(painter);

  if (s->scene.rainbow_mode) {
    drawRainbowPath(painter, surface_rect);
  } else {
    ModelRenderer::drawPath(painter, model, surface_rect.height(), surface_rect.width());
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

  if (s->scene.blindspot_ui) {
    const bool left_blindspot = car_state.getLeftBlindspot();
    const bool right_blindspot = car_state.getRightBlindspot();
    drawBlindspot(painter, surface_rect, left_blindspot, right_blindspot);
  }
  drawLeadStatus(painter, surface_rect.height(), surface_rect.width());

  painter.restore();
}

void ModelRendererSP::drawBlindspot(QPainter &painter, const QRect &surface_rect, bool left_blindspot, bool right_blindspot) {
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

void ModelRendererSP::drawLeadStatus(QPainter &painter, int height, int width) {
  auto *s = uiState();
  auto &sm = *(s->sm);

  bool longitudinal_control = sm["carParams"].getCarParams().getOpenpilotLongitudinalControl();
  if (!longitudinal_control) {
    lead_status_alpha = std::max(0.0f, lead_status_alpha - 0.05f);
    return;
  }

  if (!sm.alive("radarState")) {
    lead_status_alpha = std::max(0.0f, lead_status_alpha - 0.05f);
    return;
  }

  const auto &radar_state = sm["radarState"].getRadarState();
  const auto &lead_one = radar_state.getLeadOne();
  const auto &lead_two = radar_state.getLeadTwo();

  bool has_lead_one = lead_one.getStatus();
  bool has_lead_two = lead_two.getStatus();

  if (!has_lead_one && !has_lead_two) {
    lead_status_alpha = std::max(0.0f, lead_status_alpha - 0.05f);
    if (lead_status_alpha <= 0.0f) return;
  } else {
    lead_status_alpha = std::min(1.0f, lead_status_alpha + 0.1f);
  }

  if (has_lead_one) {
    drawLeadStatusPosition(painter, lead_one, lead_vertices[0], height, width);
  }

  if (has_lead_two && std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0) {
    drawLeadStatusPosition(painter, lead_two, lead_vertices[1], height, width);
  }
}

void ModelRendererSP::drawLeadStatusPosition(QPainter &painter, const cereal::RadarState::LeadData::Reader &lead_data,
                                             const QPointF &chevron_pos, int height, int width) {
  float d_rel = lead_data.getDRel();
  float v_rel = lead_data.getVRel();
  auto *s = uiState();
  auto &sm = *(s->sm);
  float v_ego = sm["carState"].getCarState().getVEgo();

  int chevron_data = s->scene.chevron_info;
  float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * 2.35;

  QFont content_font = painter.font();
  content_font.setPixelSize(50);
  content_font.setBold(true);
  painter.setFont(content_font);

  bool is_metric = s->scene.is_metric;
  QStringList text_lines;
  const int chevron_all = 4;
  QStringList chevron_text[3];

  // Distance display
  if (chevron_data == 1 || chevron_data == chevron_all) {
    int pos = 0;
    float val = std::max(0.0f, d_rel);
    QString unit = is_metric ? "m" : "ft";
    if (!is_metric) val *= 3.28084f;
    chevron_text[pos].append(QString::number(val, 'f', 0) + " " + unit);
  }

  // Speed display
  if (chevron_data == 2 || chevron_data == chevron_all) {
    int pos = (chevron_data == 2) ? 0 : 1;
    float multiplier = is_metric ? static_cast<float>(MS_TO_KPH) : static_cast<float>(MS_TO_MPH);
    float val = std::max(0.0f, (v_rel + v_ego) * multiplier);
    QString unit = is_metric ? "km/h" : "mph";
    chevron_text[pos].append(QString::number(val, 'f', 0) + " " + unit);
  }

  // Time to contact
  if (chevron_data == 3 || chevron_data == chevron_all) {
    int pos = (chevron_data == 3) ? 0 : 2;
    float val = (d_rel > 0 && v_ego > 0) ? std::max(0.0f, d_rel / v_ego) : 0.0f;
    QString ttc = (val > 0 && val < 200) ? QString::number(val, 'f', 1) + "s" : "---";
    chevron_text[pos].append(ttc);
  }

  for (int i = 0; i < 3; ++i) {
    if (!chevron_text[i].isEmpty()) text_lines.append(chevron_text[i]);
  }

  if (text_lines.isEmpty()) return;

  QFontMetrics fm(content_font);
  float text_width = 120.0f;
  for (const QString &line : text_lines) {
    text_width = std::max(text_width, fm.horizontalAdvance(line) + 20.0f);
  }
  text_width = std::min(text_width, 250.0f);

  float line_height = 50.0f;
  float total_height = text_lines.size() * line_height;
  float margin = 20.0f;

  float text_y = chevron_pos.y() + sz + 15;
  if (text_y + total_height > height - margin) {
    float y_max = chevron_pos.y() > (height - margin) ? (height - margin) : chevron_pos.y();
    text_y = y_max - 15 - total_height;
    text_y = std::max(margin, text_y);
  }

  float text_x = chevron_pos.x() - text_width / 2;
  text_x = std::clamp(text_x, margin, (float)width - text_width - margin);

  QPoint shadow_offset(2, 2);
  QColor text_color = QColor(255, 255, 255, (int)(255 * lead_status_alpha));
  for (int i = 0; i < text_lines.size(); ++i) {
    float y = text_y + (i * line_height);
    if (y + line_height > height - margin) break;

    QRect rect(text_x, y, text_width, line_height);

    // Draw shadow
    painter.setPen(QColor(0, 0, 0, (int)(200 * lead_status_alpha)));
    painter.drawText(rect.translated(shadow_offset), Qt::AlignCenter, text_lines[i]);
    painter.setPen(text_color);
    painter.drawText(rect, Qt::AlignCenter, text_lines[i]);
  }

  painter.setPen(Qt::NoPen);
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
