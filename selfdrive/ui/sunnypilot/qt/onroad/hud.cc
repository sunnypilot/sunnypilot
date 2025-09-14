/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/onroad/hud.h"

HudRendererSP::HudRendererSP() {}

void HudRendererSP::updateState(const UIState &s) {
  HudRenderer::updateState(s);
}

void HudRendererSP::draw(QPainter &p, const QRect &surface_rect) {
  HudRenderer::draw(p, surface_rect);
}
