/**
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
***/

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/sunnypilot/speed_limit_policy_settings.h"

SpeedLimitPolicySettings::SpeedLimitPolicySettings(QWidget* parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton();
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, false);

  speed_limit_policy = new ButtonParamControlSP(
    "SpeedLimitControlPolicy",
    tr("Speed Limit Source Policy"),
    "",
    "",
    speed_limit_policy_texts,
    250);
  speed_limit_policy->showDescription();
  connect(speed_limit_policy, &ButtonParamControlSP::buttonToggled, this, &SpeedLimitPolicySettings::updateToggles);
  list->addItem(speed_limit_policy);

  param_watcher = new ParamWatcher(this);

  QObject::connect(param_watcher, &ParamWatcher::paramChanged, [=](const QString &param_name, const QString &param_value) {
    updateToggles();
  });

  main_layout->addWidget(new ScrollViewSP(list, this));
}

void SpeedLimitPolicySettings::showEvent(QShowEvent *event) {
  updateToggles();
}

void SpeedLimitPolicySettings::updateToggles() {
  param_watcher->addParam("SpeedLimitControlPolicy");

  if (!isVisible()) {
    return;
  }

  // TODO: SP: use upstream's setCheckedButton
  speed_limit_policy->setButton("SpeedLimitControlPolicy");

  speed_limit_policy->setDescription(speedLimitPolicyDescriptionBuilder("SpeedLimitControlPolicy", speed_limit_policy_descriptions));
}
