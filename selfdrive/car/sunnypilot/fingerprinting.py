from collections.abc import Callable

import cereal.messaging as messaging
from openpilot.selfdrive.car import gen_empty_fingerprint

FRAME_FINGERPRINT = 25  # 0.25s


def get_one_can(logcan):
  while True:
    can = messaging.recv_one_retry(logcan)
    if len(can.can) > 0:
      return can


def can_fingerprint(next_can: Callable) -> tuple[str | None, dict[int, dict]]:
  finger = gen_empty_fingerprint()
  frame = 0
  done = False

  while not done:
    a = next_can()

    for can in a.can:
      # The fingerprint dict is generated for all buses, this way the car interface
      # can use it to detect a (valid) multipanda setup and initialize accordingly
      if can.src < 128:
        if can.src not in finger:
          finger[can.src] = {}
        finger[can.src][can.address] = len(can.dat)

    # bail if we've been waiting for more than 2s
    done = frame > 100

    frame += 1

  return finger
