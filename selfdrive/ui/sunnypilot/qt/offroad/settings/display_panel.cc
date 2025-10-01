/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display_panel.h"

DisplayPanel::DisplayPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QStackedLayout(this);
  ListWidgetSP *list = new ListWidgetSP(this, false);

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  sunnypilotScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(sunnypilotScroller);
  main_layout->addWidget(sunnypilotScreen);
}

void DisplayPanel::showEvent(QShowEvent *event) {
  QWidget::showEvent(event);
  refresh();
}

void DisplayPanel::refresh() {
}
