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
