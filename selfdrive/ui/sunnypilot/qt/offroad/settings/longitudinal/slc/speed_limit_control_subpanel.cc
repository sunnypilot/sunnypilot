/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/slc/speed_limit_control_subpanel.h"

SpeedLimitControlSubpanel::SpeedLimitControlSubpanel(QWidget *parent) : QStackedWidget(parent) {
  subPanelFrame = new QFrame();
  QVBoxLayout *subPanelLayout = new QVBoxLayout(subPanelFrame);
  subPanelLayout->setContentsMargins(0, 0, 0, 0);
  subPanelLayout->setSpacing(0);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  subPanelLayout->addWidget(back, 0, Qt::AlignLeft);

  subPanelLayout->addSpacing(20);

  ListWidgetSP *list = new ListWidgetSP(this, true);

  auto *slcBtnFrame = new QFrame(this);
  auto *slcBtnFrameLayout = new QGridLayout();
  slcBtnFrame->setLayout(slcBtnFrameLayout);
  slcBtnFrameLayout->setContentsMargins(0, 10, 0, 10);
  slcBtnFrameLayout->setSpacing(0);

  slcWarningScreen = new SpeedLimitControlWarning(this);
  slcPolicyScreen = new SpeedLimitControlPolicy(this);

  slcWarningControl = new PushButtonSP(tr("Customize Warning"));
  connect(slcWarningControl, &QPushButton::clicked, [&]() {
    setCurrentWidget(slcWarningScreen);
    slcWarningScreen->refresh();
  });
  connect(slcWarningScreen, &SpeedLimitControlWarning::backPress, [&]() {
    setCurrentWidget(subPanelFrame);
    showEvent(new QShowEvent());
  });

  slcSourceControl = new PushButtonSP(tr("Customize Source"));
  connect(slcSourceControl, &QPushButton::clicked, [&]() {
    setCurrentWidget(slcPolicyScreen);
    slcPolicyScreen->refresh();
  });
  connect(slcPolicyScreen, &SpeedLimitControlPolicy::backPress, [&]() {
    setCurrentWidget(subPanelFrame);
    showEvent(new QShowEvent());
  });

  slcWarningControl->setFixedWidth(650);
  slcSourceControl->setFixedWidth(650);
  slcBtnFrameLayout->addWidget(slcWarningControl, 0, 0, Qt::AlignLeft);
  slcBtnFrameLayout->addWidget(slcSourceControl, 0, 1, Qt::AlignRight);
  list->addItem(slcBtnFrame);


  std::vector<QString> slc_engage_texts{
    SLCEngageTypeText[static_cast<int>(SLCEngageType::AUTO)],
  SLCEngageTypeText[static_cast<int>(SLCEngageType::USER_CONFIRM)]};
  slc_engage_setting = new ButtonParamControlSP(
    "SpeedLimitEngageType",
    tr("Engage Mode"),
    "",
    "",
    slc_engage_texts,
    300);
  list->addItem(slc_engage_setting);

  QFrame *offsetFrame = new QFrame(this);
  QVBoxLayout *offsetLayout = new QVBoxLayout(offsetFrame);

  std::vector<QString> slc_offset_texts{
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::NONE)],
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::FIXED)],
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::PERCENT)]};
  slc_offset_setting = new ButtonParamControlSP(
    "SpeedLimitOffsetType",
    tr("Speed Limit Offset"),
    "",
    "",
    slc_offset_texts,
    300);

  offsetLayout->addWidget(slc_offset_setting);

  slc_offset = new OptionControlSP(
    "SpeedLimitValueOffset",
    "",
    "",
    "",
    {-30, 30}
    );
  slc_offset->setFixedWidth(100);
  offsetLayout->addWidget(slc_offset);

  list->addItem(offsetFrame);

  connect(slc_offset, &OptionControlSP::updateLabels, this, &SpeedLimitControlSubpanel::refresh);
  connect(slc_offset_setting, &ButtonParamControlSP::showDescriptionEvent, slc_offset, &OptionControlSP::showDescription);
  connect(slc_engage_setting, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlSubpanel::refresh);
  connect(slc_offset_setting, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlSubpanel::refresh);

  refresh();
  subPanelLayout->addWidget(list);
  addWidget(subPanelFrame);
  addWidget(slcWarningScreen);
  addWidget(slcPolicyScreen);
  setCurrentWidget(subPanelFrame);
};

void SpeedLimitControlSubpanel::refresh() {
  slc_engage_setting->setDescription(engageModeDescription(static_cast<SLCEngageType>(std::atoi(params.get("SpeedLimitEngageType").c_str()))));
  slc_offset->setDescription(offsetDescription(static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitOffsetType").c_str()))));

  QString offsetLabel = QString::fromStdString(params.get("SpeedLimitValueOffset"));
  if (static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitOffsetType").c_str())) == SLCOffsetType::PERCENT) {
    offsetLabel += "%";
  }

  if (static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitOffsetType").c_str())) == SLCOffsetType::NONE) {
    slc_offset->setDisabled(true);
    slc_offset->setLabel(tr("N/A"));
  } else {
    slc_offset->setDisabled(false);
    slc_offset->setLabel(offsetLabel);
  }
}

void SpeedLimitControlSubpanel::showEvent(QShowEvent *event) {
  refresh();
  slc_engage_setting->showDescription();
  slc_offset->showDescription();
}
