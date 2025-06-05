/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/slc/speed_limit_control_warning.h"

SpeedLimitControlWarning::SpeedLimitControlWarning(QWidget *parent) : QWidget(parent) {
  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setContentsMargins(0, 0, 0, 0);
  main_layout->setSpacing(0);

  // Back button
  PanelBackButton* back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  main_layout->addWidget(back, 0, Qt::AlignLeft);

  main_layout->addSpacing(10);

  ListWidgetSP *list = new ListWidgetSP(this, true);

  std::vector<QString> slc_warning_texts{
    SLCWarningTypeText[static_cast<int>(SLCWarningType::OFF)],
    SLCWarningTypeText[static_cast<int>(SLCWarningType::DISPLAY)],
    SLCWarningTypeText[static_cast<int>(SLCWarningType::CHIME)]};
  slc_warning_settings = new ButtonParamControlSP(
    "SpeedLimitWarningType", tr("Speed Limit Warning"),
    "",
    "",
    slc_warning_texts,
    300);
  list->addItem(slc_warning_settings);

  QFrame *offsetFrame = new QFrame(this);
  QVBoxLayout *offsetLayout = new QVBoxLayout(offsetFrame);

  std::vector<QString> slc_warning_offset_texts{
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::NONE)],
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::FIXED)],
    SLCOffsetTypeText[static_cast<int>(SLCOffsetType::PERCENT)]};
  slc_warning_offset_settings = new ButtonParamControlSP(
    "SpeedLimitWarningOffsetType",
    tr("Warning Offset"),
    "",
    "",
    slc_warning_offset_texts,
    300);
  offsetLayout->addWidget(slc_warning_offset_settings);

  slc_warning_offset = new OptionControlSP(
    "SpeedLimitWarningValueOffset",
    "",
    "",
    "",
    {-30, 30}
    );
  slc_warning_offset->setFixedWidth(100);
  offsetLayout->addWidget(slc_warning_offset);

  list->addItem(offsetFrame);

  connect(slc_warning_offset, &OptionControlSP::updateLabels, this, &SpeedLimitControlWarning::refresh);
  connect(slc_warning_offset_settings, &ButtonParamControlSP::showDescriptionEvent, slc_warning_offset, &OptionControlSP::showDescription);
  connect(slc_warning_settings, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlWarning::refresh);
  connect(slc_warning_offset_settings, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitControlWarning::refresh);

  refresh();
  main_layout->addWidget(list);
};

void SpeedLimitControlWarning::refresh() {
  slc_warning_settings->setDescription(warningDescription(static_cast<SLCWarningType>(std::atoi(params.get("SpeedLimitWarningType").c_str()))));
  slc_warning_offset->setDescription(offsetDescription(static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitWarningOffsetType").c_str()))));

  QString offsetLabel = QString::fromStdString(params.get("SpeedLimitWarningValueOffset"));
  if (static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitWarningOffsetType").c_str())) == SLCOffsetType::PERCENT) {
    offsetLabel += "%";
  }

  if (static_cast<SLCOffsetType>(std::atoi(params.get("SpeedLimitWarningOffsetType").c_str())) == SLCOffsetType::NONE) {
    slc_warning_offset->setDisabled(true);
    slc_warning_offset->setLabel(tr("N/A"));
  } else {
    slc_warning_offset->setDisabled(false);
    slc_warning_offset->setLabel(offsetLabel);
  }
}

void SpeedLimitControlWarning::showEvent(QShowEvent *event) {
  refresh();
  slc_warning_settings->showDescription();
  slc_warning_offset->showDescription();
}
