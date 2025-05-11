/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/longitudinal/custom_acc_increment.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"


class LongitudinalPanel : public QWidget {
  Q_OBJECT

public:
  explicit LongitudinalPanel(QWidget *parent = nullptr);

private:
  CustomAccIncrement *customAccIncrement = nullptr;
  ListWidgetSP *listWidget = nullptr;
};
