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

  ListWidgetSP *list = new ListWidgetSP(this, true);

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

  refresh();
  subPanelLayout->addWidget(list);
  addWidget(subPanelFrame);
  addWidget(speedLimitPolicyScreen);
  setCurrentWidget(subPanelFrame);
}

void SpeedLimitSettings::refresh() {
}

void SpeedLimitSettings::showEvent(QShowEvent *event) {
  refresh();
}
