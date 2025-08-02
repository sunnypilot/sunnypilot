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

void ModelRendererSP::drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, const QRect &surface_rect) {
  auto *s = uiState();
  auto &sm = *(s->sm);
  bool blindspot = Params().getBool("BlindSpot");

  if (blindspot) {
    bool left_blindspot = sm["carState"].getCarState().getLeftBlindspot();
    bool right_blindspot = sm["carState"].getCarState().getRightBlindspot();

    //painter.setBrush(QColor::fromRgbF(1.0, 0.0, 0.0, 0.4));  // Red with alpha for blind spot

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

  ModelRenderer::drawPath(painter, model, surface_rect.height());

  drawLeadStatus(painter, surface_rect.height(), surface_rect.width());
}

void ModelRendererSP::drawLeadStatus(QPainter &painter, int height, int width) {
    auto *s = uiState();
    auto &sm = *(s->sm);

    if (!sm.alive("radarState")) return;

    const auto &radar_state = sm["radarState"].getRadarState();
    const auto &lead_one = radar_state.getLeadOne();
    const auto &lead_two = radar_state.getLeadTwo();

    // Check if we have any active leads
    bool has_lead_one = lead_one.getStatus();
    bool has_lead_two = lead_two.getStatus();

    if (!has_lead_one && !has_lead_two) {
        // Fade out status display
        lead_status_alpha = std::max(0.0f, lead_status_alpha - 0.05f);
        if (lead_status_alpha <= 0.0f) return;
    } else {
        // Fade in status display
        lead_status_alpha = std::min(1.0f, lead_status_alpha + 0.1f);
    }

    if (has_lead_one) {
        drawLeadStatusAtPosition(painter, lead_one, lead_vertices[0], height, width, "L1");
    }

    if (has_lead_two && std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0) {
        drawLeadStatusAtPosition(painter, lead_two, lead_vertices[1], height, width, "L2");
    }
}

void ModelRendererSP::drawLeadStatusAtPosition(QPainter &painter,
                                           const cereal::RadarState::LeadData::Reader &lead_data,
                                           const QPointF &chevron_pos,
                                           int height, int width,
                                           const QString &label) {

    float d_rel = lead_data.getDRel();
    float v_rel = lead_data.getVRel();
    auto *s = uiState();
    auto &sm = *(s->sm);
    float v_ego = sm["carState"].getCarState().getVEgo();

    int chevron_data = std::atoi(Params().get("ChevronInfo").c_str());

    // Calculate chevron size (same logic as drawLead)
    float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * 2.35;

    QFont content_font = painter.font();
    content_font.setPixelSize(42);
    content_font.setBold(true);
    painter.setFont(content_font);

    QFontMetrics fm(content_font);
    bool is_metric = s->scene.is_metric;

    QStringList text_lines;

    const int chevron_types = 3;
    const int chevron_all = chevron_types + 1;  // All metrics (value 4)
    QStringList chevron_text[chevron_types];
    int position;
    float val;

    // Distance display (chevron_data == 1 or all)
    if (chevron_data == 1 || chevron_data == chevron_all) {
        position = 0;
        val = std::max(0.0f, d_rel);
        QString distance_unit = is_metric ? "m" : "ft";
        if (!is_metric) {
            val *= 3.28084f; // Convert meters to feet
        }
        chevron_text[position].append(QString::number(val, 'f', 0) + " " + distance_unit);
    }

    // Absolute velocity display (chevron_data == 2 or all)
    if (chevron_data == 2 || chevron_data == chevron_all) {
        position = (chevron_data == 2) ? 0 : 1;
        val = std::max(0.0f, (v_rel + v_ego) * (is_metric ? static_cast<float>(MS_TO_KPH) : static_cast<float>(MS_TO_MPH)));
        chevron_text[position].append(QString::number(val, 'f', 0) + " " + (is_metric ? "km/h" : "mph"));
    }

    // Time-to-contact display (chevron_data == 3 or all)
    if (chevron_data == 3 || chevron_data == chevron_all) {
        position = (chevron_data == 3) ? 0 : 2;
        val = (d_rel > 0 && v_ego > 0) ? std::max(0.0f, d_rel / v_ego) : 0.0f;
        QString ttc_str = (val > 0 && val < 200) ? QString::number(val, 'f', 1) + "s" : "---";
        chevron_text[position].append(ttc_str);
    }

    // Collect all non-empty text lines
    for (int i = 0; i < chevron_types; ++i) {
        if (!chevron_text[i].isEmpty()) {
            text_lines.append(chevron_text[i]);
        }
    }

    // If no text to display, return early
    if (text_lines.isEmpty()) {
        return;
    }

    // Text box dimensions
    float str_w = 150;  // Width of text area
    float str_h = 45;   // Height per line

    // Position text below chevron, centered horizontally
    float text_x = chevron_pos.x() - str_w / 2;
    float text_y = chevron_pos.y() + sz + 15;

    // Clamp to screen bounds
    text_x = std::clamp(text_x, 10.0f, (float)width - str_w - 10);

    // Shadow offset
    QPoint shadow_offset(2, 2);

    // Draw each line of text with shadow
    for (int i = 0; i < text_lines.size(); ++i) {
        if (!text_lines[i].isEmpty()) {
            QRect textRect(text_x, text_y + (i * str_h), str_w, str_h);

            // Draw shadow
            painter.setPen(QColor(0x0, 0x0, 0x0, (int)(200 * lead_status_alpha)));
            painter.drawText(textRect.translated(shadow_offset.x(), shadow_offset.y()),
                           Qt::AlignBottom | Qt::AlignHCenter, text_lines[i]);

            // Determine text color based on content and danger level
            QColor text_color;

            // Check if this is a distance line (contains 'm' or 'ft')
            if (text_lines[i].contains("m") || text_lines[i].contains("ft")) {
                if (d_rel < 20.0f) {
                    text_color = QColor(255, 80, 80, (int)(255 * lead_status_alpha)); // Red - danger
                } else if (d_rel < 40.0f) {
                    text_color = QColor(255, 200, 80, (int)(255 * lead_status_alpha)); // Yellow - caution
                } else {
                    text_color = QColor(80, 255, 120, (int)(255 * lead_status_alpha)); // Green - safe
                }
            }
            else {
                text_color = QColor(0xff, 0xff, 0xff, (int)(255 * lead_status_alpha)); // White for other lines
            }

            // Draw main text
            painter.setPen(text_color);
            painter.drawText(textRect, Qt::AlignBottom | Qt::AlignHCenter, text_lines[i]);
        }
    }

    // Reset pen
    painter.setPen(Qt::NoPen);
}
