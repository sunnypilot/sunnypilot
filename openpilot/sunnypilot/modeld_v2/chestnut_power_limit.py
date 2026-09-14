"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from tinygrad.device import Device

from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog

# A chestnut powered from a 12V accessory outlet sits behind wiring built for
# 1-2 A dashcams: a ~0.4 ohm path sags ~5 V at the GPU's stock boost transients,
# which resets the USB link mid-transfer or hangs the device seconds into
# inference. Bounding the SMU package power (PPT) removes those transients; the
# driving models run within 60 W (24-55 W measured on a Radeon 9060 16 GB, whose
# stock limit reads back as 160 W). chestnut is designed for 100 W of inference,
# so nothing above that is offered. 0 leaves the GPU's own limit untouched.
POWER_LIMIT_MIN_W = 40
POWER_LIMIT_MAX_W = 100


def get_power_limit(params: Params | None = None) -> int:
  """Requested package power limit in watts from ChestnutPowerLimit, clamped to a sane range. 0 means stock."""
  params = params or Params()
  try:
    limit_w = int(params.get("ChestnutPowerLimit", return_default=True) or 0)
  except (TypeError, ValueError):
    return 0
  if limit_w <= 0:
    return 0
  return max(POWER_LIMIT_MIN_W, min(POWER_LIMIT_MAX_W, limit_w))


def apply_power_limit(limit_w: int) -> int | None:
  """Set the SMU package power limit on the opened AMD device and return the value it reports back. No-op for 0."""
  if limit_w <= 0:
    return None
  smu = Device["AMD"].iface.dev_impl.smu
  smu._send_msg(smu.smu_mod.PPSMC_MSG_SetPptLimit, limit_w, timeout=100)
  applied = int(smu._send_msg(smu.smu_mod.PPSMC_MSG_GetPptLimit, 0, read_back_arg=True, timeout=100))
  cloudlog.event("chestnut power limit", requested=limit_w, applied=applied, error=applied != limit_w)
  return applied
