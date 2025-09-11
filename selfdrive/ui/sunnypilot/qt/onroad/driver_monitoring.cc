/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/onroad/driver_monitoring.h"

DriverMonitorRendererSP::DriverMonitorRendererSP() {}

void DriverMonitorRendererSP::draw(QPainter &painter, const QRect &surface_rect) {
 // TODO: only apply adjustment if dev ui is enabled
 QRect adjusted_rect = surface_rect.adjusted(0, 0, 0, -50);
 DriverMonitorRenderer::draw(painter, adjusted_rect);
}
