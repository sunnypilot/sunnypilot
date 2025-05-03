/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {

  QVBoxLayout* main_layout = new QVBoxLayout(this);
  main_layout->setMargin(0);

  listWidget = new ListWidgetSP(this);
  listWidget->setContentsMargins(0, 0, 0, 0);
  listWidget->setSpacing(0);
  main_layout->addWidget(listWidget);

  customAccIncrement = new CustomAccIncrement("CustomAccIncrementsEnabled", "Custom ACC Speed Increments", "Enable custom Short & Long press increments for cruise speed increase/decrease.", "", this);
  listWidget->addItem(customAccIncrement);

  main_layout->addStretch();
}
