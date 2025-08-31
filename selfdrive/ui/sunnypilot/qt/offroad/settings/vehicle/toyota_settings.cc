/**
 * Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.
 *
 * This file is part of sunnypilot and is licensed under the MIT License.
 * See the LICENSE.md file in the root directory for more details.
 */

#include "selfdrive/ui/sunnypilot/qt/offroad/settings/vehicle/toyota_settings.h"

ToyotaSettings::ToyotaSettings(QWidget *parent) : BrandSettingsInterface(parent)
{
    // 自己的 5 個開關設定
  std::vector<std::tuple<QString, QString, QString, QString, bool>> toggle_defs = {
      {"Test1", tr("Test 1"), tr("Description for Test1"), "../assets/icons/chffr_wheel.png", true},
      {"Test2", tr("Test 2"), tr("Description for Test2"), "../assets/icons/chffr_wheel.png", true},
      {"Test3", tr("Test 3"), tr("Description for Test3"), "../assets/icons/chffr_wheel.png", true},
      {"Test4", tr("Test 4"), tr("Description for Test4"), "../assets/icons/chffr_wheel.png", true},
      {"Test5", tr("Test 5"), tr("Description for Test5"), "../assets/icons/chffr_wheel.png", true},
  };
  SetToggles(toggle_defs);
}

void ToyotaSettings::updateSettings()
{

}