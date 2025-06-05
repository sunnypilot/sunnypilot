/*
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

enum class SLCEngageType {
  AUTO,
  USER_CONFIRM,
};

inline const char *SLCEngageTypeText[] {
  QT_TR_NOOP("Auto"),
  QT_TR_NOOP("User Confirm")
};

enum class SLCOffsetType {
  NONE,
  FIXED,
  PERCENT,
};

inline const char *SLCOffsetTypeText[] {
  QT_TR_NOOP("None"),
  QT_TR_NOOP("Fixed"),
  QT_TR_NOOP("Percent"),
};

enum class SLCWarningType {
  OFF,
  DISPLAY,
  CHIME,
};

inline const char *SLCWarningTypeText[] {
  QT_TR_NOOP("Off"),
  QT_TR_NOOP("Display"),
  QT_TR_NOOP("Chime")
};

enum class SLCSourcePolicy {
  CAR_ONLY,
  MAP_ONLY,
  CAR_FIRST,
  MAP_FIRST,
  COMBINED
};

inline const char *SLCSourcePolicyText[] {
  QT_TR_NOOP("Car\nOnly"),
  QT_TR_NOOP("Map\nOnly"),
  QT_TR_NOOP("Car\nFirst"),
  QT_TR_NOOP("Map\nFirst"),
  QT_TR_NOOP("Combined\nData")
};

class SpeedLimitControl : public ExpandableToggleRow {
    Q_OBJECT

public:
  SpeedLimitControl(const QString &param, const QString &title, const QString &desc, const QString &icon, QWidget *parent = nullptr);

signals:
  void slcSettingsButtonClicked();

private:
  Params params;
  PushButtonSP *slcSettings;
};
