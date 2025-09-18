/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/speed_limit/speed_limit_assist.h"

SpeedLimitAssist::SpeedLimitAssist(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, desc, icon, parent) {

  auto *speedLimitFrame = new QFrame(this);
  auto *speedLimitFrameLayout = new QVBoxLayout();
  speedLimitFrame->setLayout(speedLimitFrameLayout);
  speedLimitFrameLayout->setSpacing(0);
  speedLimitFrameLayout->setContentsMargins(0, 0, 0, 0);

  speedLimitSettings = new PushButtonSP(tr("Customize Speed Limit"));
  speedLimitFrameLayout->addWidget(speedLimitSettings);
  connect(speedLimitSettings, &QPushButton::clicked, [&]() {
    emit speedLimitSettingsButtonClicked();
  });
  addItem(speedLimitFrame);
}
