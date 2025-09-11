/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include "common/swaglog.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/hud.h"

HudRendererSP::HudRendererSP() : HudRenderer()
{
  turnSignalWidget = new TurnSignalWidget();

  SteerWidget = new CircleWidget();
  SteerWidget->setup(-180.0f, 180.0f, "°", 192);
  SteerWidget->setoffset(0, 0);

  LongWidget = new CircleWidget();
  LongWidget->setup(-2.0f, 2.0f, " m/s²", 192);
  LongWidget->setoffset(0, 240);
}

void HudRendererSP::updateState(const UIState &s)
{
  const SubMaster &sm = *(s.sm);
  HudRenderer::updateState(s);
  turnSignalWidget->updateState(s);

  bool enabled = false;
  bool latActive = false;
  bool longActive = false;
  float CS_Steer = 0.0f;
  float CC_Steer = 0.0f;
  float CS_Long = 0.0f;
  float CC_Long = 0.0f;

  try
  {
    if (sm.alive("carState") && sm.rcv_frame("carState") > 0)
    {
      const auto car_state = sm["carState"].getCarState();
      enabled = car_state.getCruiseState().getAvailable();
      CS_Steer = car_state.getSteeringAngleDeg();
      CS_Long = car_state.getAEgo();
    }

    if (sm.alive("carControl") && sm.rcv_frame("carControl") > 0)
    {
      const auto car_control = sm["carControl"].getCarControl();
      latActive = car_control.getLatActive();
      longActive = car_control.getLongActive();
      if (car_control.hasActuators())
      {
        CC_Steer = car_control.getActuators().getSteeringAngleDeg();
        CC_Long = car_control.getActuators().getAccel();
      }
    }

    if (sm.alive("liveMapDataSP") && sm.rcv_frame("liveMapDataSP") > 0)
    {
      const auto live_map_data = sm["liveMapDataSP"].getLiveMapDataSP();
      road_name = QString::fromStdString(live_map_data.getRoadName());
    }
  }
  catch (const std::exception &e)
  {
    LOGE("HUD UpdateState Exception: %s", e.what());
  }

  SteerWidget->updateState(s);
  SteerWidget->setValue(enabled, latActive, -CS_Steer, -CC_Steer);

  LongWidget->updateState(s);
  LongWidget->setValue(enabled, longActive, CS_Long, CC_Long);
}

void HudRendererSP::draw(QPainter &p, const QRect &surface_rect)
{
  HudRenderer::draw(p, surface_rect);
  bool EN = false;
  EN = params.getBool("ShowRoadName");
  if (EN)
  {
    drawRoadName(p, surface_rect);
  }
  EN = params.getBool("ShowTurnSignals");
  if (EN)
  {
    turnSignalWidget->draw(p, surface_rect);
  }
  EN = params.getBool("ShowSteerState");
  if (EN)
  {
    SteerWidget->draw(p, surface_rect);
  }
  EN = params.getBool("ShowLongState");
  if (EN)
  {
    LongWidget->draw(p, surface_rect);
  }
}

void HudRendererSP::drawRoadName(QPainter &p, const QRect &surface_rect)
{
  if (road_name.isEmpty())
  {
    road_name = "None";
  }

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
  p.setBrush(QColor(0, 0, 0, 120));
  p.drawRoundedRect(road_rect, 6, 6);

  // Truncate long road names if they still don't fit
  p.setPen(QColor(255, 255, 255, 255));
  QString truncated = fm.elidedText(road_name, Qt::ElideRight, road_rect.width() - 20);
  p.drawText(road_rect, Qt::AlignCenter, truncated);
}