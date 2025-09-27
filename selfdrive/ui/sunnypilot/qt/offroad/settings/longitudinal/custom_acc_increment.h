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

class CustomAccIncrement : public ExpandableToggleRow {
  Q_OBJECT

public:
  CustomAccIncrement(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);

private:
  QMap<QString, QString> customLongValues = {
    {"1", "1"},
    {"2", "5"}, // Default
    {"3", "10"}
  };
};

class AccIncrementOptionControl : public OptionControlSP {
  Q_OBJECT

public:
  AccIncrementOptionControl(const QString &param, const MinMaxValue &range, int per_value_change, const QMap<QString, QString> *valMap = nullptr);
  void refresh();

protected:
  std::string param_name;

private:
  Params params;
};
