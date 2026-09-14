"""Synthetic log tests validate report math, not the truck's physical response."""
from types import SimpleNamespace

import pytest

from opendbc.can import CANPacker
from opendbc.car import structs
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import messaging
from openpilot.selfdrive.controls.lib.ford_channel_test import AMPLITUDE, SPEEDS
from openpilot.tools.lateral_maneuvers.ford_report import ChannelRuns, analyze, first_sustained, report


def event(kind, t):
  m = messaging.new_message(kind, size=1 if kind == 'sendcan' else None)
  m.logMonoTime, m.valid = round(t*1e9), True
  return m


def fixture(channel='c0', direction=1, other_changes=False, response=True, abort=False):
  collector = ChannelRuns()
  packer = CANPacker('ford_lincoln_base_pt')
  cp = structs.CarParams(safetyConfigs=[structs.CarParams.SafetyConfig()])
  bus = CanBus(cp)
  for i in range(301):
    t = 10.+i*.01
    if i % 5 == 0:
      p = event('lateralManeuverPlan', t)
      phase = 'baseline' if i < 50 else ('pulse' if i < 100 else 'release')
      if i == 300:
        phase, p.valid = ('aborted' if abort else 'complete'), False
      p.lateralManeuverPlan.fordChannelTest = {'runId': 1, 'channel': channel, 'phase': phase,
                                              'delta': direction*AMPLITUDE[channel] if phase == 'pulse' else 0., 'speed': SPEEDS[0]}
      collector.add(p)
    delta = direction*AMPLITUDE[channel] if 50 <= i < 100 else 0.
    c0, c1 = (.01+delta, .002) if channel == 'c0' else (.01, .002+delta)
    if other_changes and 70 <= i < 90:
      if channel == 'c0':
        c1 += .001
      else:
        c0 += .01
    address, data, src = create_lat_ctl2_msg(packer, bus, 2, -c0, -c1, 0., 0., i % 16)
    m = event('sendcan', t)
    m.sendcan[0].address, m.sendcan[0].dat, m.sendcan[0].src = address, data, src
    collector.add(m)
    m = event('carState', t)
    m.carState.canValid, m.carState.vEgo = True, SPEEDS[0]
    m.carState.cruiseState.enabled = True
    m.carState.steeringAngleDeg = (direction*2. if response and 70 <= i < 150 else 0.)
    collector.add(m)
    m = event('carControl', t)
    m.carControl.latActive = True
    collector.add(m)
    m = event('carStateSP', t)
    m.carStateSP.fordPscmStatus = {'valid': True, 'canMonoTime': round(t*1e9), 'lateralState': 2}
    collector.add(m)
  assert len(collector.runs) == 1
  return cp, collector.runs[0]


@pytest.mark.parametrize('channel', ['c0', 'c1'])
@pytest.mark.parametrize('direction', [-1, 1])
def test_command_aligned_metrics(channel, direction):
  cp, run = fixture(channel, direction)
  d = analyze(run, cp)
  assert not d['problems']
  assert d['onset'] == pytest.approx(.2)
  assert d['wire_on'] == pytest.approx(10.5)
  assert d['wire_off'] == pytest.approx(11.)
  assert d['peak'] == pytest.approx(2.)
  assert d['residual'] == pytest.approx(0.)
  assert d['delta'] == pytest.approx(direction*AMPLITUDE[channel])


@pytest.mark.parametrize('channel', ['c0', 'c1'])
def test_contaminated_field_excluded(channel):
  cp, run = fixture(channel, other_changes=True)
  assert 'other field changed' in analyze(run, cp)['problems']


def test_no_movement_is_not_reported_as_zero_delay():
  cp, run = fixture(response=False)
  d = analyze(run, cp)
  assert d['onset'] is None and d['peak'] == 0.
  assert not d['problems']


def test_abort_remains_visible_in_report(tmp_path):
  cp, run = fixture(abort=True)
  assert 'aborted' in analyze(run, cp)['problems']
  output = report('FORD', 'device/route', cp, SimpleNamespace(gitCommit='synthetic'), [run], tmp_path)
  html = output.read_text()
  assert 'Exclude from comparison: aborted' in html
  assert 'data:image/png;base64,' in html


def test_incomplete_missing_and_bad_checksum():
  cp, run = fixture()
  run.outcome = 'incomplete'
  run.messages = [m for m in run.messages if m.which() != 'carStateSP']
  m = next(m for m in run.messages if m.which() == 'sendcan')
  data = bytearray(m.sendcan[0].dat)
  data[1] ^= 1
  m.sendcan[0].dat = bytes(data)
  problems = analyze(run, cp)['problems']
  assert {'incomplete', 'missing carStateSP', 'CAN checksum'} <= problems


def test_single_sample_and_gap_cannot_count_as_onset():
  assert first_sustained([0., .01, .02, .03], [False, True, False, False]) is None
  assert first_sustained([0., .5], [True, True]) is None
