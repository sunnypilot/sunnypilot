/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/slc/speed_limit_control_source.h"

SpeedLimitControlSource::SpeedLimitControlSource(QWidget *parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(50, 20, 50, 20);
  main_layout->setSpacing(20);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  ListWidgetSP *list = new ListWidgetSP(this, true);

  std::vector<QString> slc_policy_texts{
    SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::CAR_ONLY)],
  SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::MAP_ONLY)],
    SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::CAR_FIRST)],
    SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::MAP_FIRST)],
  SLCSourcePolicyText[static_cast<int>(SLCSourcePolicy::COMBINED)]};
  slc_policy = new ButtonParamControlSP(
    "SpeedLimitControlPolicy",
    tr("Speed Limit Source"),
    "",
    "",
    slc_policy_texts,
    250);
  list->addItem(slc_policy);
  connect(slc_policy, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlSource::refresh);

  refresh();
  main_layout->addWidget(list);
};

void SpeedLimitControlSource::refresh() {
  slc_policy->setDescription(sourceDescription(static_cast<SLCSourcePolicy>(std::stoi(params.get("SpeedLimitControlPolicy")))));
  slc_policy->showDescription();
}

void SpeedLimitControlSource::showEvent(QShowEvent *event) {
  refresh();
}
