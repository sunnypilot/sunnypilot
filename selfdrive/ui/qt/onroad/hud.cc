#include "selfdrive/ui/qt/onroad/hud.h"

#include <cmath>
#include <QPainterPath>

#include "selfdrive/ui/qt/util.h"

constexpr int SET_SPEED_NA = 255;

static QColor interpColor(float x, const std::vector<float> &x_vals, const std::vector<QColor> &colors) {
  assert(x_vals.size() == colors.size() && x_vals.size() >= 2);
  for (size_t i = 1; i < x_vals.size(); ++i) {
    if (x < x_vals[i]) {
      float t = (x - x_vals[i - 1]) / (x_vals[i] - x_vals[i - 1]);
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
  // No need to load map icon anymore
}

void HudRenderer::updateState(const UIState &s) {
  is_metric = s.scene.is_metric;
  status = s.status;

  const SubMaster &sm = *(s.sm);
  if (sm.rcv_frame("carState") < s.scene.started_frame) {
    is_cruise_set = false;
    set_speed = SET_SPEED_NA;
    speed = 0.0;
    return;
  }

  const auto &controls_state = sm["controlsState"].getControlsState();
  const auto &car_state = sm["carState"].getCarState();
  const auto lp_sp = sm["longitudinalPlanSP"].getLongitudinalPlanSP();
  const auto slc = lp_sp.getSlc();

  // Speed limit from SLC
  nav_speed_limit = slc.getSpeedLimit();
  has_us_speed_limit = !is_metric;
  has_eu_speed_limit = is_metric;

  // SLC state variables
  slc_state = static_cast<int>(slc.getState());
  slc_speed_limit = slc.getSpeedLimit() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_speed_offset = slc.getSpeedLimitOffset() * (is_metric ? MS_TO_KPH : MS_TO_MPH);
  slc_distance = int(slc.getDistToSpeedLimit() * (is_metric ? MS_TO_KPH : MS_TO_MPH) / 10.0) * 10;
  is_map_speed_limit = true; // Assume map-based for now
  show_slc = slc_speed_limit > 0.0;

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

  // Over speed limit detection
  over_speed_limit = (show_slc && slc_speed_limit > 0) ?
                     (speed > slc_speed_limit + slc_speed_offset + 5.0) :
                     (nav_speed_limit > 0 && speed > nav_speed_limit + 5.0);
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
  if ((show_slc && slc_speed_limit > 0) || nav_speed_limit > 0) {
    drawSpeedLimitSigns(p, surface_rect);
  }

  drawCurrentSpeed(p, surface_rect);

  p.restore();
}

void HudRenderer::drawSetSpeed(QPainter &p, const QRect &surface_rect) {
  // Draw outer box + border to contain set speed
  const QSize default_size = {172, 204};
  QSize set_speed_size = default_size;

  // Adjust width for metric
  if (is_metric) {
    set_speed_size.setWidth(200);
  }

  // Center the rect horizontally with proper positioning
  int x_offset = 60;
  QRect set_speed_rect(QPoint(x_offset, 45), set_speed_size);

  // Draw set speed box
  p.setPen(QPen(QColor(255, 255, 255, 75), 6));
  p.setBrush(QColor(0, 0, 0, 166));
  p.drawRoundedRect(set_speed_rect, 32, 32);

  // Colors based on status
  QColor max_color = QColor(0xa6, 0xa6, 0xa6, 0xff);
  QColor set_speed_color = QColor(0x72, 0x72, 0x72, 0xff);
  if (is_cruise_set) {
    set_speed_color = QColor(255, 255, 255);

    switch (status) {
      case STATUS_DISENGAGED:
        max_color = QColor(255, 255, 255);
        break;
      case STATUS_OVERRIDE:
        max_color = QColor(0x91, 0x9b, 0x95, 0xff);
        break;
      default:
        max_color = QColor(0x80, 0xd8, 0xa6, 0xff);

        // Apply color interpolation based on speed limit
        float comparison_speed = (show_slc && slc_speed_limit > 0) ? slc_speed_limit : nav_speed_limit;
        if (comparison_speed > 0) {
          auto interp_color = [=](QColor c1, QColor c2, QColor c3) {
            return interpColor(set_speed, {comparison_speed + 5, comparison_speed + 15, comparison_speed + 25}, {c1, c2, c3});
          };
          max_color = interp_color(max_color, QColor(0xff, 0xe4, 0xbf), QColor(0xff, 0xbf, 0xbf));
          set_speed_color = interp_color(set_speed_color, QColor(0xff, 0x95, 0x00), QColor(0xff, 0x00, 0x00));
        }
        break;
    }
  }

  // Draw "MAX" text
  p.setFont(InterFont(40, QFont::DemiBold));
  p.setPen(max_color);
  QRect max_rect = set_speed_rect.adjusted(0, 27, 0, 0);
  p.drawText(max_rect, Qt::AlignTop | Qt::AlignHCenter, tr("MAX"));

  // Draw set speed
  QString setSpeedStr = is_cruise_set ? QString::number(std::nearbyint(set_speed)) : "–";
  p.setFont(InterFont(90, QFont::Bold));
  p.setPen(set_speed_color);
  QRect speed_rect = set_speed_rect.adjusted(0, 77, 0, 0);
  p.drawText(speed_rect, Qt::AlignTop | Qt::AlignHCenter, setSpeedStr);
}

void HudRenderer::drawSpeedLimitSigns(QPainter &p, const QRect &surface_rect) {
  // Determine which speed limit to display and create sub-text
  float display_speed = (show_slc && slc_speed_limit > 0) ? slc_speed_limit : nav_speed_limit;
  //bool is_active = show_slc ? (slc_state != static_cast<int>(cereal::LongitudinalPlanSP::SpeedLimitControlState::INACTIVE)) : true;

  if (display_speed <= 0) return;

  QString speedLimitStr = QString::number(std::nearbyint(display_speed));

  // Create sub-text for offset (like old code)
  QString slcSubText = "";
  if (show_slc && slc_speed_offset != 0) {
    slcSubText = (slc_speed_offset > 0 ? "+" : "") + QString::number(std::nearbyint(slc_speed_offset));
  }
  // Independent positioning for speed limit sign (separate from MAX speed box)
  // Use exact same dimensions as MAX speed box for both metric and imperial
  const int sign_width = is_metric ? 200 : 172;  // Same width as MAX speed box
  const int sign_x = is_metric ? 280 : 272;      // Position to the right of MAX box
  const int sign_y = 45;       // Same top alignment as MAX box

  // Use same height as MAX box for consistent sizing
  const int sign_height = 204;  // Same as MAX box height
  QRect sign_rect(sign_x, sign_y, sign_width, sign_height);

  // Draw based on metric/imperial preference
  if (!is_metric) {
    // US/Canada (MUTCD style) sign - outer white background with no border
    p.setPen(Qt::NoPen); // No outer border
    p.setBrush(QColor(255, 255, 255, 255)); // White background
    p.drawRoundedRect(sign_rect, 32, 32);

    // Draw inner rounded rectangle with black border
    QRect inner_rect = sign_rect.adjusted(10, 10, -10, -10); // Inset by 10 pixels
    p.setPen(QPen(QColor(0, 0, 0, 255), 4)); // Black border, thinner than outer
    p.setBrush(QColor(255, 255, 255, 255)); // White background
    p.drawRoundedRect(inner_rect, 22, 22); // Smaller radius for inner rect

    // "SPEED LIMIT" text - positioned relative to inner rect
    p.setFont(InterFont(30, QFont::DemiBold));
    p.setPen(QColor(0, 0, 0, 255));
    p.drawText(inner_rect.adjusted(0, 8, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("SPEED"));
    p.drawText(inner_rect.adjusted(0, 38, 0, 0), Qt::AlignTop | Qt::AlignHCenter, tr("LIMIT"));

    // Speed value with color coding - positioned relative to inner rect
    p.setFont(InterFont(75, QFont::Bold));
    QColor speed_color = over_speed_limit ? QColor(255, 0, 0, 255) : QColor(0, 0, 0, 255);
    p.setPen(speed_color);
    p.drawText(inner_rect.adjusted(0, 65, 0, 0), Qt::AlignTop | Qt::AlignHCenter, speedLimitStr);

    // Speed limit offset value
    if (!slcSubText.isEmpty()) {
      p.setFont(InterFont(28, QFont::Bold));
      p.setPen(QColor(0, 0, 0, 255));
      p.drawText(inner_rect.adjusted(0, 65 + 75, 0, 0), Qt::AlignTop | Qt::AlignHCenter, slcSubText);
    }
  } else {
    // EU (Vienna style) sign - maximize circle size to fill the entire rect
    QRect vienna_rect = sign_rect;

    // Use the absolute maximum size - the full rect with no margins at all
    int circle_size = std::min(vienna_rect.width(), vienna_rect.height());
    QRect circle_rect(vienna_rect.x(), vienna_rect.y(), circle_size, circle_size);

    // If width > height, center horizontally; if height > width, center vertically
    if (vienna_rect.width() > vienna_rect.height()) {
        circle_rect.moveLeft(vienna_rect.x() + (vienna_rect.width() - circle_size) / 2);
    } else if (vienna_rect.height() > vienna_rect.width()) {
        circle_rect.moveTop(vienna_rect.y() + (vienna_rect.height() - circle_size) / 2);
    }

    // Draw white circle background - uses maximum possible size
    p.setPen(Qt::NoPen);
    p.setBrush(QColor(255, 255, 255, 255));
    p.drawEllipse(circle_rect);

    // Draw red border ring - minimal margins to maximize size
    QRect red_ring = circle_rect.adjusted(4, 4, -4, -4);
    p.setBrush(QColor(255, 0, 0, 255)); // Red ring
    p.drawEllipse(red_ring);

    // Draw white center circle for text - very thin red ring
    QRect center_circle = red_ring.adjusted(8, 8, -8, -8);
    p.setBrush(QColor(255, 255, 255, 255)); // White center
    p.drawEllipse(center_circle);

    // Speed value - centered in white circle, similar size to MAX speed text
    int font_size = (speedLimitStr.size() >= 3) ? 70 : 85;
    p.setFont(InterFont(font_size, QFont::Bold));
    QColor speed_color = over_speed_limit ? QColor(255, 0, 0, 255) : QColor(0, 0, 0, 255);
    p.setPen(speed_color);

    // Center the speed number
    QRect speed_text_rect = center_circle;
    if (!slcSubText.isEmpty()) {
      // If we have offset text, move speed number up slightly
      speed_text_rect = center_circle.adjusted(0, -12, 0, -12);
    }
    p.drawText(speed_text_rect, Qt::AlignCenter, speedLimitStr);

    // Speed limit offset value - positioned below speed number
    if (!slcSubText.isEmpty()) {
      p.setFont(InterFont(25, QFont::Bold));
      p.setPen(QColor(0, 0, 0, 255));
      QRect offset_rect = center_circle.adjusted(0, 85, 0, 0);
      p.drawText(offset_rect, Qt::AlignCenter, slcSubText);
    }
  }
}

void HudRenderer::drawCurrentSpeed(QPainter &p, const QRect &surface_rect) {
  QString speedStr = QString::number(std::nearbyint(speed));

  p.setFont(InterFont(176, QFont::Bold));
  drawText(p, surface_rect.center().x(), 210, speedStr);

  p.setFont(InterFont(66));
  drawText(p, surface_rect.center().x(), 290, is_metric ? tr("km/h") : tr("mph"), 200);
}

void HudRenderer::drawText(QPainter &p, int x, int y, const QString &text, int alpha) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y - real_rect.height() / 2});

  p.setPen(QColor(0xff, 0xff, 0xff, alpha));
  p.drawText(real_rect.x(), real_rect.bottom(), text);
}

void HudRenderer::drawCenteredText(QPainter &p, int x, int y, const QString &text, QColor color) {
  QRect real_rect = p.fontMetrics().boundingRect(text);
  real_rect.moveCenter({x, y});

  p.setPen(color);
  p.drawText(real_rect, Qt::AlignCenter, text);
}