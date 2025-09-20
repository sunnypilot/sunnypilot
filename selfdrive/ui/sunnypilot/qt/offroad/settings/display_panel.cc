/*
 *
  * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
  *
  * This file is part of sunnypilot and is licensed under the MIT License.
  * See the LICENSE.md file in the root directory for more details.

 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/display_panel.h"

#include "display/onroad_screen_brightness.h"

DisplayPanel::DisplayPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QStackedLayout(this);
  ListWidgetSP *list = new ListWidgetSP(this, false);

  sunnypilotScreen = new QWidget(this);
  QVBoxLayout* vlayout = new QVBoxLayout(sunnypilotScreen);
  vlayout->setContentsMargins(50, 20, 50, 20);

  // Onroad Screen Off/Brightness
  onroadScreenBrightnessControl = new OnroadScreenBrightnessControl(
    "OnroadScreenOffControl",
    tr("Driving Screen Off: Non-Critical Events"),
    "Turn off device screen or reduce brightness after driving starts. "
                    "It automatically brightens again when screen is touched or a critical event occurs.",
    "",
    this);
  list->addItem(onroadScreenBrightnessControl);

  sunnypilotScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(sunnypilotScroller);
  main_layout->addWidget(sunnypilotScreen);
}

void DisplayPanel::showEvent(QShowEvent *event) {
  QWidget::showEvent(event);
  refresh();
}

void DisplayPanel::refresh() {
  onroadScreenBrightnessControl->refresh();
}
