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

  // Onroad Screen Off/Brightness
  onroadScreenBrightnessControl = new OnroadScreenBrightnessControl(
    "OnroadScreenOffControl",
    tr("Onroad Screen: Reduced Brightness"),
    tr("Turn off device screen or reduce brightness after driving starts. "
       "It automatically brightens again when screen is touched or a visible alert is displayed."),
    "",
    this);
  list->addItem(onroadScreenBrightnessControl);
  list->addItem(horizontal_line());

  // Global Brightness
  brightness = new Brightness();
  connect(brightness, &OptionControlSP::updateLabels, brightness, &Brightness::refresh);
  list->addItem(brightness);
  list->addItem(horizontal_line());

  // Interactivity Timeout
  interactivityTimeout =  new OptionControlSP("InteractivityTimeout", tr("Interactivity Timeout"),
                                   tr("Apply a custom timeout for settings UI."
                                      "\nThis is the time after which settings UI closes automatically if user is not interacting with the screen."),
                                   "", {0, 120}, 10, true, nullptr, false);

  connect(interactivityTimeout, &OptionControlSP::updateLabels, [=]() {
    refresh();
  });
  list->addItem(interactivityTimeout);

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

  QString timeoutValue = QString::fromStdString(params.get("InteractivityTimeout"));
  if (timeoutValue == "0" || timeoutValue.isEmpty()) {
    interactivityTimeout->setLabel("Default");
  } else {
    interactivityTimeout->setLabel(timeoutValue + "s");
  }
}
