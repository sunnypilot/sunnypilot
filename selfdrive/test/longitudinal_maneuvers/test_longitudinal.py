import itertools
import os

import numpy as np

from openpilot.common.parameterized import parameterized_class

from openpilot.selfdrive.controls.lib.longitudinal_mpc_lib.long_mpc import STOP_DISTANCE
from openpilot.selfdrive.test.longitudinal_maneuvers.maneuver import Maneuver


# Per-scenario quality budgets — applied only when LONG_BUDGET=1 in env.
# Wide on purpose at first; tighten after running once on the plant baseline.
# Keyed by Maneuver title. Computed from the returned `logs` array:
#   columns = t, distance, distance_lead, speed, speed_lead, acceleration, d_rel
SCENARIO_BUDGETS: dict[str, dict[str, float]] = {
  "120 kph cut-in, slower lead 25 m/s":            {'jerk_p95': 6.0, 'peak_decel': -4.0},
  "approach stopped car at 30 m/s, initial 200m":  {'jerk_p95': 5.0, 'peak_decel': -4.0},
  "approach stopped car at 33 m/s, initial 250m":  {'jerk_p95': 5.0, 'peak_decel': -4.0},
  "lead loss + reacquisition mid-decel":           {'jerk_p95': 4.0},
  "stop-and-go creep behind a slow queue":         {'jerk_p95': 3.0, 'peak_decel': -2.5},
  "slow lead pulling away from close start":       {'jerk_p95': 2.0, 'max_hard_brakes': 0},
}


# TODO: make new FCW tests
def create_maneuvers(kwargs):
  maneuvers = [
    Maneuver(
      'approach stopped car at 25m/s, initial distance: 120m',
      duration=20.,
      initial_speed=25.,
      lead_relevancy=True,
      initial_distance_lead=120.,
      speed_lead_values=[30., 0.],
      breakpoints=[0., 1.],
      **kwargs,
    ),
    Maneuver(
      'approach stopped car at 20m/s, initial distance 90m',
      duration=20.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=90.,
      speed_lead_values=[20., 0.],
      breakpoints=[0., 1.],
      **kwargs,
    ),
    Maneuver(
      'steady state following a car at 20m/s, then lead decel to 0mph at 1m/s^2',
      duration=50.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=35.,
      speed_lead_values=[20., 20., 0.],
      breakpoints=[0., 15., 35.0],
      **kwargs,
    ),
    Maneuver(
      'steady state following a car at 20m/s, then lead decel to 0mph at 2m/s^2',
      duration=50.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=35.,
      speed_lead_values=[20., 20., 0.],
      breakpoints=[0., 15., 25.0],
      **kwargs,
    ),
    Maneuver(
      'steady state following a car at 20m/s, then lead decel to 0mph at 3m/s^2',
      duration=50.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=35.,
      speed_lead_values=[20., 20., 0.],
      breakpoints=[0., 15., 21.66],
      **kwargs,
    ),
    Maneuver(
      'steady state following a car at 20m/s, then lead decel to 0mph at 3+m/s^2',
      duration=40.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=35.,
      speed_lead_values=[20., 20., 0.],
      prob_lead_values=[0., 1., 1.],
      cruise_values=[20., 20., 20.],
      breakpoints=[2., 2.01, 8.8],
      **kwargs,
    ),
    Maneuver(
      "approach stopped car at 20m/s, with prob_lead_values",
      duration=30.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=120.,
      speed_lead_values=[0.0, 0., 0.],
      prob_lead_values=[0.0, 0., 1.],
      cruise_values=[20., 20., 20.],
      breakpoints=[0.0, 2., 2.01],
      **kwargs,
    ),
    Maneuver(
      "approach stopped car at 20m/s, with prob_throttle_values and pitch = -0.1",
      duration=30.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=120.,
      speed_lead_values=[0.0, 0., 0.],
      prob_throttle_values=[1., 0., 0.],
      cruise_values=[20., 20., 20.],
      pitch_values=[0., -0.1, -0.1],
      breakpoints=[0.0, 2., 2.01],
      **kwargs,
    ),
    Maneuver(
      "approach stopped car at 20m/s, with prob_throttle_values and pitch = +0.1",
      duration=30.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=120.,
      speed_lead_values=[0.0, 0., 0.],
      prob_throttle_values=[1., 0., 0.],
      cruise_values=[20., 20., 20.],
      pitch_values=[0., 0.1, 0.1],
      breakpoints=[0.0, 2., 2.01],
      **kwargs,
    ),
    Maneuver(
      "approach slower cut-in car at 20m/s",
      duration=20.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=50.,
      speed_lead_values=[15., 15.],
      breakpoints=[1., 11.],
      only_lead2=True,
      **kwargs,
    ),
    Maneuver(
      "stay stopped behind radar override lead",
      duration=20.,
      initial_speed=0.,
      lead_relevancy=True,
      initial_distance_lead=10.,
      speed_lead_values=[0., 0.],
      prob_lead_values=[0., 0.],
      breakpoints=[1., 11.],
      only_radar=True,
      **kwargs,
    ),
    Maneuver(
      "NaN recovery",
      duration=30.,
      initial_speed=15.,
      lead_relevancy=True,
      initial_distance_lead=60.,
      speed_lead_values=[0., 0., 0.0],
      breakpoints=[1., 1.01, 11.],
      cruise_values=[float("nan"), 15., 15.],
      **kwargs,
    ),
    Maneuver(
      'cruising at 25 m/s while disabled',
      duration=20.,
      initial_speed=25.,
      lead_relevancy=False,
      enabled=False,
      **kwargs,
    ),
    Maneuver(
      "slow to 5m/s with allow_throttle = False and pitch = +0.1",
      duration=30.,
      initial_speed=20.,
      lead_relevancy=False,
      prob_throttle_values=[1., 0., 0.],
      cruise_values=[20., 20., 20.],
      pitch_values=[0., 0.1, 0.1],
      breakpoints=[0.0, 2., 2.01],
      ensure_slowdown=True,
      **kwargs,
    ),
    Maneuver(
      "120 kph cut-in, slower lead 25 m/s",
      duration=20.,
      initial_speed=33.0,
      lead_relevancy=True,
      initial_distance_lead=80.,
      speed_lead_values=[25., 25.],
      cruise_values=[35., 35.],
      breakpoints=[1., 11.],
      only_lead2=True,
      **kwargs,
    ),
    Maneuver(
      "approach stopped car at 30 m/s, initial 200m",
      duration=25.,
      initial_speed=30.,
      lead_relevancy=True,
      initial_distance_lead=200.,
      speed_lead_values=[30., 0.],
      cruise_values=[35., 35.],
      breakpoints=[0., 1.],
      **kwargs,
    ),
    Maneuver(
      "approach stopped car at 33 m/s, initial 250m",
      duration=25.,
      initial_speed=33.,
      lead_relevancy=True,
      initial_distance_lead=250.,
      speed_lead_values=[33., 0.],
      cruise_values=[35., 35.],
      breakpoints=[0., 1.],
      **kwargs,
    ),
    Maneuver(
      "lead loss + reacquisition mid-decel",
      duration=20.,
      initial_speed=20.,
      lead_relevancy=True,
      initial_distance_lead=40.,
      speed_lead_values=[20., 20., 10., 10., 10., 10.],
      prob_lead_values=[1., 1., 1., 0., 0., 1.],
      cruise_values=[22., 22., 22., 22., 22., 22.],
      breakpoints=[0., 3., 5., 5.5, 7.0, 7.5],
      **kwargs,
    ),
    Maneuver(
      "stop-and-go creep behind a slow queue",
      duration=25.,
      initial_speed=0.,
      lead_relevancy=True,
      initial_distance_lead=8.,
      speed_lead_values=[0., 2., 2., 0., 0., 3., 3., 0.],
      cruise_values=[8., 8., 8., 8., 8., 8., 8., 8.],
      breakpoints=[0., 2., 5., 6., 10., 12., 16., 20.],
      **kwargs,
    ),
    Maneuver(
      "slow lead pulling away from close start",
      duration=20.,
      initial_speed=5.,
      lead_relevancy=True,
      initial_distance_lead=8.,
      speed_lead_values=[5., 5., 20.],
      cruise_values=[20., 20., 20.],
      breakpoints=[0., 3., 15.],
      **kwargs,
    )]
  if not kwargs['force_decel']:
    # controls relies on planner commanding to move for stock-ACC resume spamming
    maneuvers.append(Maneuver(
      "resume from a stop",
      duration=20.,
      initial_speed=0.,
      lead_relevancy=True,
      initial_distance_lead=STOP_DISTANCE,
      speed_lead_values=[0., 0., 2.],
      breakpoints=[1., 10., 15.],
      ensure_start=True,
      **kwargs,
    ))
  return maneuvers


def compute_metrics(logs: np.ndarray) -> dict:
  """logs columns: t, distance, distance_lead, speed, speed_lead, acceleration, d_rel."""
  if logs is None or logs.ndim != 2 or logs.shape[0] < 2:
    return {'jerk_p95': 0.0, 'jerk_max': 0.0, 'peak_decel': 0.0, 'hard_brakes': 0}
  t = logs[:, 0]
  a = logs[:, 5]
  dt = np.diff(t)
  dt[dt <= 0] = np.median(dt[dt > 0]) if np.any(dt > 0) else 0.05
  j = np.diff(a) / dt
  return {
    'jerk_p95':    float(np.percentile(np.abs(j), 95)) if j.size else 0.0,
    'jerk_max':    float(np.max(np.abs(j))) if j.size else 0.0,
    'peak_decel':  float(np.min(a)) if a.size else 0.0,
    'hard_brakes': int(np.sum(a < -2.0)),
  }


def check_budget(title: str, metrics: dict, strict: bool) -> list[str]:
  budget = SCENARIO_BUDGETS.get(title)
  if not budget:
    return []
  failures = []
  if 'jerk_p95' in budget and metrics['jerk_p95'] > budget['jerk_p95']:
    failures.append(f"jerk_p95 {metrics['jerk_p95']:.2f} > {budget['jerk_p95']:.2f}")
  if 'peak_decel' in budget and metrics['peak_decel'] < budget['peak_decel']:
    failures.append(f"peak_decel {metrics['peak_decel']:.2f} < {budget['peak_decel']:.2f}")
  if 'max_hard_brakes' in budget and metrics['hard_brakes'] > budget['max_hard_brakes']:
    failures.append(f"hard_brakes {metrics['hard_brakes']} > {budget['max_hard_brakes']}")
  return failures


@parameterized_class(("e2e", "force_decel"), itertools.product([True, False], repeat=2))
class TestLongitudinalControl:
  e2e: bool
  force_decel: bool

  def test_maneuver(self, subtests):
    strict = os.environ.get('LONG_BUDGET', '0') == '1'
    for maneuver in create_maneuvers({"e2e": self.e2e, "force_decel": self.force_decel}):
      with subtests.test(title=maneuver.title, e2e=maneuver.e2e, force_decel=maneuver.force_decel):
        print(maneuver.title, f'in {"e2e" if maneuver.e2e else "acc"} mode')
        valid, logs = maneuver.evaluate()
        assert valid
        m = compute_metrics(logs)
        print(f"  metrics: jerk_p95={m['jerk_p95']:.2f} jerk_max={m['jerk_max']:.2f}"
              + f" peak_decel={m['peak_decel']:.2f} hard_brakes={m['hard_brakes']}")
        failures = check_budget(maneuver.title, m, strict)
        if failures:
          msg = f"budget violations on '{maneuver.title}': " + "; ".join(failures)
          if strict:
            raise AssertionError(msg)
          print(f"  ⚠ {msg}  (set LONG_BUDGET=1 to enforce)")
