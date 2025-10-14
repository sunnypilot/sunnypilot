/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#pragma once

enum class SpeedLimitOffsetType {
  NONE,
  FIXED,
  PERCENT,
};

inline const QString SpeedLimitOffsetTypeTexts[]{
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "None"),
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Fixed"),
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Percent"),
};

enum class SpeedLimitSourcePolicy {
  CAR_ONLY,
  MAP_ONLY,
  CAR_FIRST,
  MAP_FIRST,
  COMBINED,
};

inline const QString SpeedLimitSourcePolicyTexts[]{
  QT_TRANSLATE_NOOP("SpeedLimitPolicy", "Car\nOnly"),
  QT_TRANSLATE_NOOP("SpeedLimitPolicy", "Map\nOnly"),
  QT_TRANSLATE_NOOP("SpeedLimitPolicy", "Car\nFirst"),
  QT_TRANSLATE_NOOP("SpeedLimitPolicy", "Map\nFirst"),
  QT_TRANSLATE_NOOP("SpeedLimitPolicy", "Combined\nData")
};

enum class SpeedLimitMode {
  OFF,
  INFORMATION,
  WARNING,
  ASSIST,
};

inline const QString SpeedLimitModeTexts[]{
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Off"),
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Information"),
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Warning"),
  QT_TRANSLATE_NOOP("SpeedLimitSettings", "Assist"),
};
