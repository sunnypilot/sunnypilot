/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#pragma once

#include "selfdrive/ui/sunnypilot/ui.h"
#include "selfdrive/ui/sunnypilot/qt/offroad/settings/settings.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/controls.h"
#include "selfdrive/ui/sunnypilot/qt/widgets/expandable_row.h"

class TorqueLateralControlCustomParams : public ExpandableToggleRow {
  Q_OBJECT

public:
  TorqueLateralControlCustomParams(const QString &param, const QString &title, const QString &description, const QString &icon, QWidget *parent = nullptr);
  void refresh();

private:
  Params params;
  ParamControl *torqueLateralControlParamsOverride;
  OptionControlSP *torqueParamsOverrideFriction;
  OptionControlSP *torqueParamsOverrideLatAccelFactor;
};
