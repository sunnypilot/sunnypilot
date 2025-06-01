/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/slc/speed_limit_control.h"

SpeedLimitControl::SpeedLimitControl(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, desc, icon, parent) {

  auto *slcFrame = new QFrame(this);
  auto *slcFrameLayout = new QVBoxLayout();
  slcFrame->setLayout(slcFrameLayout);
  slcFrameLayout->setSpacing(0);

  auto *slcBtnFrame = new QFrame(this);
  auto *slcBtnFrameLayout = new QGridLayout();
  slcBtnFrame->setLayout(slcBtnFrameLayout);
  slcBtnFrameLayout->setSpacing(0);

  slcWarningControl = new PushButtonSP(tr("Customize Warning"));
  connect(slcWarningControl, &QPushButton::clicked, this, &SpeedLimitControl::slcWarningButtonClicked);

  slcSourceControl = new PushButtonSP(tr("Customize Source"));
  connect(slcSourceControl, &QPushButton::clicked, this, &SpeedLimitControl::slcSourceButtonClicked);

  slcWarningControl->setFixedWidth(650);
  slcSourceControl->setFixedWidth(650);
  slcBtnFrameLayout->addWidget(slcWarningControl, 0, 0, Qt::AlignLeft);
  slcBtnFrameLayout->addWidget(slcSourceControl, 0, 1, Qt::AlignRight);
  slcFrameLayout->addWidget(slcBtnFrame);


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
  slcFrameLayout->addWidget(slc_engage_setting);

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

  slcFrameLayout->addWidget(offsetFrame);

  connect(slc_offset, &OptionControlSP::updateLabels, this, &SpeedLimitControl::refresh);
  connect(slc_offset_setting, &ButtonParamControlSP::showDescriptionEvent, slc_offset, &OptionControlSP::showDescription);
  connect(slc_engage_setting, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControl::refresh);
  connect(slc_offset_setting, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControl::refresh);

  refresh();
  addItem(slcFrame);
}

void SpeedLimitControl::refresh() {
  slc_engage_setting->setDescription(engageModeDescription(static_cast<SLCEngageType>(std::stoi(params.get("SpeedLimitEngageType")))));
  slc_offset->setDescription(offsetDescription(static_cast<SLCOffsetType>(std::stoi(params.get("SpeedLimitOffsetType")))));

  QString offsetLabel = QString::fromStdString(params.get("SpeedLimitValueOffset"));
  if (static_cast<SLCOffsetType>(std::stoi(params.get("SpeedLimitOffsetType"))) == SLCOffsetType::PERCENT) {
    offsetLabel += "%";
  }

  if (static_cast<SLCOffsetType>(std::stoi(params.get("SpeedLimitOffsetType"))) == SLCOffsetType::NONE) {
    slc_offset->setDisabled(true);
    slc_offset->setLabel(tr("N/A"));
  } else {
    slc_offset->setDisabled(false);
    slc_offset->setLabel(offsetLabel);
  }

  slc_engage_setting->showDescription();
  slc_offset->showDescription();
}

void SpeedLimitControl::showEvent(QShowEvent *event) {
  refresh();
}
