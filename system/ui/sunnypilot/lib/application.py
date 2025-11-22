"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os

SUNNYPILOT_UI = os.getenv("SUNNYPILOT_UI", "1") == "1"


class GuiApplicationExt:
  @staticmethod
  def sunnypilot_ui() -> bool:
    return SUNNYPILOT_UI
