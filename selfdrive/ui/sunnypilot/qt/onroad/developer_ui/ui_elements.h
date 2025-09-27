/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#pragma once

#include <QColor>

struct UiElement {
  QString value{};
  QString label{};
  QString units{};
  QColor color{};

  explicit UiElement(const QString &value = "", const QString &label = "", const QString &units = "", const QColor &color = QColor(255, 255, 255, 255))
    : value(value), label(label), units(units), color(color) {}
};
