/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/brand_settings_factory.h"

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/brands.h"

BrandSettingsInterface* BrandSettingsFactory::createBrandSettings(const QString& brand, QWidget* parent) {
  if (brand == "hyundai") {
    return new HyundaiSettings(parent);
  }
  // Add other brands here

  // Default empty settings if brand not supported
  return nullptr;
}

bool BrandSettingsFactory::isBrandSupported(const QString& brand) {
  static const QStringList supportedBrands = {
    "chrysler",
    "hyundai",
  };

  return supportedBrands.contains(brand);
}

QStringList BrandSettingsFactory::getSupportedBrands() {
  static const QStringList supportedBrands = {
    "hyundai",
  };

  return supportedBrands;
}
