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

// ListWidget
#define LIST_WIDGET_FUNCTION_1                                                                                    \
  inline void AddWidgetAt(const int index, QWidget *new_widget) { inner_layout.insertWidget(index, new_widget); } \

#define LIST_WIDGET_FUNCTION_2                                               \
  inline void RemoveWidgetAt(const int index) {                              \
    if (QLayoutItem* item; (item = inner_layout.takeAt(index)) != nullptr) { \
      if(item->widget()) delete item->widget();                              \
      delete item;                                                           \
    }                                                                        \
  }                                                                          \

#define LIST_WIDGET_FUCNTION_3                                               \
  inline void ReplaceOrAddWidget(QWidget *old_widget, QWidget *new_widget) { \
    if (const int index = inner_layout.indexOf(old_widget); index != -1) {   \
      RemoveWidgetAt(index);                                                 \
      AddWidgetAt(index, new_widget);                                        \
    } else {                                                                 \
      addItem(new_widget);                                                   \
    }                                                                        \
  }                                                                          \
