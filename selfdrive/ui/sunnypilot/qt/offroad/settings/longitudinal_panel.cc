/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/platform_selector.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {
  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this, false);

  toyotaFlipACC = new ParamControlSP(
    "FlipAccIncrements",
    tr("Flip ACC Controls"),
    tr("Enable this to flip Short & Long press ACC increments."),
    "",
    this);
  list->addItem(toyotaFlipACC);
  main_layout->addWidget(list);
  updateState();
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  updateState();
}

void LongitudinalPanel::updateState() {
  if (!isVisible()) {
    return;
  }

  toyotaFlipACC->setVisible(PlatformSelector::getPlatformBundle("brand").toString() == "toyota");
}
