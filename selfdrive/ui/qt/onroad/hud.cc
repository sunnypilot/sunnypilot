#include "selfdrive/ui/qt/onroad/hud.h"

#include <cmath>
#include <QPainterPath>

#include "selfdrive/ui/qt/util.h"

constexpr int SET_SPEED_NA = 255;

QColor HudRenderer::interpColor(float x, const std::vector<float> &x_vals, const std::vector<QColor> &colors) {
  assert(x_vals.size() == colors.size() && x_vals.size() >= 2);

  if (x < x_vals[0]) return colors[0];
  if (x > x_vals.back()) return colors.back();

  for (size_t i = 1; i < x_vals.size(); ++i) {
    if (x < x_vals[i]) {
      float t = (x - x_vals[i - 1]) / (x_vals[i] - x_vals[i - 1]);
      t = std::max(0.0f, std::min(1.0f, t));
      QColor c1 = colors[i - 1];
      QColor c2 = colors[i];
      return QColor::fromRgbF(
        c1.redF() + (c2.redF() - c1.redF()) * t,
        c1.greenF() + (c2.greenF() - c1.greenF()) * t,
        c1.blueF() + (c2.blueF() - c1.blueF()) * t,
        c1.alphaF() + (c2.alphaF() - c1.alphaF()) * t
      );
    }
  }
  return colors.back();
}

HudRenderer::HudRenderer() {
}

void HudRenderer::updateState(const UIState &s) {
  is_metric = s.scene.is_metric;
  status = s.status;

  const SubMaster &sm = *(s.sm);
  if (sm.rcv_frame("carState") < s.scene.started_frame) {
    is_cruise_set = false;
    set_speed = SET_SPEED_NA;
    speed = 0.0;
    engine_rpm = 0.0f;
    return;
  }

  const auto &controls_state = sm["controlsState"].getControlsState();
  const auto &car_state = sm["carState"].getCarState();
  const auto lp_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();
  const auto slc = lp_sp.getSlc();
  const auto live_map_data = sm["liveMapDataSP"].getLiveMapDataSP();

  // SLC state variables
  slc_speed_limit = slc.getSpeedLimit() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_speed_offset = slc.getSpeedLimitOffset() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_state = slc.getState();
  show_slc = slc_speed_limit > 0.0;

  // Distance to speed limit change
  dist_to_speed_limit = slc.getDistToSpeedLimit();

  // Live map data for upcoming speed limits
  speed_limit_ahead_valid = live_map_data.getSpeedLimitAheadValid();
  if (speed_limit_ahead_valid) {
    speed_limit_ahead = live_map_data.getSpeedLimitAhead() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
    speed_limit_ahead_distance = live_map_data.getSpeedLimitAheadDistance();
  }

  // Road name
  road_name = QString::fromStdString(live_map_data.getRoadName());

  // Vision Turn Speed Control
  const auto vtsc = lp_sp.getVisionTurnSpeedControl();
  vtsc_state = static_cast<int>(vtsc.getState());
  vtsc_velocity = vtsc.getVelocity() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  vtsc_current_lateral_accel = vtsc.getCurrentLateralAccel();
  vtsc_max_predicted_lateral_accel = vtsc.getMaxPredictedLateralAccel();
  show_vtsc = vtsc_state != 0; // Show when not disabled

  // Handle older routes where vCruiseCluster is not set
  set_speed = car_state.getVCruiseCluster() == 0.0 ? controls_state.getVCruiseDEPRECATED() : car_state.getVCruiseCluster();
  is_cruise_set = set_speed > 0 && set_speed != SET_SPEED_NA;
  is_cruise_available = set_speed != -1;

  if (is_cruise_set && !is_metric) {
    set_speed *= KM_TO_MILE;
  }

  // Handle older routes where vEgoCluster is not set
  v_ego_cluster_seen = v_ego_cluster_seen || car_state.getVEgoCluster() != 0.0;
  float v_ego = v_ego_cluster_seen ? car_state.getVEgoCluster() : car_state.getVEgo();
  speed = std::max<float>(0.0f, v_ego * (is_metric ? MS_TO_KPH : MS_TO_MPH));

  // Eco mode detection - moving but engine off (hybrid/EV mode)
  is_eco_mode = v_ego > 0 && car_state.getEngineRpm() == 0;

  // Enhanced over speed limit detection with multiple thresholds
  float current_limit = slc_speed_limit;
  if (current_limit > 0) {
    float effective_limit = current_limit + slc_speed_offset;
    speed_violation_level = 0; // No violation
    if (speed > effective_limit + 3.0) speed_violation_level = 1; // Warning
    if (speed > effective_limit + 5.0) speed_violation_level = 2; // Moderate
    if (speed > effective_limit + 8.0) speed_violation_level = 3; // Severe
    over_speed_limit = speed_violation_level > 1;
  } else {
    speed_violation_level = 0;
    over_speed_limit = false;
  }
}

void HudRenderer::draw(QPainter &p, const QRect &surface_rect) {
  p.save();
  p.setRenderHint(QPainter::Antialiasing, true);
  p.setRenderHint(QPainter::TextAntialiasing, true);

  // Draw header gradient
  QLinearGradient bg(0, UI_HEADER_HEIGHT - (UI_HEADER_HEIGHT / 2.5), 0, UI_HEADER_HEIGHT);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, surface_rect.width(), UI_HEADER_HEIGHT, bg);


  if (is_cruise_available) {
    drawSetSpeed(p, surface_rect);
  }

  // Always try to draw speed limit signs if we have any speed limit data
  if (show_slc && slc_speed_limit > 0) {
    drawSpeedLimitSigns(p, surface_rect);
  }

  // Draw upcoming speed limit if available
  if (speed_limit_ahead_valid && speed_limit_ahead != slc_speed_limit) {
    drawUpcomingSpeedLimit(p, surface_rect);
  }

  // Draw SLC state indicator
  //if (show_slc) {
  //  drawSLCStateIndicator(p, surface_rect);
  //}

  // Draw road name if available
  if (!road_name.isEmpty()) {
    drawRoadName(p, surface_rect);
  }

  // Draw Vision Turn Speed Control if active
  if (show_vtsc) {
    drawVisionTurnControl(p, surface_rect);
  }

  drawCurrentSpeed(p, surface_rect);

  p.restore();
}

void HudRenderer::drawSetSpeed(QPainter &p, const QRect &surface_rect) {
  // Draw outer box + border to contain set speed
  const QSize default_size = {172, 204};
  QSize set_speed_size = is_metric ? QSize(200, 204) : default_size;
  QRect set_speed_rect(QPoint(60 + (default_size.width() - set_speed_size.width()) / 2, 45), set_speed_size);

  // Draw set speed box
  p.setPen(QPen(QColor(255, 255, 255, 75), 6));
  p.setBrush(QColor(0, 0, 0, 166));
  p.drawRoundedRect(set_speed_rect, 32, 32);

  // Colors based on status
  QColor max_color = QColor(0xa6, 0xa6, 0xa6, 0xff);
  QColor set_speed_color = QColor(0x72, 0x72, 0x72, 0xff);
  if (is_cruise_set) {
    set_speed_color = QColor(255, 255, 255);
    if (status == STATUS_DISENGAGED) {
      max_color = QColor(255, 255, 255);
    } else if (status == STATUS_OVERRIDE) {
      max_color = QColor(0x91, 0x9b, 0x95, 0xff);
    } else {
      max_color = QColor(0x80, 0xd8, 0xa6, 0xff);

      // Speed limit color interpolation
      if (slc_speed_limit > 0) {
      float comparison_speed = slc_speed_limit + slc_speed_offset;
        max_color = interpColor(set_speed,
          {comparison_speed, comparison_speed + 5, comparison_speed + 10},
          {max_color, QColor(0xff, 0xe4, 0xbf), QColor(0xff, 0xbf, 0xbf)});
        set_speed_color = interpColor(set_speed,
          {comparison_speed, comparison_speed + 5, comparison_speed + 10},
          {set_speed_color, QColor(0xff, 0x95, 0x00), QColor(0xff, 0x00, 0x00)});
      }
    }
  }

  // Draw "MAX" text
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(max_color);
  p.drawText(set_speed_rect.adjusted(0, 27, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("MAX"));

  // Draw set speed
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(set_speed)) : "–";
  p.setFont(InterFont(90, QFont::Bold));
  p.setPen(set_speed_color);
  p.drawText(set_speed_rect.adjusted(0, 77, 0, 0), Qt::AlignTop | Qt::AlignHCenter, setSpeedStr);
}

void HudRenderer::drawSpeedLimitSigns(QPainter &p, const QRect &surface_rect) {
  // Determine which speed limit to display
  float display_speed = slc_speed_limit;

  if (display_speed <= 0) return;

  QString speedLimitStr = QString::number(std::nearbyint(display_speed));

  // Create sub-text for offset
  QString slcSubText = "";
  if (show_slc && slc_speed_offset != 0) {
    slcSubText = (slc_speed_offset > 0 ? "+" : "") + QString::number(std::nearbyint(slc_speed_offset));
  }

  // Position speed limit sign to the right of MAX speed box
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;
  QRect sign_rect(sign_x, sign_y, sign_width, sign_height);

  // Check if SLC is inactive or controller is not active
  bool is_slc_inactive = (slc_state == cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE ||
                         slc_state == cereal::LongitudinalPlanSP::SpeedLimitControlState::TEMP_INACTIVE);
  bool is_controller_inactive = (status == STATUS_DISENGAGED);
  bool should_show_inactive = is_slc_inactive || is_controller_inactive;

  // Reduce opacity when inactive (50% opacity instead of full)
  int base_alpha = should_show_inactive ? 128 : 255;

  // Add pulsing animation for violations (but not when inactive)
  bool should_pulse = speed_violation_level >= 2 && !should_show_inactive;
  int pulse_alpha = should_pulse ? (int)(127 + 128 * std::sin(QTime::currentTime().msec() * 0.01)) : base_alpha;

  if (!is_metric) {
    // US/Canada (MUTCD style) sign
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawRoundedRect(sign_rect, 32, 32);

    // Draw inner rounded rectangle with colored border
    QRect inner_rect = sign_rect.adjusted(10, 10, -10, -10);
    QColor border_color = QColor(0, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) border_color = QColor(255, 165, 0, pulse_alpha); // Orange or yellow?
      else if (speed_violation_level >= 2) border_color = QColor(255, 0, 0, pulse_alpha); // Red
    }

    p.setPen(QPen(border_color, 4));
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawRoundedRect(inner_rect, 22, 22);

    // "SPEED LIMIT" text
    p.setFont(InterFont(40, QFont::DemiBold));
    p.setPen(QColor(0, 0, 0, pulse_alpha));
    p.drawText(inner_rect.adjusted(0, 10, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("SPEED"));
    p.drawText(inner_rect.adjusted(0, 50, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("LIMIT"));

    // Speed value with color coding
    p.setFont(InterFont(90, QFont::Bold));
    QColor speed_color = QColor(0, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) speed_color = QColor(255, 165, 0, pulse_alpha);
      else if (speed_violation_level >= 2) speed_color = QColor(255, 0, 0, pulse_alpha);
    }

    p.setPen(speed_color);
    p.drawText(inner_rect.adjusted(0, 80, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedLimitStr);

    // Draw diagonal line when inactive
    if (should_show_inactive) {
      p.setPen(QPen(QColor(200, 50, 50, 180), 8, Qt::SolidLine, Qt::RoundCap));
      p.drawLine(inner_rect.topLeft() + QPoint(15, 15),
                 inner_rect.bottomRight() + QPoint(-15, -15));
    }

    // Speed limit offset value
    if (!slcSubText.isEmpty()) {
      int offset_box_size = 70;
      QRect offset_box_rect(
        sign_rect.right() - offset_box_size/2 + 10,
        sign_rect.top() + offset_box_size/2 - 65,
        offset_box_size,
        offset_box_size
      );

      p.setPen(QPen(QColor(255, 255, 255, 75), 6));
      p.setBrush(QColor(0, 0, 0, pulse_alpha));
      p.drawRoundedRect(offset_box_rect, 12, 12);

      p.setFont(InterFont(40, QFont::Bold));
      p.setPen(QColor(255, 255, 255, pulse_alpha));
      p.drawText(offset_box_rect, Qt::AlignCenter, slcSubText);
    }
  } else {
    // EU (Vienna style) sign
    QRect vienna_rect = sign_rect;
    int circle_size = std::min(vienna_rect.width(), vienna_rect.height());
    QRect circle_rect(vienna_rect.x(), vienna_rect.y(), circle_size, circle_size);

    if (vienna_rect.width() > vienna_rect.height()) {
        circle_rect.moveLeft(vienna_rect.x() + (vienna_rect.width() - circle_size) / 2);
    } else if (vienna_rect.height() > vienna_rect.width()) {
        circle_rect.moveTop(vienna_rect.y() + (vienna_rect.height() - circle_size) / 2);
    }

    // Draw white circle background
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawEllipse(circle_rect);

    QRect red_ring = circle_rect.adjusted(4, 4, -4, -4);
    QColor ring_color = QColor(255, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) ring_color = QColor(255, 165, 0, pulse_alpha);
      else if (speed_violation_level >= 2) ring_color = QColor(255, 0, 0, pulse_alpha);
    }

    p.setBrush(ring_color);
    p.drawEllipse(red_ring);

    // Draw white center circle for text
    QRect center_circle = red_ring.adjusted(30, 30, -30, -30);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawEllipse(center_circle);

    // Speed value
    int font_size = (speedLimitStr.size() >= 3) ? 70 : 85;
    p.setFont(InterFont(font_size, QFont::Bold));
    QColor speed_color = QColor(0, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) speed_color = QColor(255, 165, 0, pulse_alpha);
      else if (speed_violation_level >= 2) speed_color = QColor(255, 0, 0, pulse_alpha);
    }

    p.setPen(speed_color);

    QRect speed_text_rect = center_circle;
    p.drawText(speed_text_rect, Qt::AlignCenter, speedLimitStr);

    // Draw diagonal line when inactive
    if (should_show_inactive) {
      p.setPen(QPen(QColor(200, 50, 50, 180), 8, Qt::SolidLine, Qt::RoundCap));
      // Draw line across the center circle
      QPoint center = center_circle.center();
      int radius = center_circle.width() / 2 - 8;
      p.drawLine(center + QPoint(-radius, -radius), center + QPoint(radius, radius));
    }

    // Speed limit offset value
    if (!slcSubText.isEmpty()) {
      int offset_circle_size = 80;
      QRect offset_circle_rect(
        circle_rect.right() - offset_circle_size/2 + 10,
        circle_rect.top() + offset_circle_size/2 - 35,
        offset_circle_size,
        offset_circle_size
      );

      p.setPen(QPen(QColor(255, 255, 255, 75), 6));
      p.setBrush(QColor(0, 0, 0, pulse_alpha));
      p.drawRoundedRect(offset_circle_rect, offset_circle_size/2, offset_circle_size/2);

      p.setFont(InterFont(40, QFont::Bold));
      p.setPen(QColor(255, 255, 255, pulse_alpha));
      p.drawText(offset_circle_rect, Qt::AlignCenter, slcSubText);
    }
  }
}

void HudRenderer::drawUpcomingSpeedLimit(QPainter &p, const QRect &surface_rect) {
  if (!speed_limit_ahead_valid || speed_limit_ahead <= 0) return;

  QString speedStr = QString::number(std::nearbyint(speed_limit_ahead));
  QString distanceStr;
  //TODO: this shit is garbage someone help
  if (is_metric) {
    if (speed_limit_ahead_distance < 1000) {
      distanceStr = QString::number(std::nearbyint(speed_limit_ahead_distance)) + "m";
    } else {
      distanceStr = QString::number(speed_limit_ahead_distance / 1000.0, 'f', 1) + "km";
    }
  } else {
    float distance_ft = speed_limit_ahead_distance * 3.28084;
    if (distance_ft < 1000) {
      distanceStr = QString::number(std::nearbyint(distance_ft)) + "ft";
    } else {
      distanceStr = QString::number(distance_ft / 5280.0, 'f', 1) + "mi";
    }
  }

  // Position upcoming speed limit directly under the current speed limit sign
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;

  const int ahead_width = 170;
  const int ahead_height = 160;
  // Center the upcoming sign under the speed limit sign with small gap
  const int ahead_x = sign_x + (sign_width - ahead_width) / 2;
  const int ahead_y = sign_y + sign_height + 10; // 10px gap below speed limit sign

  QRect ahead_rect(ahead_x, ahead_y, ahead_width, ahead_height);
  p.setPen(QPen(QColor(255, 255, 255, 100), 3));
  p.setBrush(QColor(0, 0, 0, 180));
  p.drawRoundedRect(ahead_rect, 16, 16);

  // "AHEAD" label
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(QColor(200, 200, 200, 255));
  p.drawText(ahead_rect.adjusted(0, 12, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("AHEAD"));

  // Speed value
  p.setFont(InterFont(70, QFont::Bold));
  p.setPen(QColor(255, 255, 255, 255));
  p.drawText(ahead_rect.adjusted(0, 42, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedStr);

  // Distance
  p.setFont(InterFont(40, QFont::Normal));
  p.setPen(QColor(180, 180, 180, 255));
  p.drawText(ahead_rect.adjusted(0, 110, 0, 0), Qt::AlignTop | Qt::AlignHCenter, distanceStr);
}

void HudRenderer::drawSLCStateIndicator(QPainter &p, const QRect &surface_rect) {
  QString stateText;
  QColor stateColor;

  //TODO: fix me i am ugly
  switch (slc_state) {
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE:
      return; // Don't show anything
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::TEMP_INACTIVE:
      stateText = tr("IGNORED");
      stateColor = QColor(255, 165, 0, 255);
      break;
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::PRE_ACTIVE:
      stateText = tr("PREPARING");
      stateColor = QColor(255, 255, 0, 255);
      break;
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::ADAPTING:
      stateText = tr("ADAPTING");
      stateColor = QColor(0, 150, 255, 255);
      break;
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::ACTIVE:
      stateText = tr("ACTIVE");
      stateColor = QColor(0, 255, 0, 255);
      break;
    default:
      return;
  }

  // Position state indicator below the upcoming speed limit if it exists,
  // otherwise below the current speed limit sign
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;

  int state_y = sign_y + sign_height + 10; // Default position right under speed limit

  // If upcoming speed limit is shown, position state indicator below it
  if (speed_limit_ahead_valid && speed_limit_ahead != slc_speed_limit) {
    const int ahead_height = 120;
    state_y = sign_y + sign_height + 10 + ahead_height + 10; // Below upcoming speed limit
  }

  QRect state_rect(sign_x, state_y, sign_width, 40);

  p.setPen(QPen(stateColor, 2));
  p.setBrush(QColor(0, 0, 0, 150));
  p.drawRoundedRect(state_rect, 8, 8);

  p.setFont(InterFont(24, QFont::Bold));
  p.setPen(stateColor);
  p.drawText(state_rect, Qt::AlignCenter, stateText);
}

void HudRenderer::drawRoadName(QPainter &p, const QRect &surface_rect) {
  if (road_name.isEmpty()) return;

  // Set font first to measure text
  p.setFont(InterFont(40, QFont::Normal));
  QFontMetrics fm(p.font());

  // Calculate required width based on text + padding
  int text_width = fm.horizontalAdvance(road_name);
  int padding = 40;
  int rect_width = text_width + padding;

  // Set minimum and maximum widths
  int min_width = 200;
  int max_width = surface_rect.width() - 40;
  rect_width = std::max(min_width, std::min(rect_width, max_width));

  // Position road name at the top center
  QRect road_rect(surface_rect.width() / 2 - rect_width / 2, 5, rect_width, 60);

  p.setPen(QPen(QColor(255, 255, 255, 100), 1));
  //p.setBrush(QColor(0, 0, 0, 120));
  p.drawRoundedRect(road_rect, 6, 6);

  p.setPen(QColor(255, 255, 255, 200));

  // Truncate long road names if they still don't fit
  QString truncated = fm.elidedText(road_name, Qt::ElideRight, road_rect.width() - 20);
  p.drawText(road_rect, Qt::AlignCenter, truncated);
}

void HudRenderer::drawCurrentSpeed(QPainter &p, const QRect &surface_rect) {
  QString speedStr = QString::number(std::nearbyint(speed));

  p.setFont(InterFont(176, QFont::Bold));
  // Change color based on eco mode (RPM = 0)
  if (is_eco_mode) {
    drawEcoText(p, surface_rect.center().x(), 210, speedStr);
  } else {
    drawText(p, surface_rect.center().x(), 210, speedStr);
  }

  p.setFont(InterFont(66));

  // Also make units eco green when in eco mode
  if (is_eco_mode) {
    drawEcoText(p, surface_rect.center().x(), 290, is_metric ? tr("km/h") : tr("mph"), 200);
  } else {
    drawText(p, surface_rect.center().x(), 290, is_metric ? tr("km/h") : tr("mph"), 200);
  }
}

void HudRenderer::drawEcoText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});
  p.setPen(QColor(0x80, 0xd8, 0xa6, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}


void HudRenderer::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void HudRenderer::drawVisionTurnControl(QPainter &p, const QRect &surface_rect) {
  // Position below the current speed display
  const int vtsc_width = 280;
  const int vtsc_height = 120;
  const int vtsc_x = (surface_rect.width() - vtsc_width) / 2;
  const int vtsc_y = 350; // Below speed display

  QRect vtsc_rect(vtsc_x, vtsc_y, vtsc_width, vtsc_height);

  // Determine state colors and text
  QColor state_color;
  QString state_text;
  QColor bg_color = QColor(0, 0, 0, 180);

  switch (vtsc_state) {
    case 1: // entering
      state_color = QColor(255, 200, 0, 255); // Orange
      state_text = tr("TURN AHEAD");
      bg_color = QColor(40, 30, 0, 200); // Dark orange tint
      break;
    case 2: // turning
      state_color = QColor(255, 100, 100, 255); // Light red
      state_text = tr("TURNING");
      bg_color = QColor(40, 20, 20, 200); // Dark red tint
      break;
    case 3: // leaving
      state_color = QColor(100, 255, 100, 255); // Light green
      state_text = tr("TURN EXIT");
      bg_color = QColor(20, 40, 20, 200); // Dark green tint
      break;
    default:
      return; // Don't draw if disabled
  }

  // Draw background with subtle border
  p.setPen(QPen(state_color, 2));
  p.setBrush(bg_color);
  p.drawRoundedRect(vtsc_rect, 16, 16);

  // Draw state text
  p.setFont(InterFont(32, QFont::Bold));
  p.setPen(state_color);
  p.drawText(vtsc_rect.adjusted(0, 10, 0, 0), Qt::AlignTop | Qt::AlignHCenter, state_text);

  // Draw target velocity if significantly different from current speed
  if (vtsc_velocity > 0 && std::abs(vtsc_velocity - speed) > 2.0) {
    QString velocity_text = QString::number(std::nearbyint(vtsc_velocity)) + (is_metric ? " km/h" : " mph");
    p.setFont(InterFont(24, QFont::DemiBold));
    p.setPen(QColor(255, 255, 255, 200));
    p.drawText(vtsc_rect.adjusted(0, 50, 0, 0), Qt::AlignTop | Qt::AlignHCenter, velocity_text);
  }

  // Draw lateral acceleration indicator (simplified)
  if (vtsc_max_predicted_lateral_accel > 0.5) { // Only show for significant turns
    QRect accel_rect = vtsc_rect.adjusted(10, vtsc_rect.height() - 25, -10, -10);

    // Background bar
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(60, 60, 60, 150));
    p.drawRoundedRect(accel_rect, 4, 4);

    // Current acceleration indicator
    float accel_ratio = std::min(1.0f, std::abs(vtsc_current_lateral_accel) / 4.0f); // Scale to 4 m/s²
    int current_width = static_cast<int>(accel_rect.width() * accel_ratio);
    if (current_width > 0) {
      QRect current_rect = accel_rect;
      current_rect.setWidth(current_width);
      QColor accel_color = interpColor(accel_ratio, {0.0f, 0.7f, 1.0f},
                                      {QColor(100, 255, 100), QColor(255, 255, 100), QColor(255, 100, 100)});
      p.setBrush(accel_color);
      p.drawRoundedRect(current_rect, 4, 4);
    }
  }
}
