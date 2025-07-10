#include <QPainterPath>
#include "selfdrive/ui/qt/onroad/model.h"

void ModelRenderer::draw(QPainter &painter, const QRect &surface_rect) {
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
  drawLeadStatus(painter, surface_rect.height(), surface_rect.width());

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
  const auto &model_position = model.getPosition();
  float max_distance = std::clamp(*(model_position.getX().end() - 1), MIN_DRAW_DISTANCE, MAX_DRAW_DISTANCE);

  // update lane lines
  const auto &lane_lines = model.getLaneLines();
  const auto &line_probs = model.getLaneLineProbs();
  int max_idx = get_path_length_idx(lane_lines[0], max_distance);
  for (int i = 0; i < std::size(lane_line_vertices); i++) {
    lane_line_probs[i] = line_probs[i];
    mapLineToPolygon(lane_lines[i], 0.025 * lane_line_probs[i], 0, &lane_line_vertices[i], max_idx);
  }

  // update road edges
  const auto &road_edges = model.getRoadEdges();
  const auto &edge_stds = model.getRoadEdgeStds();
  for (int i = 0; i < std::size(road_edge_vertices); i++) {
    road_edge_stds[i] = edge_stds[i];
    mapLineToPolygon(road_edges[i], 0.025, 0, &road_edge_vertices[i], max_idx);
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

void ModelRenderer::drawPath(QPainter &painter, const cereal::ModelDataV2::Reader &model, int height, int width) {
  QLinearGradient bg(0, height, 0, 0);
  auto *s = uiState();
  auto &sm = *(s->sm);

  float v_ego = sm["carState"].getCarState().getVEgo();
  bool rainbow = Params().getBool("RainbowMode");

  // Get the current time in seconds for dynamic effect (speed of rainbow movement)
  float time_offset = std::chrono::duration_cast<std::chrono::milliseconds>(
      std::chrono::steady_clock::now().time_since_epoch()).count() / 1000.0f;

  if (rainbow) {  // Rainbow Mode
      const int max_len = track_vertices.length();
      bg.setSpread(QGradient::PadSpread);  // Pad for a smooth gradient fade

      for (int i = 0; i < max_len; i += 2) {  // Skip every other point for performance
          if (track_vertices[i].y() < 0 || track_vertices[i].y() > height) continue;

          float lin_grad_point = (height - track_vertices[i].y()) / height;

          // Use easing for smoother color transitions
          float eased_point = pow(lin_grad_point, 1.5f);  // Ease-in effect

          // Dynamic hue with subtle, smooth animation
          float path_hue = fmod(eased_point * 360.0 + (v_ego * 20.0) + (time_offset * 100.0), 360.0);

          // Smooth alpha transition with longer fade
          float alpha = util::map_val(eased_point, 0.2f, 0.75f, 0.8f, 0.0f);

          // Use soft lightness for a premium feel
          bg.setColorAt(eased_point, QColor::fromHslF(path_hue / 360.0, 1.0f, 0.55f, alpha));
      }
  } else if (experimental_mode) {
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
  LongFuel(painter,height, width);
  LateralFuel(painter, height, width);
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

void ModelRenderer::drawGaugeBackground(QPainter &painter, qreal centerX, qreal centerY) {
    const qreal backgroundSize = GAUGE_SIZE * BACKGROUND_SIZE_MULTIPLIER;

    // Draw circular background
    painter.setPen(Qt::NoPen);
    painter.setBrush(BACKGROUND_COLOR);
    painter.drawEllipse(QPointF(centerX, centerY), backgroundSize / 2, backgroundSize / 2);

    // Draw border
    QPen borderPen(BORDER_COLOR);
    borderPen.setWidth(BORDER_PEN_WIDTH);
    painter.setPen(borderPen);
    painter.drawEllipse(QPointF(centerX, centerY), backgroundSize / 2 + 1, backgroundSize / 2 + 1);

    // Draw background semicircle
    QPen semicirclePen(GAUGE_BACKGROUND_COLOR);
    semicirclePen.setWidth(GAUGE_PEN_WIDTH);
    semicirclePen.setCapStyle(Qt::RoundCap);
    painter.setPen(semicirclePen);
    painter.drawArc(QRectF(centerX - GAUGE_SIZE / 2, centerY - GAUGE_SIZE / 2,
                          GAUGE_SIZE, GAUGE_SIZE), 0, SEMICIRCLE_SPAN);
}

QColor ModelRenderer::getIndicatorColor(float absoluteValue, float lowThreshold, float highThreshold) {
    if (absoluteValue < lowThreshold) {
        return LOW_INDICATOR_COLOR;
    } else if (absoluteValue < highThreshold) {
        return MODERATE_INDICATOR_COLOR;
    } else {
        return HIGH_INDICATOR_COLOR;
    }
}

int ModelRenderer::calculateSpanAngle(float absoluteValue, float maxValue) {
    const int spanAngle = static_cast<int>(QUARTER_CIRCLE_SPAN * (absoluteValue / maxValue));
    return std::clamp(spanAngle, 0, QUARTER_CIRCLE_SPAN);
}

void ModelRenderer::drawGaugeArc(QPainter &painter, qreal centerX, qreal centerY,
                                float value, bool isPositive, const QString &label) {
    const float absoluteValue = std::abs(value);

    if (absoluteValue <= MIN_THRESHOLD) {
        return; // Skip drawing if value is too small
    }

    // Set up the arc rectangle
    const QRectF arcRect(centerX - GAUGE_SIZE / 2, centerY - GAUGE_SIZE / 2,
                        GAUGE_SIZE, GAUGE_SIZE);

    // Configure pen for the indicator arc
    QPen indicatorPen;
    indicatorPen.setWidth(GAUGE_PEN_WIDTH);
    indicatorPen.setCapStyle(Qt::RoundCap);
    painter.setPen(indicatorPen);

    // Draw the arc based on direction
    const int spanAngle = calculateSpanAngle(absoluteValue, 1.0f); // Adjust max value as needed
    if (isPositive) {
        painter.drawArc(arcRect, STARTING_ANGLE, spanAngle);
    } else {
        painter.drawArc(arcRect, STARTING_ANGLE, -spanAngle);
    }

    // Draw center label
    painter.setPen(Qt::white);
    QFont font = painter.font();
    font.setPixelSize(20);
    font.setBold(true);
    painter.setFont(font);
    painter.drawText(QRectF(centerX - 50, centerY + 10, 100, 20), Qt::AlignCenter, label);
}

void ModelRenderer::LongFuel(QPainter &painter, int height, int width) {
    const qreal rectWidth = static_cast<qreal>(width);
    const qreal rectHeight = static_cast<qreal>(height);

    UIState *s = uiState();
    if (!s || !s->sm) {
        return; // Safety check
    }

    // Get current acceleration
    const float currentAcceleration = (*s->sm)["carControl"].getCarControl().getActuators().getAccel();
    const float absoluteAcceleration = std::abs(currentAcceleration);

    // Calculate gauge position
    const qreal centerX = rectWidth / 17;
    const qreal centerY = rectHeight / 2 + 120;

    // Draw gauge background
    drawGaugeBackground(painter, centerX, centerY);

    // Skip drawing arc if acceleration is too small
    if (absoluteAcceleration <= MIN_THRESHOLD) {
        drawGaugeArc(painter, centerX, centerY, 0.0f, true, tr("LONG"));
        return;
    }

    // Determine indicator color based on acceleration magnitude
    const QColor indicatorColor = getIndicatorColor(absoluteAcceleration, 0.3f, 0.6f);

    // Calculate span angle (scale for better visibility)
    const int spanAngle = static_cast<int>(QUARTER_CIRCLE_SPAN * absoluteAcceleration);
    const int clampedSpanAngle = std::clamp(spanAngle, 0, QUARTER_CIRCLE_SPAN);

    // Draw the acceleration arc
    QPen indicatorPen(indicatorColor);
    indicatorPen.setWidth(GAUGE_PEN_WIDTH);
    indicatorPen.setCapStyle(Qt::RoundCap);
    painter.setPen(indicatorPen);

    const QRectF arcRect(centerX - GAUGE_SIZE / 2, centerY - GAUGE_SIZE / 2,
                        GAUGE_SIZE, GAUGE_SIZE);

    // Draw arc based on acceleration direction
    if (currentAcceleration > 0) {
        painter.drawArc(arcRect, STARTING_ANGLE, -clampedSpanAngle); // Left side for positive
    } else {
        painter.drawArc(arcRect, STARTING_ANGLE, clampedSpanAngle);  // Right side for negative
    }

    // Draw center label
    painter.setPen(Qt::white);
    QFont font = painter.font();
    font.setPixelSize(20);
    font.setBold(true);
    painter.setFont(font);
    painter.drawText(QRectF(centerX - 50, centerY + 10, 100, 20), Qt::AlignCenter, tr("LONG"));
}

void ModelRenderer::LateralFuel(QPainter &painter, int height, int width) {
    const qreal rectWidth = static_cast<qreal>(width);
    const qreal rectHeight = static_cast<qreal>(height);

    UIState *s = uiState();
    if (!s || !s->sm) {
        return; // Safety check
    }

    // Get current steering angle
    const float currentLateral = (*s->sm)["carState"].getCarState().getSteeringAngleDeg();
    const float absoluteLateral = std::abs(currentLateral);

    // Calculate gauge position
    const qreal centerX = rectWidth / 17;
    const qreal centerY = rectHeight / 2 - 120;

    // Draw gauge background
    drawGaugeBackground(painter, centerX, centerY);

    // Skip drawing arc if lateral force is too small
    if (absoluteLateral <= 0.1f) {
        drawGaugeArc(painter, centerX, centerY, 0.0f, true, tr("LAT"));
        return;
    }

    // Determine indicator color based on lateral force magnitude
    const QColor indicatorColor = getIndicatorColor(absoluteLateral, 5.0f, 15.0f);

    // Calculate span angle (normalized to max expected steering angle)
    const float maxSteeringAngle = 15.0f; // Adjust based on your vehicle's characteristics
    const int spanAngle = static_cast<int>(QUARTER_CIRCLE_SPAN * (absoluteLateral / maxSteeringAngle));
    const int clampedSpanAngle = std::clamp(spanAngle, 0, QUARTER_CIRCLE_SPAN);

    // Draw the lateral arc
    QPen indicatorPen(indicatorColor);
    indicatorPen.setWidth(GAUGE_PEN_WIDTH);
    indicatorPen.setCapStyle(Qt::RoundCap);
    painter.setPen(indicatorPen);

    const QRectF arcRect(centerX - GAUGE_SIZE / 2, centerY - GAUGE_SIZE / 2,
                        GAUGE_SIZE, GAUGE_SIZE);

    // Draw arc based on steering direction
    if (currentLateral < 0) {
        painter.drawArc(arcRect, STARTING_ANGLE, -clampedSpanAngle); // Left turn
    } else {
        painter.drawArc(arcRect, STARTING_ANGLE, clampedSpanAngle);  // Right turn
    }

    // Draw center label
    painter.setPen(Qt::white);
    QFont font = painter.font();
    font.setPixelSize(20);
    font.setBold(true);
    painter.setFont(font);
    painter.drawText(QRectF(centerX - 50, centerY + 10, 100, 20), Qt::AlignCenter, tr("LAT"));
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
    if (has_lead_one) {
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

    // Calculate chevron size (same logic as drawLead)
    float sz = std::clamp((25 * 30) / (d_rel / 3 + 30), 15.0f, 30.0f) * 2.35;

    QFont content_font = painter.font();
    content_font.setPixelSize(35);
    content_font.setBold(true);
    painter.setFont(content_font);

    QFontMetrics fm(content_font);
    bool is_metric = s->scene.is_metric;

    QStringList text_lines;

    // Use your chevron data logic TODOSP: params!
    const int chevron_types = 3;
    //const int chevron_all = chevron_types + 1;  // All metrics not in use
    QStringList chevron_text[chevron_types];
    int position;
    float val;

    // Distance display (always show for primary lead)
    position = 0;
    val = std::max(0.0f, d_rel);
    chevron_text[position].append(QString::number(val, 'f', 0) + " " + "m");

    // Absolute velocity display (ego + relative)
    position = 1;
    val = std::max(0.0f, (v_rel + v_ego) * (is_metric ? static_cast<float>(MS_TO_KPH) : static_cast<float>(MS_TO_MPH)));
    chevron_text[position].append(QString::number(val, 'f', 0) + " " + (is_metric ? "km/h" : "mph"));

    // Time-to-contact display
    position = 2;
    val = (d_rel > 0 && v_ego > 0) ? std::max(0.0f, d_rel / v_ego) : 0.0f;
    QString ttc_str = (val > 0 && val < 200) ? QString::number(val, 'f', 1) + "s" : "---";
    chevron_text[position].append(ttc_str);

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
            } else {
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
  float raw_x = std::clamp<float>(vd.x(), 0.f, surface_rect.width() - sz / 2);
  float y = std::min<float>(vd.y(), surface_rect.height() - sz * 0.6);

// Check if the change in position is large
  float position_delta = std::abs(raw_x - hysteretic_x);
  float threshold = 100.0f;  // Adjust this value to tune when smoothing kicks in

  if (position_delta > threshold) {
    // For large changes, immediately update position
    hysteretic_x = raw_x;
  } else {
    // For small changes, apply smoothing
    hysteretic_x = (hysteresis_factor * raw_x) + ((1.0f - hysteresis_factor) * hysteretic_x);
  }

  float x = hysteretic_x;  // Use smoothed x value instead of raw_x



  // Set up the pen for drawing
  QPen pen;
  pen.setCapStyle(Qt::RoundCap);  // Round ends of the line
  pen.setJoinStyle(Qt::RoundJoin);  // Round corners

  // Disable fill
  painter.setBrush(Qt::NoBrush);


  // Draw the outer glow effect
  pen.setColor(QColor(218, 202, 37, 255));  // Yellow glow color
  pen.setWidth(10);  // Thicker width for glow
  painter.setPen(pen);

  // Create path for the line
  QPainterPath path;
  path.moveTo(x + (sz * 1.35), y + sz);   // right point
  path.lineTo(x, y); // top point
  path.lineTo(x - (sz * 1.35), y + sz);  // left point

  painter.drawPath(path);  // Draw the glow

  // Draw the main line
  pen.setColor(QColor(201, 34, 49, fillAlpha));  // Red color with calculated opacity
  pen.setWidth(7);  // Slightly thinner than the glow
  painter.setPen(pen);
  painter.drawPath(path);  // Draw the main line

}

// Projects a point in car to space to the corresponding point in full frame image space.
bool ModelRenderer::mapToScreen(float in_x, float in_y, float in_z, QPointF *out) {
  Eigen::Vector3f input(in_x, in_y, in_z);
  auto pt = car_space_transform * input;
  *out = QPointF(pt.x() / pt.z(), pt.y() / pt.z());
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