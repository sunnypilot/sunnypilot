/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/slc/speed_limit_control.h"

SpeedLimitControl::SpeedLimitControl(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent)
    : ExpandableToggleRow(param, title, desc, icon, parent) {

  auto *slcFrame = new QFrame(this);
  auto *slcFrameLayout = new QVBoxLayout();
  slcFrame->setLayout(slcFrameLayout);
  slcFrameLayout->setSpacing(0);

  slcSettings = new PushButtonSP(tr("Customize SLC"));
  slcFrameLayout->addWidget(slcSettings);
  connect(slcSettings, &QPushButton::clicked, [&]() {
    emit slcSettingsButtonClicked();
  });
  addItem(slcFrame);

}
