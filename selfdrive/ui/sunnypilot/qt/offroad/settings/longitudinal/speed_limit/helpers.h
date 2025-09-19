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
  QObject::tr("None"),
  QObject::tr("Fixed"),
  QObject::tr("Percent"),
};

enum class SpeedLimitSourcePolicy {
  CAR_ONLY,
  MAP_ONLY,
  CAR_FIRST,
  MAP_FIRST,
  COMBINED,
};

inline const QString SpeedLimitSourcePolicyTexts[]{
  QObject::tr("Car\nOnly"),
  QObject::tr("Map\nOnly"),
  QObject::tr("Car\nFirst"),
  QObject::tr("Map\nFirst"),
  QObject::tr("Combined\nData")
};
