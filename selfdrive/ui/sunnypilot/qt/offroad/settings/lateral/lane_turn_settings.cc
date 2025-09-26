/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/lateral/lane_turn_settings.h"


LaneTurnSettings::LaneTurnSettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);
  // Lane Turn Desire Control
  laneTurnDesireControl = new LaneTurnDesireControl();
  laneTurnDesireControl->setUpdateOtherToggles(true);
  laneTurnDesireControl->showDescription();
  connect(laneTurnDesireControl, &OptionControlSP::updateLabels, laneTurnDesireControl, &LaneTurnDesireControl::refresh);
  list->addItem(laneTurnDesireControl);

  // Lane Turn Value control
  bool is_metric = params.getBool("IsMetric");
  int per_value_change = is_metric ? 62 : 100; // ~1 km/h or 1 mph
  laneTurnValueControl = new OptionControlSP("LaneTurnValue", tr("Adjust Lane Turn Speed"),
    tr("Set the maximum speed for lane turn desires. Default is 19 %1.").arg(is_metric ? "km/h" : "mph"),
    "", {500, 2000}, per_value_change, false, nullptr, true, true);
  laneTurnValueControl->showDescription();
  list->addItem(laneTurnValueControl);

  // show/hide value control based on desire
  connect(laneTurnDesireControl, &OptionControlSP::updateLabels, this, &LaneTurnSettings::updateValueControlVisibility);
  connect(laneTurnValueControl, &OptionControlSP::updateLabels, this, &LaneTurnSettings::refreshLaneTurnValueControl);
  main_layout->addWidget(new ScrollViewSP(list, this));
}

void LaneTurnSettings::showEvent(QShowEvent *event) {
  updateValueControlVisibility();
}

void LaneTurnSettings::updateValueControlVisibility() {
  QString option = QString::fromStdString(params.get("LaneTurnDesire"));
  bool visible = (option != "0");
  laneTurnValueControl->setVisible(visible);
  if (visible) {
    refreshLaneTurnValueControl();
  }
}

void LaneTurnSettings::refreshLaneTurnValueControl() {
  if (!laneTurnValueControl) return;
  float stored_mph = QString::fromStdString(params.get("LaneTurnValue")).toFloat();
  bool is_metric = params.getBool("IsMetric");
  QString unit = is_metric ? "km/h" : "mph";
  float display_value = is_metric ? stored_mph * 1.609344f : stored_mph;
  laneTurnValueControl->setLabel(QString::number(qRound(display_value)) + " " + unit);
}

// Lane Turn Desire Control
LaneTurnDesireControl::LaneTurnDesireControl() : OptionControlSP(
  "LaneTurnDesire",
  tr("Lane Turn Desires"),
  tr("If you're driving at 20 mph (32 km/h) or below and have your blinker on, "
     "the car will plan a turn in that direction at the nearest drivable path. "
     "This prevents situations (like at red lights) where the car might plan the wrong turn direction."),
  "../assets/offroad/icon_shell.png",
  {0, 2}) {
  refresh();
}

void LaneTurnDesireControl::refresh() {
  QString option = QString::fromStdString(params.get("LaneTurnDesire"));
  static const QMap<QString, QString> options = {
    {"0", tr("Off")},
    {"1", tr("Nudge")},
    {"2", tr("Nudgeless")},
  };
  setLabel(options.value(option, tr("Off")));
}
