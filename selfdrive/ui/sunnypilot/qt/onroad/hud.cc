/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/onroad/hud.h"
#include "selfdrive/ui/qt/util.h"
#include <cmath>
#include <QTime>

QColor HudRendererSP::interpColor(float x, const std::vector<float> &x_vals, const std::vector<QColor> &colors) {
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

HudRendererSP::HudRendererSP() {}

void HudRendererSP::updateState(const UIState &s) {
  HudRenderer::updateState(s);

  const SubMaster &sm = *(s.sm);

  const auto lp_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();
  const auto slc = lp_sp.getSlc();
  const auto live_map_data = sm["liveMapDataSP"].getLiveMapDataSP();

  slc_speed_limit = slc.getSpeedLimit() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_speed_offset = slc.getSpeedLimitOffset() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_state = slc.getState();
  show_slc = slc_speed_limit > 0.0;

  dist_to_speed_limit = slc.getDistToSpeedLimit();

  speed_limit_ahead_valid = live_map_data.getSpeedLimitAheadValid();
  if (speed_limit_ahead_valid) {
    speed_limit_ahead = live_map_data.getSpeedLimitAhead() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
    speed_limit_ahead_distance = live_map_data.getSpeedLimitAheadDistance();
  }

  road_name = QString::fromStdString(live_map_data.getRoadName());

  // when going above speed limit and offset it will flash
  float current_limit = slc_speed_limit;
  if (current_limit > 0) {
    float effective_limit = current_limit + slc_speed_offset;
    speed_violation_level = 0;
    if (speed > effective_limit + 3.0) speed_violation_level = 1; // Warning
    if (speed > effective_limit + 5.0) speed_violation_level = 2; // Moderate
    if (speed > effective_limit + 8.0) speed_violation_level = 3; // Severe
    over_speed_limit = speed_violation_level > 1;
  } else {
    speed_violation_level = 0;
    over_speed_limit = false;
  }
}

void HudRendererSP::draw(QPainter &p, const QRect &surface_rect) {
  p.save();
  p.setRenderHint(QPainter::Antialiasing, true);
  p.setRenderHint(QPainter::TextAntialiasing, true);

  // Header gradient background
  QLinearGradient bg(0, UI_HEADER_HEIGHT - (UI_HEADER_HEIGHT / 2.5), 0, UI_HEADER_HEIGHT);
  bg.setColorAt(0, QColor::fromRgbF(0, 0, 0, 0.45));
  bg.setColorAt(1, QColor::fromRgbF(0, 0, 0, 0));
  p.fillRect(0, 0, surface_rect.width(), UI_HEADER_HEIGHT, bg);

  if (is_cruise_available) {
    drawSetSpeedSP(p, surface_rect);
  }

  if (show_slc && slc_speed_limit > 0) {
    drawSpeedLimitSigns(p, surface_rect);
  }

  if (speed_limit_ahead_valid && speed_limit_ahead != slc_speed_limit) {
    drawUpcomingSpeedLimit(p, surface_rect);
  }

  if (!road_name.isEmpty()) {
    drawRoadName(p, surface_rect);
  }

  drawCurrentSpeed(p, surface_rect);

  p.restore();
}

void HudRendererSP::drawSetSpeedSP(QPainter &p, const QRect &surface_rect) {
  const QSize default_size = {172, 204};
  QSize set_speed_size = is_metric ? QSize(200, 204) : default_size;
  QRect set_speed_rect(QPoint(40 + (default_size.width() - set_speed_size.width()) / 2, 45), set_speed_size);

  // Main container box
  p.setPen(QPen(QColor(255, 255, 255, 75), 6));
  p.setBrush(QColor(0, 0, 0, 166));
  p.drawRoundedRect(set_speed_rect, 32, 32);

  // Default colors
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

      // Adjust colors based on speed limit compliance
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

  // "MAX" label
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(max_color);
  p.drawText(set_speed_rect.adjusted(0, 27, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("MAX"));

  // Set speed value
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(set_speed)) : "–";
  p.setFont(InterFont(90, QFont::Bold));
  p.setPen(set_speed_color);
  p.drawText(set_speed_rect.adjusted(0, 77, 0, 0), Qt::AlignTop | Qt::AlignHCenter, setSpeedStr);
}

void HudRendererSP::drawSpeedLimitSigns(QPainter &p, const QRect &surface_rect) {
  float display_speed = slc_speed_limit;
  if (display_speed <= 0) return;

  QString speedLimitStr = QString::number(std::nearbyint(display_speed));

  // Offset display text
  QString slcSubText = "";
  if (show_slc && slc_speed_offset != 0) {
    slcSubText = (slc_speed_offset > 0 ? "+" : "") + QString::number(std::nearbyint(slc_speed_offset));
  }

  // Position next to MAX speed box
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;
  QRect sign_rect(sign_x, sign_y, sign_width, sign_height);

  // Check for inactive states
  bool is_slc_inactive = (slc_state == cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE);
  bool is_controller_inactive = (status == STATUS_DISENGAGED);
  bool should_show_inactive = is_slc_inactive || is_controller_inactive;

  int base_alpha = should_show_inactive ? 128 : 255;

  // Pulse animation for speed violations (when active)
  bool should_pulse = speed_violation_level >= 2 && !should_show_inactive;
  int pulse_alpha = should_pulse ? (int)(127 + 128 * std::sin(QTime::currentTime().msec() * 0.01)) : base_alpha;

  if (!is_metric) {
    // US/Canada MUTCD style sign
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawRoundedRect(sign_rect, 32, 32);

    // Inner border with violation color coding
    QRect inner_rect = sign_rect.adjusted(10, 10, -10, -10);
    QColor border_color = QColor(0, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) border_color = QColor(255, 165, 0, pulse_alpha); // Orange
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

    // Strikethrough for inactive state
    if (should_show_inactive) {
      p.setPen(QPen(QColor(200, 50, 50, 180), 8, Qt::SolidLine, Qt::RoundCap));
      p.drawLine(inner_rect.topLeft() + QPoint(15, 15),
                 inner_rect.bottomRight() + QPoint(-15, -15));
    }

    // Offset value in small box
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
    // EU Vienna Convention style circular sign
    QRect vienna_rect = sign_rect;
    int circle_size = std::min(vienna_rect.width(), vienna_rect.height());
    QRect circle_rect(vienna_rect.x(), vienna_rect.y(), circle_size, circle_size);

    if (vienna_rect.width() > vienna_rect.height()) {
        circle_rect.moveLeft(vienna_rect.x() + (vienna_rect.width() - circle_size) / 2);
    } else if (vienna_rect.height() > vienna_rect.width()) {
        circle_rect.moveTop(vienna_rect.y() + (vienna_rect.height() - circle_size) / 2);
    }

    // White background circle
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawEllipse(circle_rect);

    // Red border ring with color coding
    QRect red_ring = circle_rect.adjusted(4, 4, -4, -4);
    QColor ring_color = QColor(255, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) ring_color = QColor(255, 165, 0, pulse_alpha);
      else if (speed_violation_level >= 2) ring_color = QColor(255, 0, 0, pulse_alpha);
    }

    p.setBrush(ring_color);
    p.drawEllipse(red_ring);

    // Center white circle for text
    QRect center_circle = red_ring.adjusted(30, 30, -30, -30);
    p.setBrush(QColor(255, 255, 255, pulse_alpha));
    p.drawEllipse(center_circle);

    // Speed value, smaller font for 3+ digits
    int font_size = (speedLimitStr.size() >= 3) ? 70 : 85;
    p.setFont(InterFont(font_size, QFont::Bold));
    QColor speed_color = QColor(0, 0, 0, pulse_alpha);
    if (!should_show_inactive) {
      if (speed_violation_level == 1) speed_color = QColor(255, 165, 0, pulse_alpha);
      else if (speed_violation_level >= 2) speed_color = QColor(255, 0, 0, pulse_alpha);
    }

    p.setPen(speed_color);
    p.drawText(center_circle, Qt::AlignCenter, speedLimitStr);

    // Strikethrough for inactive state
    if (should_show_inactive) {
      p.setPen(QPen(QColor(200, 50, 50, 180), 8, Qt::SolidLine, Qt::RoundCap));
      QPoint center = center_circle.center();
      int radius = center_circle.width() / 2 - 8;
      p.drawLine(center + QPoint(-radius, -radius), center + QPoint(radius, radius));
    }

    // Offset value in small circular box
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

void HudRendererSP::drawUpcomingSpeedLimit(QPainter &p, const QRect &surface_rect) {
  if (!speed_limit_ahead_valid || speed_limit_ahead <= 0) return;

  QString speedStr = QString::number(std::nearbyint(speed_limit_ahead));
  QString distanceStr;

  // Format distance based on units
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

  // Position below current speed limit sign
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;

  const int ahead_width = 170;
  const int ahead_height = 160;
  const int ahead_x = sign_x + (sign_width - ahead_width) / 2;
  const int ahead_y = sign_y + sign_height + 10;

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

// Disabled for now i do not like it.
void HudRendererSP::drawSLCStateIndicator(QPainter &p, const QRect &surface_rect) {
  QString stateText;
  QColor stateColor;

  switch (slc_state) {
    case cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE:
      return;
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

  // Position below upcoming speed limit or current speed limit
  const int sign_width = is_metric ? 200 : 172;
  const int sign_x = is_metric ? 280 : 272;
  const int sign_y = 45;
  const int sign_height = 204;

  int state_y = sign_y + sign_height + 10;

  if (speed_limit_ahead_valid && speed_limit_ahead != slc_speed_limit) {
    const int ahead_height = 160;
    state_y = sign_y + sign_height + 10 + ahead_height + 10;
  }

  QRect state_rect(sign_x, state_y, sign_width, 40);

  p.setPen(QPen(stateColor, 2));
  p.setBrush(QColor(0, 0, 0, 150));
  p.drawRoundedRect(state_rect, 8, 8);

  p.setFont(InterFont(24, QFont::Bold));
  p.setPen(stateColor);
  p.drawText(state_rect, Qt::AlignCenter, stateText);
}

void HudRendererSP::drawRoadName(QPainter &p, const QRect &surface_rect) {
  if (road_name.isEmpty()) return;

  // Measure text to size container
  p.setFont(InterFont(40, QFont::Normal));
  QFontMetrics fm(p.font());

  int text_width = fm.horizontalAdvance(road_name);
  int padding = 40;
  int rect_width = text_width + padding;

  // Constrain to reasonable bounds
  int min_width = 200;
  int max_width = surface_rect.width() - 40;
  rect_width = std::max(min_width, std::min(rect_width, max_width));

  // Center at top of screen
  QRect road_rect(surface_rect.width() / 2 - rect_width / 2, 5, rect_width, 60);

  p.setPen(QPen(QColor(255, 255, 255, 100), 1));
  p.setBrush(QColor(0, 0, 0, 120));
  p.drawRoundedRect(road_rect, 6, 6);

  p.setPen(QColor(255, 255, 255, 200));

  // Truncate if still too long
  QString truncated = fm.elidedText(road_name, Qt::ElideRight, road_rect.width() - 20);
  p.drawText(road_rect, Qt::AlignCenter, truncated);
}