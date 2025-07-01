/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/slc/speed_limit_control_policy.h"

SpeedLimitControlPolicy::SpeedLimitControlPolicy(QWidget *parent) : QWidget(parent) {
  QVBoxLayout *main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);
  main_layout->setSpacing(0);

  // Back button
  PanelBackButton *back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  main_layout->addSpacing(10);

  ListWidgetSP *list = new ListWidgetSP(this, true);

  std::vector<QString> slc_policy_texts{
    tr(SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::CAR_ONLY)]),
    tr(SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::MAP_ONLY)]),
    tr(SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::CAR_FIRST)]),
    tr(SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::MAP_FIRST)]),
    tr(SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::COMBINED)])
  };
  slc_policy = new ButtonParamControlSP(
    "SpeedLimitControlPolicy",
    tr("Speed Limit Source"),
    "",
    "",
    slc_policy_texts,
    250);
  list->addItem(slc_policy);
  connect(slc_policy, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlPolicy::refresh);

  refresh();
  main_layout->addWidget(list);
};

void SpeedLimitControlPolicy::refresh() {
  SLCSourcePolicy policy_param = static_cast<SLCSourcePolicy>(std::atoi(params.get("SpeedLimitControlPolicy").c_str()));
  slc_policy->setDescription(sourceDescription(policy_param));
}

void SpeedLimitControlPolicy::showEvent(QShowEvent *event) {
  refresh();
  slc_policy->showDescription();
}
