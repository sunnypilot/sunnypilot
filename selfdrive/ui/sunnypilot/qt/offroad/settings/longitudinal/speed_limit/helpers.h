/*
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */
#pragma once

enum class SpeedLimitMode {
  OFF,
  INFORMATION,
  WARNING,
  ASSIST,
};

inline const char *SpeedLimitModeTexts[]{
  QT_TR_NOOP("Off"),
  QT_TR_NOOP("Information"),
  QT_TR_NOOP("Warning"),
  QT_TR_NOOP("Assist"),
};

enum class SpeedLimitOffsetType {
  NONE,
  FIXED,
  PERCENT,
};

inline const char *SpeedLimitOffsetTypeTexts[]{
  QT_TR_NOOP("None"),
  QT_TR_NOOP("Fixed"),
  QT_TR_NOOP("Percent"),
};

enum class SpeedLimitSourcePolicy {
  CAR_ONLY,
  MAP_ONLY,
  CAR_FIRST,
  MAP_FIRST,
  COMBINED
};

inline const char *SpeedLimitSourcePolicyTexts[]{
  QT_TR_NOOP("Car\nOnly"),
  QT_TR_NOOP("Map\nOnly"),
  QT_TR_NOOP("Car\nFirst"),
  QT_TR_NOOP("Map\nFirst"),
  QT_TR_NOOP("Combined\nData")
};
