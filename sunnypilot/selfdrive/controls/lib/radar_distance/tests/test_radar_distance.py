"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

from types import SimpleNamespace

import pytest

from openpilot.sunnypilot.selfdrive.controls.lib.radar_distance.radar_distance import \
  RadarDistanceController, HOLD_MAX_FRAMES, FCW_PROB_CAP

COMFORT_BRAKE = 2.5


class FakeParams:
  def __init__(self, store=None):
    self.store = dict(store or {})

  def get_bool(self, key):
    return bool(self.store.get(key, False))


def lead(status=True, dRel=40.0, vRel=-2.0, vLead=18.0, aLeadK=0.0, aLeadTau=1.5, modelProb=0.95):
  return SimpleNamespace(status=status, dRel=dRel, yRel=0.0, vRel=vRel, vLead=vLead, vLeadK=vLead,
                         aLeadK=aLeadK, aLeadTau=aLeadTau, modelProb=modelProb)


def rs(one, two=None):
  return SimpleNamespace(leadOne=one, leadTwo=two or lead(status=False, dRel=0.0, modelProb=0.0))


def obstacle(ld):
  return ld.dRel + ld.vLead ** 2 / (2 * COMFORT_BRAKE)


def ctrl(enabled=True):
  return RadarDistanceController(CP=SimpleNamespace(), params=FakeParams({'RadarDistance': enabled}))


def test_disabled_is_identity():
  c = ctrl(enabled=False)
  r = rs(lead())
  assert c.smooth_radarstate(r) is r  # byte-stock passthrough


def test_valid_lead_passthrough():
  c = ctrl()
  one = lead(dRel=40.0)
  out = c.smooth_radarstate(rs(one))
  assert out.leadOne is one


def test_holds_after_sustained_dropout():
  c = ctrl()
  for _ in range(3):  # sustain (>= SUSTAIN_FRAMES)
    c.smooth_radarstate(rs(lead(dRel=30.0, vRel=-4.0, vLead=16.0)))
  out = c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0)))
  held = out.leadOne
  assert held.status is True
  assert held.dRel < 30.0          # dead-reckoned closer
  assert held.dRel == pytest.approx(30.0 - 4.0 * 0.05, abs=1e-6)


def test_obstacle_monotone_during_hold():
  c = ctrl()
  for _ in range(3):
    c.smooth_radarstate(rs(lead(dRel=30.0, vRel=-4.0, vLead=16.0)))
  last_obs = obstacle(lead(dRel=30.0, vLead=16.0))
  prev = last_obs
  for _ in range(HOLD_MAX_FRAMES):
    held = c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0))).leadOne
    if not held.status:
      break
    o = obstacle(held)
    assert o <= last_obs + 1e-6     # never farther than the last real obstacle (brakes >= last real)
    assert o <= prev + 1e-6         # monotonically non-increasing -> brakes more over the hold
    prev = o


def test_releases_after_hold_cap():
  c = ctrl()
  for _ in range(3):
    c.smooth_radarstate(rs(lead(dRel=30.0)))
  statuses = [c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0))).leadOne.status
              for _ in range(HOLD_MAX_FRAMES + 3)]
  assert all(statuses[:HOLD_MAX_FRAMES])        # held through the cap
  assert statuses[HOLD_MAX_FRAMES] is False     # released after


def test_no_hold_without_sustained_lead():
  c = ctrl()
  c.smooth_radarstate(rs(lead(dRel=30.0)))       # single valid frame (< SUSTAIN_FRAMES)
  out = c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0)))
  assert out.leadOne.status is False             # not armed -> no hold


def test_flicker_does_not_reset_wall_clock():
  c = ctrl()
  for _ in range(3):
    c.smooth_radarstate(rs(lead(dRel=30.0)))
  # 1/0/1/0 flicker: lone valid frames must NOT reset the wall-clock (sustained < SUSTAIN_FRAMES)
  for _ in range(4):
    c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0)))  # dropout
    c.smooth_radarstate(rs(lead(dRel=31.0)))                              # lone valid
  assert c._one._since_real > 0                  # wall-clock kept climbing through the flicker


def test_fcw_prob_capped_and_aleadk_not_positive():
  c = ctrl()
  for _ in range(3):
    c.smooth_radarstate(rs(lead(dRel=30.0, aLeadK=1.0, modelProb=0.99)))
  held = c.smooth_radarstate(rs(lead(status=False, dRel=0.0, modelProb=0.0))).leadOne
  assert held.modelProb <= FCW_PROB_CAP          # no false FCW from a held phantom
  assert held.aLeadK <= 0.0                       # never project the held lead as accelerating
