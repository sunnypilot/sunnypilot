#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

achievementsd: counts driving stats and unlocks achievements while onroad.

Read-only toward the car: it only subscribes to messages, never publishes
controls. Progress is saved to a JSON file on the device (see engine.state_path)
every SAVE_INTERVAL_S and when the drive ends. The community log (map tiles,
stops, daily totals; see community.py) is saved next to it, and when the drive
ends a dry-run preview of what would be shared is written to preview/.
Nothing leaves the device.
"""
import datetime
import time

from openpilot.cereal import messaging
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.common.time_helpers import system_time_valid
from openpilot.sunnypilot.achievements.community import CommunityLog, Settings
from openpilot.sunnypilot.achievements.engine import (AchievementEngine, MAX_GPS_ACCURACY_M, Sample, load_state,
                                                      save_state)
from openpilot.sunnypilot.achievements.preview import write_preview

RATE_HZ = 10.
SAVE_INTERVAL_S = 30.
SLOW_POLL_S = 30.  # model, build and sunnylink checks
GPS_MAX_AGE_S = 2.
UNREGISTERED_SUNNYLINK_DONGLE_ID = "UnregisteredDevice"

SERVICES = ['carState', 'selfdriveState', 'selfdriveStateSP', 'modelV2', 'driverMonitoringState',
            'gpsLocation', 'gpsLocationExternal']


def _dev_build() -> bool:
  try:
    from openpilot.common.version import get_build_metadata
    bm = get_build_metadata()
    return "staging" in bm.channel or not (bm.release_channel or bm.release_sp_channel)
  except Exception:
    return False


def _active_model() -> tuple[str, str]:
  try:
    from openpilot.sunnypilot.models.helpers import get_active_bundle
    bundle = get_active_bundle()
    if bundle is None:
      return "default", "Default"
    return bundle.ref or bundle.internalName, bundle.displayName or bundle.internalName
  except Exception:
    cloudlog.exception("achievementsd: could not read the active model")
    return "", ""


def _sunnylink_linked(params: Params) -> bool:
  try:
    dongle = params.get("SunnylinkDongleId")
    return bool(params.get_bool("SunnylinkEnabled")) and dongle not in (None, "", UNREGISTERED_SUNNYLINK_DONGLE_ID)
  except Exception:
    return False


def _gps_fix(sm: messaging.SubMaster, now: float) -> tuple[float | None, float | None]:
  for svc in ('gpsLocation', 'gpsLocationExternal'):
    if sm.seen[svc] and now - sm.recv_time[svc] < GPS_MAX_AGE_S:
      g = sm[svc]
      if g.hasFix and 0 < g.horizontalAccuracy < MAX_GPS_ACCURACY_M:
        return g.latitude, g.longitude
  return None, None


def _car_platform(params: Params) -> str | None:
  try:
    from opendbc.car.structs import car
    cp_bytes = params.get("CarParams")
    if not cp_bytes:
      return None
    return messaging.log_from_bytes(cp_bytes, car.CarParams).carFingerprint or None
  except Exception:
    return None


def _open_community() -> CommunityLog | None:
  try:
    community = CommunityLog()
    _ = community.regions  # load the region table now, not mid-drive
    return community
  except Exception:
    cloudlog.exception("achievementsd: could not open the community log")
    return None


def _community_step(community: CommunityLog, sample: Sample, engine: AchievementEngine, save: bool) -> CommunityLog | None:
  """Feed one sample. On any error the community log is off until the next drive; achievements keep working."""
  try:
    community.update(sample, engine.last_step)
    if save:
      community.flush()
    return community
  except Exception:
    cloudlog.exception("achievementsd: community log failed, off until the next drive")
    community.close()
    return None


def _finish_community(community: CommunityLog, engine: AchievementEngine, params: Params) -> None:
  """Save where the drive ended and write the dry-run preview. Must stay well under the manager's 5 s stop timeout."""
  try:
    community.end_drive(engine.utc_offset_h)
    if system_time_valid():
      today = engine.local_date(datetime.datetime.now(datetime.UTC).timestamp())
      write_preview(community, engine.state, today, _car_platform(params), Settings.load())
  except Exception:
    cloudlog.exception("achievementsd: community log or preview failed")
  finally:
    community.close()


def _wall_time(valid: bool) -> float | None:
  return datetime.datetime.now(datetime.UTC).timestamp() if valid else None


def main():
  params = Params()
  sm = messaging.SubMaster(SERVICES, ignore_alive=['gpsLocation', 'gpsLocationExternal'],
                           ignore_valid=['gpsLocation', 'gpsLocationExternal'])
  engine = AchievementEngine(load_state())
  community = _open_community()
  rk = Ratekeeper(RATE_HZ, print_delay_threshold=None)

  dev_build = _dev_build()
  model_ref, model_name = _active_model()
  last_save = last_slow = time.monotonic()
  clock_ok = system_time_valid()
  engine.set_sunnylink_linked(_sunnylink_linked(params), _wall_time(clock_ok))

  try:
    while True:
      sm.update(0)
      now = time.monotonic()

      if now - last_slow > SLOW_POLL_S:
        last_slow = now
        model_ref, model_name = _active_model()
        clock_ok = system_time_valid()
        for uid in engine.set_sunnylink_linked(_sunnylink_linked(params), _wall_time(clock_ok)):
          cloudlog.event("achievement unlocked", id=uid)

      lat, lon = _gps_fix(sm, now)
      sample = Sample(
        t=now,
        v_ego=sm['carState'].vEgo,
        op_active=sm['selfdriveState'].active,
        mads_active=sm['selfdriveStateSP'].mads.active,
        lane_change_state=sm['modelV2'].meta.laneChangeState.raw,
        dm_alert_level=sm['driverMonitoringState'].alertLevel.raw,
        lat=lat,
        lon=lon,
        model_ref=model_ref,
        model_name=model_name,
        dev_build=dev_build,
        wall=_wall_time(clock_ok),
      )
      for uid in engine.update(sample):
        cloudlog.event("achievement unlocked", id=uid)

      save = now - last_save > SAVE_INTERVAL_S
      if save:
        last_save = now
        save_state(engine.state)
      if community is not None:
        community = _community_step(community, sample, engine, save)

      rk.keep_time()
  finally:
    # the manager stops us with SIGINT when the drive ends
    engine.end_drive()
    save_state(engine.state)
    if community is not None:
      _finish_community(community, engine, params)


if __name__ == "__main__":
  main()
