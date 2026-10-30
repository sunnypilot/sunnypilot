"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import subprocess

from openpilot.system.ui.lib.wifi_manager import WifiManager

TETHERING_SUBNET = "192.168.43.0/24"
TETHERING_UPLINK_IFACE = "ppp0"


class WifiManagerSP(WifiManager):
  def __init__(self):
    super().__init__()

  @staticmethod
  def _tethering_nat_rule() -> list[str]:
    return ["POSTROUTING", "-s", TETHERING_SUBNET, "-o", TETHERING_UPLINK_IFACE, "-j", "MASQUERADE"]

  def _has_tethering_nat_rule(self) -> bool:
    nat_rule = self._tethering_nat_rule()
    return subprocess.run(
      ["sudo", "iptables-legacy", "-t", "nat", "-C", *nat_rule],
      check=False,
      stdout=subprocess.DEVNULL,
      stderr=subprocess.DEVNULL,
    ).returncode == 0

  def _set_tethering_nat_rule(self, present: bool) -> None:
    nat_rule = self._tethering_nat_rule()
    exists = self._has_tethering_nat_rule()

    if present and not exists:
      subprocess.run(["sudo", "iptables-legacy", "-t", "nat", "-A", *nat_rule], check=False)
    elif not present and exists:
      subprocess.run(["sudo", "iptables-legacy", "-t", "nat", "-D", *nat_rule], check=False)

  def is_tethering_internet_shared(self) -> bool:
    return self._has_tethering_nat_rule()

  def set_tethering_internet_shared(self, shared: bool) -> None:
    self._set_tethering_nat_rule(shared and self._ipv4_forward)

  def set_tethering_active(self, active: bool):
    super().set_tethering_active(active)
    if not active:
      self._set_tethering_nat_rule(False)
