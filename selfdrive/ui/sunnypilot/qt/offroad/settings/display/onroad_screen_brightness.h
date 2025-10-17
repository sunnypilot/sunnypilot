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

static const QMap<QString, QString> onroadScreenOffTimerOptions = {
  {"0", "15"},
  {"1", "30"},
  {"2", "60"},
  {"3", "120"},
  {"4", "180"},
  {"5", "240"},
  {"6", "300"},
  {"7", "360"},
  {"8", "420"},
  {"9", "480"},
  {"10", "540"},
  {"11", "600"}
};

class OnroadScreenBrightnessControl : public ExpandableToggleRow {
  Q_OBJECT

public:
  OnroadScreenBrightnessControl(const QString &param, const QString &title, const QString &desc, const QString &icon,
                                QWidget *parent = nullptr);
  void refresh();

private:
  Params params;
  OptionControlSP *onroadScreenOffTimer;
  OptionControlSP *onroadScreenBrightness;
};
