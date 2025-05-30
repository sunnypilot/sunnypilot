/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class ExpandableToggleRow : public ToggleControlSP {
  Q_OBJECT

public:
  ExpandableToggleRow(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);

  void addItem(QWidget *widget) {
    list->addItem(widget);
  }

  ListWidgetSP *innerList() {
    return list;
  }

  void refresh() {
    bool state = params.getBool(key);
    if (state != toggle.on) {
      toggle.togglePosition();
    }
    collapsibleWidget->setVisible(state);
  }

  bool isToggled() {
    return params.getBool(key);
  }

  void showEvent(QShowEvent *event) override {
    refresh();
  }

private:
  void toggleClicked(bool state);

  std::string key;
  Params params;

  ListWidgetSP *list;
  QFrame *collapsibleWidget = nullptr;
};
