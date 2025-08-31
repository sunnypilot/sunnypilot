/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include <QPainter>

#include "selfdrive/ui/qt/onroad/hud.h"
#include "selfdrive/ui/sunnypilot/qt/onroad/turnsignal_ui.h"

class HudRendererSP : public HudRenderer {
  Q_OBJECT

public:
  explicit HudRendererSP();
  void updateState(const UIState &s) override;
  void draw(QPainter &p, const QRect &surface_rect) override;
  void drawSurfaceRect(QPainter &p, const QRect &surface_rect);

protected:
  TurnSignalWidget *turnSignalWidget;

private:

};
