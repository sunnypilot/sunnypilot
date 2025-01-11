/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/device_panel.h"

DevicePanelSP::DevicePanelSP(SettingsWindowSP *parent) : DevicePanel(parent) {
  QGridLayout *grid_layout = new QGridLayout;
  grid_layout->setSpacing(30);
  grid_layout->setHorizontalSpacing(5);
  grid_layout->setVerticalSpacing(25);

  QStringList btns = {
    tr("Driver Camera Preview"), tr("Calibration Reset"),
    tr("Training Guide"),        tr("Language"),
    tr("Reboot"),                tr("Shutdown"),
  };

  int i = 0;
  for (int row = 0; row < 3; row++) {
    for (int col = 0; col < 2; col++) {
      SubPanelButton *btn = new SubPanelButton(btns[i], 730, this);
      grid_layout->addWidget(btn, row, col);
      buttons[btns[i]] = btn;
      i++;
    }
  }

  SubPanelButton *force_offroad_btn = new SubPanelButton(tr("Offroad Mode"), 730, this);
  grid_layout->addWidget(force_offroad_btn, 3, 0, 1, 1);

  QWidget *space = new QWidget(this);
  grid_layout->addWidget(space, 3, 1);

  addItem(grid_layout);
}
