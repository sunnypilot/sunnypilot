/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_settings.h"

SpeedLimitSettings::SpeedLimitSettings(QWidget *parent) : QStackedWidget(parent) {
  subPanelFrame = new QFrame();
  QVBoxLayout *subPanelLayout = new QVBoxLayout(subPanelFrame);
  subPanelLayout->setContentsMargins(0, 0, 0, 0);
  subPanelLayout->setSpacing(0);

  // Back button
  PanelBackButton *back = new PanelBackButton(tr("Back"));
  connect(back, &QPushButton::clicked, [=]() { emit backPress(); });
  subPanelLayout->addWidget(back, 0, Qt::AlignLeft);

  subPanelLayout->addSpacing(20);

  ListWidgetSP *list = new ListWidgetSP(this);

  auto *speedLimitBtnFrame = new QFrame(this);
  auto *speedLimitBtnFrameLayout = new QGridLayout();
  speedLimitBtnFrame->setLayout(speedLimitBtnFrameLayout);
  speedLimitBtnFrameLayout->setContentsMargins(0, 40, 0, 40);
  speedLimitBtnFrameLayout->setSpacing(0);

  speedLimitPolicyScreen = new SpeedLimitPolicy(this);

  speedLimitSource = new PushButtonSP(tr("Customize Source"));
  connect(speedLimitSource, &QPushButton::clicked, [&]() {
    setCurrentWidget(speedLimitPolicyScreen);
    speedLimitPolicyScreen->refresh();
  });
  connect(speedLimitPolicyScreen, &SpeedLimitPolicy::backPress, [&]() {
    setCurrentWidget(subPanelFrame);
    showEvent(new QShowEvent());
  });

  speedLimitSource->setFixedWidth(720);
  speedLimitBtnFrameLayout->addWidget(speedLimitSource, 0, 0, Qt::AlignLeft);
  list->addItem(speedLimitBtnFrame);

  QFrame *offsetFrame = new QFrame(this);
  QVBoxLayout *offsetLayout = new QVBoxLayout(offsetFrame);

  std::vector<QString> speed_limit_offset_texts{
    SpeedLimitOffsetTypeTexts[static_cast<int>(SpeedLimitOffsetType::NONE)],
    SpeedLimitOffsetTypeTexts[static_cast<int>(SpeedLimitOffsetType::FIXED)],
    SpeedLimitOffsetTypeTexts[static_cast<int>(SpeedLimitOffsetType::PERCENT)]
  };
  speed_limit_offset_settings = new ButtonParamControlSP(
    "SpeedLimitOffsetType",
    tr("Speed Limit Offset"),
    "",
    "",
    speed_limit_offset_texts,
    500);

  offsetLayout->addWidget(speed_limit_offset_settings);

  speed_limit_offset = new OptionControlSP(
    "SpeedLimitValueOffset",
    "",
    "",
    "",
    {-30, 30}
    );
  offsetLayout->addWidget(speed_limit_offset);

  list->addItem(offsetFrame);

  connect(speed_limit_offset, &OptionControlSP::updateLabels, this, &SpeedLimitSettings::refresh);
  connect(speed_limit_offset_settings, &ButtonParamControlSP::showDescriptionEvent, speed_limit_offset, &OptionControlSP::showDescription);
  connect(speed_limit_offset_settings, &ButtonParamControlSP::buttonClicked, this, &SpeedLimitSettings::refresh);

  refresh();
  subPanelLayout->addWidget(list);
  addWidget(subPanelFrame);
  addWidget(speedLimitPolicyScreen);
  setCurrentWidget(subPanelFrame);
}

void SpeedLimitSettings::refresh() {
  bool is_metric_param = params.getBool("IsMetric");
  SpeedLimitOffsetType offset_type_param = static_cast<SpeedLimitOffsetType>(std::atoi(params.get("SpeedLimitOffsetType").c_str()));
  QString offsetLabel = QString::fromStdString(params.get("SpeedLimitValueOffset"));

  speed_limit_offset->setDescription(offsetDescription(offset_type_param));

  if (offset_type_param == SpeedLimitOffsetType::PERCENT) {
    offsetLabel += "%";
  } else if (offset_type_param == SpeedLimitOffsetType::FIXED) {
    offsetLabel += QString(" %1").arg(is_metric_param ? "km/h" : "mph");
  }

  if (offset_type_param == SpeedLimitOffsetType::NONE) {
    speed_limit_offset->setVisible(false);
  } else {
    speed_limit_offset->setVisible(true);
    speed_limit_offset->setLabel(offsetLabel);
    speed_limit_offset->showDescription();
  }
}

void SpeedLimitSettings::showEvent(QShowEvent *event) {
  refresh();
  speed_limit_offset->showDescription();
}
