/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "system/hardware/hw.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"

class ExternalStorageControl : public ButtonControl {
  Q_OBJECT

public:
  ExternalStorageControl();

protected:
  void showEvent(QShowEvent *event) override;

private:
  Params params;

  void refresh();
  void mountStorage();
  void unmountStorage();
  void formatStorage();
  void runFormat();
};
