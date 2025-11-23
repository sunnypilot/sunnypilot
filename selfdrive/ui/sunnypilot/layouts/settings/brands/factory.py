"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.brands.hyundai import HyundaiSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.brands.subaru import SubaruSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.brands.tesla import TeslaSettings


class BrandSettingsFactory:
  @staticmethod
  def create_brand_settings(brand):
    if brand in "hyundai":
      return HyundaiSettings()
    elif brand in "subaru":
      return SubaruSettings()
    elif brand in "tesla":
      return TeslaSettings()
    return None
