"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.base import BrandSettingsMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.chrysler import ChryslerSettingsMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.hyundai import HyundaiSettingsMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.subaru import SubaruSettingsMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.tesla import TeslaSettingsMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.vehicle_sub_layouts.brands.toyota import ToyotaSettingsMici

class BrandSettingsFactoryMici:
  @staticmethod
  def create_brand_settings(brand: str) -> BrandSettingsMici:
    brand = brand.lower()

    if brand == "hyundai" or brand == "kia" or brand == "genesis":
      return HyundaiSettingsMici()
    elif brand == "toyota" or brand == "lexus":
      return ToyotaSettingsMici()
    elif brand == "subaru":
      return SubaruSettingsMici()
    elif brand == "tesla":
      return TeslaSettingsMici()
    elif brand == "chrysler" or brand == "jeep" or brand == "dodge" or brand == "ram":
      return ChryslerSettingsMici()

    return BrandSettingsMici()
