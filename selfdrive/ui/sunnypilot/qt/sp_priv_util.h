#pragma once

#include <optional>

#define ELIDED_LABEL_SET_STUFF                          \
  void setColor(const QString &color) {                 \
    setStyleSheet("QLabel { color : " + color + "; }"); \
  }                                                     \

#define ABSTRACT_CONTROL_FUNCTION_1                                                \
  void setValue(const QString &val, std::optional<QString> color = std::nullopt) { \
    value->setText(val);                                                           \
    if (color.has_value()) {                                                       \
      value->setColor(color.value());                                              \
    }                                                                              \
  }                                                                                \

#define ABSTRACT_CONTROL_FUNCTION_2                                                \
  void hideDescription() {                                                         \
    description->setVisible(false);                                                \
  }                                                                                \

#define BUTTON_CONTROL_FUNCTION_1      \
  inline void click() { btn.click(); } \


