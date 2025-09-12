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
}

void HudRendererSP::draw(QPainter &p, const QRect &surface_rect)
{
  HudRenderer::draw(p, surface_rect);
  bool EN = false;
  EN = params.getBool("ShowTurnSignals");
  if (EN)
  {
    turnSignalWidget->draw(p, surface_rect);
  }
}