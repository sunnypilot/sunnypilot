"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.base import BrandSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.body import BodySettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.chrysler import ChryslerSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.ford import FordSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.gm import GMSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.honda import HondaSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.hyundai import HyundaiSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.mazda import MazdaSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.nissan import NissanSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.psa import PSASettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.rivian import RivianSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.subaru import SubaruSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.tesla import TeslaSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.toyota import ToyotaSettings
from openpilot.selfdrive.ui.sunnypilot.layouts.settings.vehicle.brands.volkswagen import VolkswagenSettings


class BrandSettingsFactory:
  _BRAND_MAP: dict[str, type[BrandSettings]] = {
    "body": BodySettings,
    "chrysler": ChryslerSettings,
    "ford": FordSettings,
    "gm": GMSettings,
    "honda": HondaSettings,
    "hyundai": HyundaiSettings,
    "mazda": MazdaSettings,
    "nissan": NissanSettings,
    "psa": PSASettings,
    "rivian": RivianSettings,
    "subaru": SubaruSettings,
    "tesla": TeslaSettings,
    "toyota": ToyotaSettings,
    "volkswagen": VolkswagenSettings,
  }

  @staticmethod
  def create_brand_settings(brand: str) -> BrandSettings | None:
    cls = BrandSettingsFactory._BRAND_MAP.get(brand)
    return cls() if cls is not None else None
