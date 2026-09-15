from types import SimpleNamespace

import numpy as np
import pytest

from opendbc.car.common.conversions import Conversions as CV
from opendbc.car.ford.values import CAR, FordFlags
from openpilot.sunnypilot.livedelay.helpers import get_ford_delay_offset, get_lat_delay


@pytest.mark.parametrize('mph,expected', [(-1, .4), (0, .4), (10, .4), (15, .4), (20, .4*2/3),
                                          (22.5, .2), (25, .4/3), (30, 0), (45, 0), (100, 0)])
def test_preview_schedule(mph, expected):
  cp = SimpleNamespace(brand='ford', flags=FordFlags.CANFD)
  assert get_ford_delay_offset(cp, True, mph*CV.MPH_TO_MS) == pytest.approx(expected)


@pytest.mark.parametrize('enabled', [False, True])
@pytest.mark.parametrize('brand,flags', [('ford', 0), ('ford', 8), ('ford', FordFlags.CANFD),
                                       ('ford', FordFlags.CANFD | 8), ('toyota', FordFlags.CANFD)])
def test_only_enabled_ford_canfd_has_preview(enabled, brand, flags):
  cp = SimpleNamespace(brand=brand, flags=flags)
  expected = .4 if enabled and brand == 'ford' and flags & FordFlags.CANFD else 0.
  assert get_ford_delay_offset(cp, enabled, 0.) == expected


@pytest.mark.parametrize('vehicle', list(CAR))
def test_all_ford_platforms_follow_canfd_gate(vehicle):
  cp = SimpleNamespace(brand='ford', flags=vehicle.config.flags)
  assert get_ford_delay_offset(cp, True, 5.) == (.4 if vehicle.config.flags & FordFlags.CANFD else 0.)


@pytest.mark.parametrize('v_ego', [float('nan'), float('inf'), -float('inf')])
def test_invalid_speed_does_not_add_preview(v_ego):
  assert get_ford_delay_offset(SimpleNamespace(brand='ford', flags=FordFlags.CANFD), True, v_ego) == 0.


def test_preview_is_continuous_and_recomputed_from_current_speed():
  cp = SimpleNamespace(brand='ford', flags=FordFlags.CANFD)
  mph = np.linspace(0, 60, 12001)
  delays = np.array([get_ford_delay_offset(cp, True, v*CV.MPH_TO_MS) for v in mph])
  assert np.all((0 <= delays) & (delays <= .4))
  assert np.all(np.diff(delays) <= 0)
  assert np.max(np.abs(np.diff(delays))) <= .4/15*.005 + 1e-14
  assert [get_ford_delay_offset(cp, True, v*CV.MPH_TO_MS) for v in [10, 40, 10]] == [.4, 0., .4]


@pytest.mark.parametrize('learning,expected', [(True, .16894637), (False, .32)])
def test_preview_does_not_replace_or_write_the_base_delay(learning, expected):
  params = SimpleNamespace(get_bool=lambda key: learning, get=lambda key, **kwargs: .32)
  cp = SimpleNamespace(brand='ford', flags=FordFlags.CANFD)
  base = get_lat_delay(params, .16894637)
  assert base == expected
  assert base + get_ford_delay_offset(cp, True, 0.) == pytest.approx(expected+.4)
  assert get_lat_delay(params, .16894637) == expected
