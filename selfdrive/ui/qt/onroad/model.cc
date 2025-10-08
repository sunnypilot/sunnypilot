#include "selfdrive/ui/qt/onroad/model.h"
#include <QPainterPath>
#include <algorithm>

void ModelRenderer::drawRadarPoint(QPainter &painter, const QPointF &pos, float v_rel, float radius) {
  painter.setBrush(QColor(255, 255, 255, 200));
  painter.setPen(Qt::NoPen);
  painter.drawEllipse(pos, radius, radius);
}

void ModelRenderer::draw(QPainter &painter, const QRect &surface_rect) {
  static double last_draw_t = millis_since_boot();
  static float avg_frame_time = 50.0f;
  static float avg_fps = 20.0f;

  double frame_now = millis_since_boot();
  double frame_time_ms = frame_now - last_draw_t;
  last_draw_t = frame_now;

  float fps = (frame_time_ms > 0) ? (1000.0f / frame_time_ms) : 0.0f;

  // Stronger smoothing to reduce jutter
  const float alpha = 0.02f;  // smaller = smoother
  avg_frame_time = (1 - alpha) * avg_frame_time + alpha * frame_time_ms;
  avg_fps        = (1 - alpha) * avg_fps + alpha * fps;

  auto *s = uiState();
  auto &sm = *(s->sm);
  // Check if data is up-to-date
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
  drawPath(painter, model, surface_rect);

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

  if (s->scene.visual_radar_tracks) {
    if (sm.alive("liveTracks") && sm.rcv_frame("liveTracks") >= s->scene.started_frame) {
      const auto &tracks = sm["liveTracks"].getLiveTracks().getPoints();
      for (const auto &track : tracks) {
        if (!std::isfinite(track.getDRel()) || !std::isfinite(track.getYRel())) continue;
        float t_lag = s->scene.visual_radar_tracks_delay;
        float d_pred = track.getDRel();
        float y_pred = track.getYRel();
        if (t_lag > 0.0f) {
          d_pred += track.getVRel() * t_lag + 0.5f * track.getARel() * t_lag * t_lag;
        }
        QPointF screen_pt;
        if (mapToScreen(d_pred, -y_pred, path_offset_z, &screen_pt)) {
          drawRadarPoint(painter, screen_pt, track.getVRel(), 10);
        }
      }
    }
  }

  drawLeadStatus(painter, surface_rect.height(), surface_rect.width());

  if (s->scene.visual_fps) {
    static double last_overlay_update_t = 0.0;
    static QString cached_fps_line;
    static QString cached_frame_line;

    double now_overlay = millis_since_boot();
    if (now_overlay - last_overlay_update_t > 500.0) {
      cached_fps_line   = QString("FPS %1 / %2").arg(fps, 0, 'f', 0).arg(avg_fps, 0, 'f', 0);
      cached_frame_line = QString("FRM %1 / %2").arg(frame_time_ms, 0, 'f', 0).arg(avg_frame_time, 0, 'f', 0);
      last_overlay_update_t = now_overlay;
    }

    painter.setPen(Qt::white);
    QFont font;
    font.setFamily("FixedFont");
    font.setStyleHint(QFont::Monospace);
    font.setFixedPitch(true);
    font.setPixelSize(48);
    font.setBold(true);
    painter.setFont(font);

    int x = 30;
    int mid_y = surface_rect.center().y();
    int line_spacing = 40;

    painter.drawText(x, mid_y - line_spacing/2, cached_fps_line);
    painter.drawText(x, mid_y + line_spacing/2, cached_frame_line);
  }

  painter.restore();
}

void ModelRenderer::update_leads(const cereal::RadarState::Reader &radar_state, const cereal::XYZTData::Reader &line) {
  for (int i = 0; i < 2; ++i) {
    const auto &lead_data = (i == 0) ? radar_state.getLeadOne() : radar_state.getLeadTwo();
    if (lead_data.getStatus()) {
      float z = line.getZ()[get_path_length_idx(line, lead_data.getDRel())];
      mapToScreen(lead_data.getDRel(), -lead_data.getYRel(), z + path_offset_z, &lead_vertices[i]);
    }
  }
}

void ModelRenderer::update_model(const cereal::ModelDataV2::Reader &model, const cereal::RadarState::LeadData::Reader &lead) {
  auto *s = uiState();
  const auto &model_position = model.getPosition();
  float max_distance;
  if (s->scene.visual_style == 0) {
    max_distance = std::clamp(*(model_position.getX().end() - 1), MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE);
  } else {
    max_distance = std::clamp(*(model_position.getX().end() - 1), MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE);
  }

  // update lane lines
  const auto &lane_lines = model.getLaneLines();
  const auto &line_probs = model.getLaneLineProbs();
  int max_idx = get_path_length_idx(lane_lines[0], max_distance);
  for (int i = 0; i < std::size(lane_line_vertices); i++) {
    lane_line_probs[i] = line_probs[i];
    if (s->scene.visual_style == 2) {
      mapLineToPolygon(lane_lines[i], 0.075 * lane_line_probs[i], 0, &lane_line_vertices[i], max_idx);
    } else {
      mapLineToPolygon(lane_lines[i], 0.025 * lane_line_probs[i], 0, &lane_line_vertices[i], max_idx);
    }
  }

  // update road edges
  const auto &road_edges = model.getRoadEdges();
  const auto &edge_stds = model.getRoadEdgeStds();
  for (int i = 0; i < std::size(road_edge_vertices); i++) {
    road_edge_stds[i] = edge_stds[i];
    if (s->scene.visual_style == 2) {
      mapLineToPolygon(road_edges[i], 0.1, 0, &road_edge_vertices[i], max_idx);
    } else {
      mapLineToPolygon(road_edges[i], 0.025, 0, &road_edge_vertices[i], max_idx);
    }
  }

  // update path
  if (lead.getStatus()) {
    const float lead_d = lead.getDRel() * 2.;
    max_distance = std::clamp((float)(lead_d - fmin(lead_d * 0.35, 10.)), 0.0f, max_distance);
  }
  max_idx = get_path_length_idx(model_position, max_distance);
  mapLineToPolygon(model_position, 0.9, path_offset_z, &track_vertices, max_idx, false);
}

void ModelRenderer::drawLaneLines(QPainter &painter) {
  auto *s = uiState();
  if (s->scene.visual_style == 2) {
    QRectF r = clip_region;

    // --- Find horizon from road edges ---
    qreal horizonY = r.bottom();  // fallback
    if (!road_edge_vertices[0].isEmpty() || !road_edge_vertices[1].isEmpty()) {
      qreal leftH  = r.top();
      qreal rightH = r.top();

      if (!road_edge_vertices[0].isEmpty()) {
        leftH = std::numeric_limits<qreal>::max();
        for (const QPointF &pt : road_edge_vertices[0]) {
          if (pt.y() < leftH) leftH = pt.y();
        }
      }

      if (!road_edge_vertices[1].isEmpty()) {
        rightH = std::numeric_limits<qreal>::max();
        for (const QPointF &pt : road_edge_vertices[1]) {
          if (pt.y() < rightH) rightH = pt.y();
        }
      }

      // Pick the lower (visually deeper) horizon to ensure no gaps
      horizonY = std::max(leftH, rightH);
    }


    // --- Background ---
    // Fill above horizon: pure black
    // painter.fillRect(QRectF(r.left(), r.top(), r.width(), horizonY - 100), QColor("#000000"));


    // Fill below horizon: solid dark gray
    painter.fillRect(QRectF(r.left(), horizonY + 0, r.width(), r.bottom() - (horizonY + 0)), QColor("#111111"));


    auto buildFill = [&](const QPolygonF &edgeRibbon, bool isLeftSide) -> QPolygonF {
      if (edgeRibbon.isEmpty()) return {};

      QMap<int, QPointF> byY;
      for (const QPointF &pt : edgeRibbon) {
        int yi = int(std::round(pt.y()));
        if (!byY.contains(yi)) {
          byY[yi] = pt;
        } else {
          if (isLeftSide) {
            if (pt.x() > byY[yi].x()) byY[yi] = pt;
          } else {
            if (pt.x() < byY[yi].x()) byY[yi] = pt;
          }
        }
      }
      if (byY.isEmpty()) return {};

      QPolygonF curve;
      for (auto it = byY.cbegin(); it != byY.cend(); ++it) {
        curve << it.value();
      }
      if (curve.size() < 2) return {};

      const qreal topY = curve.first().y();
      QPolygonF fill;
      if (isLeftSide) {
        fill << QPointF(r.left(), topY);
        for (const QPointF &pt : curve) fill << pt;
        fill << QPointF(r.left(), r.bottom());
      } else {
        fill << QPointF(r.right(), topY);
        for (const QPointF &pt : curve) fill << pt;
        fill << QPointF(r.right(), r.bottom());
      }
      return fill;
    };

    // Left and right fills
    QPolygonF leftFill  = buildFill(road_edge_vertices[0], true);
    QPolygonF rightFill = buildFill(road_edge_vertices[1], false);

    if (!leftFill.isEmpty()) {
      painter.setBrush(QColor("#222222"));
      painter.drawPolygon(leftFill);
    }
    if (!rightFill.isEmpty()) {
      painter.setBrush(QColor("#222222"));
      painter.drawPolygon(rightFill);
    }

    // lanelines
    for (int i = 0; i < std::size(lane_line_vertices); ++i) {
      painter.setBrush(QColor::fromRgbF(0.902, 0.902, 0.902, std::clamp<float>(lane_line_probs[i], 0.0, 0.7)));
      painter.drawPolygon(lane_line_vertices[i]);
    }

    // road edges
    for (int i = 0; i < std::size(road_edge_vertices); ++i) {
      painter.setBrush(QColor(0x55, 0x55, 0x55, 255));
      painter.drawPolygon(road_edge_vertices[i]);
    }

    // Gradient band across horizon
    QLinearGradient bgGrad(r.left(), horizonY - 100, r.left(), horizonY + 100);
    bgGrad.setColorAt(0.0, QColor("#000000"));  // top of band
    bgGrad.setColorAt(0.5, QColor("#111111"));  // middle blend
    bgGrad.setColorAt(1.0, QColor("#111111"));  // bottom of band
    painter.fillRect(QRectF(r.left(), horizonY - 200, r.width(), 200), bgGrad);

  } else {
    // lanelines
    for (int i = 0; i < std::size(lane_line_vertices); ++i) {
      painter.setBrush(QColor::fromRgbF(1.0, 1.0, 1.0, std::clamp<float>(lane_line_probs[i], 0.0, 0.7)));
      painter.drawPolygon(lane_line_vertices[i]);
    }

    // road edges
    for (int i = 0; i < std::size(road_edge_vertices); ++i) {
      painter.setBrush(QColor::fromRgbF(1.0, 0, 0, std::clamp<float>(1.0 - road_edge_stds[i], 0.0, 1.0)));
      painter.drawPolygon(road_edge_vertices[i]);
    }
  }
}

void ModelRenderer::drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, int height) {
  QLinearGradient bg(0, height, 0, 0);
  if (experimental_mode) {
    // The first half of track_vertices are the points for the right side of the path
    const auto &acceleration = model.getAcceleration().getX();
    const int max_len = std::min<int>(track_vertices.length() / 2, acceleration.size());

    for (int i = 0; i < max_len; ++i) {
      // Some points are out of frame
      int track_idx = max_len - i - 1;  // flip idx to start from bottom right
      if (track_vertices[track_idx].y() < 0 || track_vertices[track_idx].y() > height) continue;

      // Flip so 0 is bottom of frame
      float lin_grad_point = (height - track_vertices[track_idx].y()) / height;

      // speed up: 120, slow down: 0
      float path_hue = fmax(fmin(60 + acceleration[i] * 35, 120), 0);
      // FIXME: painter.drawPolygon can be slow if hue is not rounded
      path_hue = int(path_hue * 100 + 0.5) / 100;

      float saturation = fmin(fabs(acceleration[i] * 1.5), 1);
      float lightness = util::map_val(saturation, 0.0f, 1.0f, 0.95f, 0.62f);        // lighter when grey
      float alpha = util::map_val(lin_grad_point, 0.75f / 2.f, 0.75f, 0.4f, 0.0f);  // matches previous alpha fade
      bg.setColorAt(lin_grad_point, QColor::fromHslF(path_hue / 360., saturation, lightness, alpha));

      // Skip a point, unless next is last
      i += (i + 2) < max_len ? 1 : 0;
    }

  } else {
    updatePathGradient(bg);
  }

  painter.setBrush(bg);
  painter.drawPolygon(track_vertices);
}

void ModelRenderer::updatePathGradient(QLinearGradient &bg) {
  static const QColor throttle_colors[] = {
      QColor::fromHslF(148. / 360., 0.94, 0.51, 0.4),
      QColor::fromHslF(112. / 360., 1.0, 0.68, 0.35),
      QColor::fromHslF(112. / 360., 1.0, 0.68, 0.0)};

  static const QColor no_throttle_colors[] = {
      QColor::fromHslF(148. / 360., 0.0, 0.95, 0.4),
      QColor::fromHslF(112. / 360., 0.0, 0.95, 0.35),
      QColor::fromHslF(112. / 360., 0.0, 0.95, 0.0),
  };

  // Transition speed; 0.1 corresponds to 0.5 seconds at UI_FREQ
  constexpr float transition_speed = 0.1f;

  // Start transition if throttle state changes
  bool allow_throttle = (*uiState()->sm)["longitudinalPlan"].getLongitudinalPlan().getAllowThrottle() || !longitudinal_control;
  if (allow_throttle != prev_allow_throttle) {
    prev_allow_throttle = allow_throttle;
    // Invert blend factor for a smooth transition when the state changes mid-animation
    blend_factor = std::max(1.0f - blend_factor, 0.0f);
  }

  const QColor *begin_colors = allow_throttle ? no_throttle_colors : throttle_colors;
  const QColor *end_colors = allow_throttle ? throttle_colors : no_throttle_colors;
  if (blend_factor < 1.0f) {
    blend_factor = std::min(blend_factor + transition_speed, 1.0f);
  }

  // Set gradient colors by blending the start and end colors
  bg.setColorAt(0.0f, blendColors(begin_colors[0], end_colors[0], blend_factor));
  bg.setColorAt(0.5f, blendColors(begin_colors[1], end_colors[1], blend_factor));
  bg.setColorAt(1.0f, blendColors(begin_colors[2], end_colors[2], blend_factor));
}

QColor ModelRenderer::blendColors(const QColor &start, const QColor &end, float t) {
  if (t == 1.0f) return end;
  return QColor::fromRgbF(
      (1 - t) * start.redF() + t * end.redF(),
      (1 - t) * start.greenF() + t * end.greenF(),
      (1 - t) * start.blueF() + t * end.blueF(),
      (1 - t) * start.alphaF() + t * end.alphaF());
}


void ModelRenderer::drawLeadStatus(QPainter &painter, int height, int width) {
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

    // Draw status for each lead vehicle under its chevron
    if (true) {
        drawLeadStatusAtPosition(painter, lead_one, lead_vertices[0], height, width, "L1");
    }

    if (has_lead_two && std::abs(lead_one.getDRel() - lead_two.getDRel()) > 3.0) {
        drawLeadStatusAtPosition(painter, lead_two, lead_vertices[1], height, width, "L2");
    }
}

void ModelRenderer::drawLeadStatusAtPosition(QPainter &painter,
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
    content_font.setPixelSize(35);
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
            // Enhanced color coding for time-to-contact
            else if (text_lines[i].contains("s") && !text_lines[i].contains("---")) {
                float ttc_val = text_lines[i].left(text_lines[i].length() - 1).toFloat();
                if (ttc_val < 3.0f) {
                    text_color = QColor(255, 80, 80, (int)(255 * lead_status_alpha)); // Red - urgent
                } else if (ttc_val < 6.0f) {
                    text_color = QColor(255, 200, 80, (int)(255 * lead_status_alpha)); // Yellow - caution
                } else {
                    text_color = QColor(0xff, 0xff, 0xff, (int)(255 * lead_status_alpha)); // White - safe
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

void ModelRenderer::drawLead(QPainter &painter, const cereal::RadarState::LeadData::Reader &lead_data,
                             const QPointF &vd, const QRect &surface_rect) {
  auto *s = uiState();
  const float speedBuff = 10.;
  const float leadBuff = 40.;
  const float d_rel = lead_data.getDRel();
  const float v_rel = lead_data.getVRel();

  float fillAlpha = 0;
  if (d_rel < leadBuff) {
    fillAlpha = 255 * (1.0 - (d_rel / leadBuff));
    if (v_rel < 0) {
      fillAlpha += 255 * (-1 * (v_rel / speedBuff));
    }
    fillAlpha = (int)(fmin(fillAlpha, 255));
  }

  float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * 2.35;
  float x = std::clamp<float>(vd.x(), 0.f, surface_rect.width() - sz / 2);
  float y = std::min<float>(vd.y(), surface_rect.height() - sz * 0.6);

  float g_xo = sz / 5;
  float g_yo = sz / 10;

  QPointF glow[] = {{x + (sz * 1.35) + g_xo, y + sz + g_yo}, {x, y - g_yo}, {x - (sz * 1.35) - g_xo, y + sz + g_yo}};
  if (s->scene.visual_style == 2) {
    painter.setBrush(QColor(0xE6, 0xE6, 0xE6, 255));
  } else {
    painter.setBrush(QColor(218, 202, 37, 255));
  }
  painter.drawPolygon(glow, std::size(glow));

  // chevron
  QPointF chevron[] = {{x + (sz * 1.25), y + sz}, {x, y}, {x - (sz * 1.25), y + sz}};
  if (s->scene.visual_style == 2) {
    painter.setBrush(QColor(0, 0, 0, fillAlpha));
  } else {
    painter.setBrush(QColor(201, 34, 49, fillAlpha));
  }
  painter.drawPolygon(chevron, std::size(chevron));
}

float mapRange(float x, float in_min, float in_max, float out_min, float out_max) {
  x = std::clamp(x, in_min, in_max);
  return out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min);
}

// Projects a point in car space to the corresponding point in full frame image space.
bool ModelRenderer::mapToScreen(float in_x, float in_y, float in_z, QPointF *out) {
  auto *s = uiState();
  auto &sm = *(s->sm);
  float blend_speed_mph = fabsf(sm["carState"].getCarState().getVEgo() * 2.23694f);  // convert to mph

  // Normal perspective (3D)
  Eigen::Vector3f input(in_x, in_y, in_z);

  if (s->scene.visual_style_zoom == 1 && s->scene.visual_style != 0) {
    float IN_X_OFFSET = mapRange(blend_speed_mph, 20.0f, 50.0f, 0.0f, 24.0f);
    float IN_Y_OFFSET = mapRange(blend_speed_mph, 20.0f, 50.0f, 1.0f, 2.0f);
    float IN_Z_OFFSET = mapRange(blend_speed_mph, 20.0f, 50.0f, 0.0f, 5.0f);
    float PITCH_DEG = mapRange(blend_speed_mph, 20.0f, 50.0f, 0.0f, 5.0f);

    input = Eigen::Vector3f(in_x + IN_X_OFFSET, in_y / IN_Y_OFFSET, in_z + IN_Z_OFFSET);
    Eigen::AngleAxisf pitch_rot(PITCH_DEG * M_PI / 180.0f, Eigen::Vector3f::UnitY());
    input = pitch_rot * input;
  }

  auto pt = car_space_transform * input;
  bool normal_valid = (pt.z() > 1e-3f &&
                       std::isfinite(pt.x()) && std::isfinite(pt.y()));
  QPointF normal_view;
  if (normal_valid) {
    normal_view = QPointF(pt.x() / pt.z(), pt.y() / pt.z());
  }

  const float base_scale_x = 20.0f;  // in/out 20 (far/fast) 100 (close/slow)
  const float base_scale_y = 15.0f;  // squish (was 20.0f)
  const float y_offset = 450.0f;

  float factor_scale_x = 0.0f;
  if (blend_speed_mph > 0.0f) {
    factor_scale_x = mapRange(blend_speed_mph, 0.0f, 50.0f, 100.0f, 0.0f);
  }

  float scale_x = base_scale_x + factor_scale_x;
  float scale_y = base_scale_y;

  QPointF topdown_view(
    clip_region.center().x() + in_y * scale_x,
    (clip_region.bottom() - y_offset) - in_x * scale_y
  );

  // Force top-down if VisualStyle == 3
  // if (s->scene.visual_style == 3) {
  //   *out = topdown_view;
  //   return clip_region.contains(*out);
  // }

  // Blending mode
  if (s->scene.visual_style_overhead_zoom == 1 && s->scene.visual_style != 0) {
    static float blend = 0.0f;        // 0 = 3D, 1 = 2D
    static float target_blend = 0.0f; // where we want to go
    static double last_t = millis_since_boot();

    // Hysteresis logic
    if (target_blend < 0.5f && blend_speed_mph > s->scene.visual_style_overhead_threshold) {
      target_blend = 1.0f;  // switch to 2D
    } else if (target_blend > 0.5f && blend_speed_mph < (s->scene.visual_style_overhead_threshold - 5)) {
      target_blend = 0.0f;  // switch back to 3D
    }

    // Time-based interpolation
    double now = millis_since_boot();
    double dt = (now - last_t) / 1000.0;
    last_t = now;

    const float transition_time = 1.50f; // seconds for full morph
    float step = dt / transition_time;

    if (blend < target_blend) {
      blend = std::min(blend + step, target_blend);
    } else if (blend > target_blend) {
      blend = std::max(blend - step, target_blend);
    }

    if (!normal_valid) return false;
    *out = QPointF(
      (1 - blend) * normal_view.x() + blend * topdown_view.x(),
      (1 - blend) * normal_view.y() + blend * topdown_view.y()
    );
  } else {
    if (!normal_valid) return false;
    *out = normal_view;
  }

  return clip_region.contains(*out);
}

void ModelRenderer::mapLineToPolygon(const cereal::XYZTData::Reader &line, float y_off, float z_off,
                                     QPolygonF *pvd, int max_idx, bool allow_invert) {
  const auto line_x = line.getX(), line_y = line.getY(), line_z = line.getZ();
  QPointF left, right;
  pvd->clear();
  for (int i = 0; i <= max_idx; i++) {
    // highly negative x positions  are drawn above the frame and cause flickering, clip to zy plane of camera
    if (line_x[i] < 0) continue;

    bool l = mapToScreen(line_x[i], line_y[i] - y_off, line_z[i] + z_off, &left);
    bool r = mapToScreen(line_x[i], line_y[i] + y_off, line_z[i] + z_off, &right);
    if (l && r) {
      // For wider lines the drawn polygon will "invert" when going over a hill and cause artifacts
      if (!allow_invert && pvd->size() && left.y() > pvd->back().y()) {
        continue;
      }
      pvd->push_back(left);
      pvd->push_front(right);
    }
  }
}
