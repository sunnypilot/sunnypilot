"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import abc


class BrandSettings(abc.ABC):
  def __init__(self):
    self.items = []

  @abc.abstractmethod
  def update_settings(self) -> None:
    """Update the settings based on the current vehicle brand."""
