/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#include <QScrollBar>

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_policy.h"

SpeedLimitPolicy::SpeedLimitPolicy(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);
  main_layout->setSpacing(0);

  // Back button
  PanelBackButton *back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  main_layout->addSpacing(10);

  ListWidgetSP *list = new ListWidgetSP(this);

  std::vector<QString> speed_limit_policy_texts{
    tr(SpeedLimitSourcePolicyTexts[static_cast<int>(SpeedLimitSourcePolicy::CAR_ONLY)].toStdString().c_str()),
    tr(SpeedLimitSourcePolicyTexts[static_cast<int>(SpeedLimitSourcePolicy::MAP_ONLY)].toStdString().c_str()),
    tr(SpeedLimitSourcePolicyTexts[static_cast<int>(SpeedLimitSourcePolicy::CAR_FIRST)].toStdString().c_str()),
    tr(SpeedLimitSourcePolicyTexts[static_cast<int>(SpeedLimitSourcePolicy::MAP_FIRST)].toStdString().c_str()),
    tr(SpeedLimitSourcePolicyTexts[static_cast<int>(SpeedLimitSourcePolicy::COMBINED)].toStdString().c_str())
  };
  speed_limit_policy = new ButtonParamControlSP(
    "SpeedLimitPolicy",
    tr("Speed Limit Source"),
    "",
    "",
    speed_limit_policy_texts,
    250);
  list->addItem(speed_limit_policy);
  connect(speed_limit_policy, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitPolicy::refresh);

  speedLimitPolicyScroller = new ScrollViewSP(list, this);
  main_layout->addWidget(speedLimitPolicyScroller);
  refresh();
};

void SpeedLimitPolicy::refresh() {
  SpeedLimitSourcePolicy policy_param = static_cast<SpeedLimitSourcePolicy>(std::atoi(params.get("SpeedLimitPolicy").c_str()));
  speed_limit_policy->setDescription(sourceDescription(policy_param));
}

void SpeedLimitPolicy::showEvent(QShowEvent *event) {
  speedLimitPolicyScroller->verticalScrollBar()->setValue(0);
  refresh();
  speed_limit_policy->showDescription();
}
