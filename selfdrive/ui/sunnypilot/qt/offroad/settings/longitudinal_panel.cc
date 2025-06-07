/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal_panel.h"

LongitudinalPanel::LongitudinalPanel(QWidget *parent) : QWidget(parent) {

  main_layout = new QStackedLayout(this);
  ListWidget *list = new ListWidget(this, false);

  cruisePanelScreen = new QWidget(this);
  QVBoxLayout *vlayout = new QVBoxLayout(cruisePanelScreen);
  vlayout->setContentsMargins(0, 0, 0, 0);

  cruisePanelScroller = new ScrollViewSP(list, this);
  vlayout->addWidget(cruisePanelScroller);


  customAccIncrement = new CustomAccIncrement(
    "CustomAccIncrementsEnabled",
    tr("Custom ACC Speed Increments"),
    "",
    "",
    this);
  list->addItem(customAccIncrement);

  main_layout->addWidget(cruisePanelScreen);
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh();
}

void LongitudinalPanel::showEvent(QShowEvent *event) {
  main_layout->setCurrentWidget(cruisePanelScreen);
  refresh();
}

void LongitudinalPanel::refresh() {
  auto cp_bytes = params.get("CarParamsPersistent");
  bool has_longitudinal_control;
  bool is_pcm_cruise;
  if (!cp_bytes.empty()) {
    AlignedBuffer aligned_buf;
    capnp::FlatArrayMessageReader cmsg(aligned_buf.align(cp_bytes.data(), cp_bytes.size()));
    cereal::CarParams::Reader CP = cmsg.getRoot<cereal::CarParams>();
    has_longitudinal_control = hasLongitudinalControl(CP);
    is_pcm_cruise = CP.getPcmCruise();
  } else {
    has_longitudinal_control = false;
    is_pcm_cruise = true;
  }
  QString accEnabledDescription = tr("Enable custom Short & Long press increments for cruise speed increase/decrease.");
  QString accNoLongDescription = tr("This feature can only be used with openpilot longitudinal control enabled.");
  if (has_longitudinal_control) {
    if (is_pcm_cruise) {
      customAccIncrement->setVisible(false);
    } else {
      customAccIncrement->setDescription(accEnabledDescription);
      customAccIncrement->setEnabled(true);
    }
  } else {
    customAccIncrement->setDescription(accNoLongDescription);
    customAccIncrement->showDescription();
    customAccIncrement->setEnabled(false);
  }
}
