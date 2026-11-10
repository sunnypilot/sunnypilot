"""The replay tool, fed fake log messages (the real LogReader needs the full openpilot build)."""
import datetime as dt
import os
from types import SimpleNamespace as NS

from openpilot.sunnypilot.achievements.community import CommunityLog, tile_of
from openpilot.sunnypilot.achievements.engine import AchievementEngine, State
from openpilot.sunnypilot.achievements.replay import RouteFeeder, find_routes
from openpilot.sunnypilot.achievements.simulate import HOME, WORK

T0 = int(dt.datetime(2026, 11, 2, 13, 0, tzinfo=dt.UTC).timestamp() * 1e3)


class Ev:
  def __init__(self, kind: str, mono_s: float, **fields):
    self._kind, self.logMonoTime = kind, int(mono_s * 1e9)
    setattr(self, kind, NS(**fields))

  def which(self):
    return self._kind


def fake_route(start, end, seconds=600):
  yield Ev("carParams", 0.0, carFingerprint="HYUNDAI_IONIQ_5")
  yield Ev("selfdriveState", 0.0, active=True)
  yield Ev("selfdriveStateSP", 0.0, mads=NS(active=False))
  yield Ev("driverMonitoringState", 0.0, alertLevel=NS(raw=0))
  for i in range(seconds * 10):  # carState at 10 Hz, GPS at 1 Hz, like a qlog
    t = i / 10
    if i % 10 == 0:
      f = t / seconds
      yield Ev("gpsLocationExternal", t, hasFix=True, horizontalAccuracy=5.0,
               latitude=start[0] + (end[0] - start[0]) * f, longitude=start[1] + (end[1] - start[1]) * f,
               unixTimestampMillis=T0 + int(t * 1000))
    yield Ev("carState", t, vEgo=30.0)


def test_route_feeder_counts_a_drive(tmp_path):
  engine, log = AchievementEngine(State()), CommunityLog(tmp_path / "c.db")
  feeder = RouteFeeder(engine, log)
  for ev in fake_route(HOME, WORK):
    feeder.feed(ev)
  engine.end_drive()
  log.end_drive(engine.utc_offset_h)

  assert feeder.car == "HYUNDAI_IONIQ_5"
  assert 17_000 < engine.state.engaged_m < 18_500  # 600 s at 30 m/s
  assert engine.state.days == ["2026-11-02"]
  view = log.tile_view(dt.date(2026, 11, 3))
  assert tile_of(*HOME) in view.held  # where the drive started
  assert len(view.driven) > 3
  assert log.home_region(dt.date(2026, 11, 3)) == "US-OH"


def test_find_routes(tmp_path):
  for name, mtime in (("00000002--bbbb--0", 200), ("00000002--bbbb--1", 260), ("00000001--aaaa--0", 100),
                      ("00000001--aaaa--10", 160), ("00000001--aaaa--2", 130), ("boot", 0)):
    d = tmp_path / name
    d.mkdir()
    if name != "boot":
      (d / "qlog.zst").write_bytes(b"")
      os.utime(d / "qlog.zst", (mtime, mtime))
  routes = find_routes(tmp_path, rlog=False, days=None)
  assert [[p.parent.name for p in r] for r in routes] == [
    ["00000001--aaaa--0", "00000001--aaaa--2", "00000001--aaaa--10"],
    ["00000002--bbbb--0", "00000002--bbbb--1"],
  ]
  assert find_routes(tmp_path, rlog=True, days=None) == []
