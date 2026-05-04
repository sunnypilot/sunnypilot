"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import subprocess
import threading
import time

from openpilot.common.swaglog import cloudlog
from openpilot.system.ui.lib.wifi_manager import WifiManager

TETHERING_SUBNET = "192.168.43.0/24"
TETHERING_UPLINK_IFACE = "wwan0"


class WifiManagerSP(WifiManager):
  def __init__(self):
    super().__init__()
    self._set_tethering_nat_rule(False)

  @staticmethod
  def _tethering_nat_rule() -> list[str]:
    return ["POSTROUTING", "-s", TETHERING_SUBNET, "-o", TETHERING_UPLINK_IFACE, "-j", "MASQUERADE"]

  def _set_tethering_nat_rule(self, present: bool) -> None:
    nat_rule = self._tethering_nat_rule()
    exists = subprocess.run(
      ["sudo", "iptables-legacy", "-t", "nat", "-C", *nat_rule],
      check=False,
    ).returncode == 0

    if present and not exists:
      subprocess.run(["sudo", "iptables-legacy", "-t", "nat", "-A", *nat_rule], check=False)
    elif not present and exists:
      subprocess.run(["sudo", "iptables-legacy", "-t", "nat", "-D", *nat_rule], check=False)

  def set_tethering_active(self, active: bool):
    def worker():
      if active:
        self.activate_connection(self._tethering_ssid, block=True)

        if self._ipv4_forward:
          self._set_tethering_nat_rule(True)
        else:
          time.sleep(5)
          cloudlog.warning("net.ipv4.ip_forward = 0")
          subprocess.run(["sudo", "sysctl", "net.ipv4.ip_forward=0"], check=False)
      else:
        self._set_tethering_nat_rule(False)
        self._deactivate_connection(self._tethering_ssid)

    threading.Thread(target=worker, daemon=True).start()
