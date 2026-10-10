"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import numpy as np

from openpilot.common.params import Params
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.selfdrive.controls.lib.accel_controller.accel_controller import (
  AccelController, AccelProfile, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES,
)


class TestEcoLeadBoost(OpenpilotTestCase):
  """Eco lead pull-away boost (driver 2026-10-01 night)."""

  @staticmethod
  def _ac(profile):
    from types import SimpleNamespace
    ac = AccelController.__new__(AccelController)
    ac._profile, ac._enabled, ac._boost = profile, True, 0.0
    ac._cruise_decel = ac._cruise_decel_target = None
    return ac, SimpleNamespace

  def test_no_lead_unchanged(self):
    ac, _ = self._ac(AccelProfile.eco)
    v = 15.0
    base = float(np.interp(v, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.eco]))
    for _ in range(100):
      assert ac.get_max_accel(v, False, None) == base

  def test_pulling_away_lead_boosts_smoothly_within_normal(self):
    ac, NS = self._ac(AccelProfile.eco)
    v = 15.0
    lead = NS(present=True, modelProb=0.9, dRel=30.0, vLead=v + 3.0)
    base = float(np.interp(v, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.eco]))
    normal = float(np.interp(v, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.normal]))
    out = [ac.get_max_accel(v, False, lead) for _ in range(60)]
    steps = np.diff([base] + out)
    assert max(steps) <= 0.25 * 0.05 + 1e-9          # eased in
    assert out[-1] > base + 0.2 and out[-1] <= normal + 1e-9
    lead.present = False
    out2 = [ac.get_max_accel(v, False, lead) for _ in range(60)]
    assert min(np.diff([out[-1]] + out2)) >= -0.5 * 0.05 - 1e-9   # eased out
    assert abs(out2[-1] - base) < 1e-9

  def test_no_boost_at_80_kph_or_for_a_closing_lead(self):
    ac, NS = self._ac(AccelProfile.eco)
    v = 80 / 3.6
    lead = NS(present=True, modelProb=0.9, dRel=30.0, vLead=v + 3.0)
    base = float(np.interp(v, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.eco]))
    assert abs([ac.get_max_accel(v, False, lead) for _ in range(40)][-1] - base) < 1e-9
    ac, NS = self._ac(AccelProfile.eco)
    v = 15.0
    lead = NS(present=True, modelProb=0.9, dRel=30.0, vLead=v - 1.0)
    base = float(np.interp(v, MAX_ACCEL_BREAKPOINTS, MAX_ACCEL_PROFILES[AccelProfile.eco]))
    assert abs([ac.get_max_accel(v, False, lead) for _ in range(40)][-1] - base) < 1e-9


class _Lead:
  def __init__(self, present=True, modelProb=0.9, dRel=30.0, vLead=18.0):
    self.present, self.modelProb, self.dRel, self.vLead = present, modelProb, dRel, vLead


class _Radar:
  def __init__(self, lead):
    self.leadOne = lead


class _Sink:
  def clear(self):
    pass

  def update(self, *args, **kwargs):
    pass


class TestPlannerLeadWiring(OpenpilotTestCase):
  """The boost needs a lead, so the planner has to carry radarState.leadOne into get_max_accel_override."""

  def setUp(self):
    self.params = Params()
    self.params.put_bool("AccelPersonalityEnabled", True, block=True)
    self.params.put("AccelPersonality", AccelProfile.eco, block=True)

  @staticmethod
  def _planner():
    from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP

    planner = LongitudinalPlannerSP.__new__(LongitudinalPlannerSP)
    planner.accel_controller = AccelController()
    planner.accel_controller_active = False
    planner.lead_one = None
    return planner

  @staticmethod
  def _settle(planner, v_ego, lead=None, n=60):
    return [planner.get_max_accel_override(v_ego, lead=lead) for _ in range(n)][-1]

  def test_update_stores_the_radar_lead(self):
    planner = self._planner()
    planner.events_sp = _Sink()
    planner.e2e_alerts_helper = _Sink()
    lead = _Lead()
    planner.update({"radarState": _Radar(lead)})
    assert planner.lead_one is lead

  def test_stored_lead_feeds_the_boost_and_an_explicit_lead_wins(self):
    v = 15.0
    lead = _Lead(vLead=v + 3.0)
    planner = self._planner()
    planner.lead_one = lead
    boosted = self._settle(planner, v)

    planner.accel_controller._boost = 0.0
    planner.lead_one = _Lead(present=False)
    base = self._settle(planner, v)
    assert boosted > base + 0.2

    planner.accel_controller._boost = 0.0
    explicit = self._settle(planner, v, lead=lead)
    assert abs(explicit - boosted) < 1e-9

  def test_disabled_accel_controller_returns_no_override(self):
    self.params.put_bool("AccelPersonalityEnabled", False, block=True)
    assert self._planner().get_max_accel_override(15.0, lead=_Lead()) is None
