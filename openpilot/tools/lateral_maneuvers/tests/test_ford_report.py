"""Synthetic log tests validate report math, not the truck's physical response."""
from types import SimpleNamespace

import pytest

from opendbc.can import CANPacker
from opendbc.car import structs
from opendbc.car.ford.fordcan import CanBus, create_lat_ctl2_msg
from openpilot.cereal import messaging
from openpilot.selfdrive.controls.lib.ford_channel_test import SPEEDS
from openpilot.tools.lateral_maneuvers.ford_report import ChannelRuns, analyze, first_sustained, report


# Archived raw-pulse routes remain readable after replacing the diagnostic.
AMPLITUDE = {'c0': 1.28, 'c1': .125}

def event(kind, t):
  m = messaging.new_message(kind, size=1 if kind == 'sendcan' else None)
  m.logMonoTime, m.valid = round(t*1e9), True
  return m


def fixture(channel='c0', direction=1, other_changes=False, response=True, abort=False, pulse_frames=100, amplitude=None):
  collector = ChannelRuns()
  packer = CANPacker('ford_lincoln_base_pt')
  cp = structs.CarParams(safetyConfigs=[structs.CarParams.SafetyConfig()])
  bus = CanBus(cp)
  amplitude = AMPLITUDE[channel] if amplitude is None else amplitude
  release_frame, complete_frame = 50+pulse_frames, 250+pulse_frames
  for i in range(complete_frame+1):
    t = 10.+i*.01
    if i % 5 == 0:
      p = event('lateralManeuverPlan', t)
      phase = 'baseline' if i < 50 else ('pulse' if i < release_frame else 'release')
      if i == complete_frame:
        phase, p.valid = ('aborted' if abort else 'complete'), False
      p.lateralManeuverPlan.fordChannelTest = {'runId': 1, 'channel': channel, 'phase': phase,
                                              'delta': direction*amplitude if phase == 'pulse' else 0., 'speed': SPEEDS[0]}
      collector.add(p)
    delta = direction*amplitude if 50 <= i < release_frame else 0.
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
    m.carState.steeringAngleDeg = (direction*2. if response and 70 <= i < release_frame+50 else 0.)
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
@pytest.mark.parametrize('legacy', [False, True])
def test_command_aligned_metrics(channel, direction, legacy):
  amplitude = {'c0': .03, 'c1': .01}[channel] if legacy else AMPLITUDE[channel]
  pulse_frames = 50 if legacy else 100
  cp, run = fixture(channel, direction, pulse_frames=pulse_frames, amplitude=amplitude)
  d = analyze(run, cp)
  assert not d['problems']
  assert d['onset'] == pytest.approx(.2)
  assert d['wire_on'] == pytest.approx(10.5)
  assert d['wire_off'] == pytest.approx(10.5+pulse_frames*.01)
  assert d['peak'] == pytest.approx(2.)
  assert d['residual'] == pytest.approx(0.)
  assert d['delta'] == pytest.approx(direction*amplitude)


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


@pytest.mark.parametrize('channel', ['c0', 'c1'])
def test_normal_channel_report_uses_real_targets_and_decoded_output(channel, tmp_path, monkeypatch):
  from pathlib import Path
  from openpilot.tools.lateral_maneuvers import generate_report as generator
  from openpilot.tools.lateral_maneuvers.ford_report import channel_commands

  cp = structs.CarParams(carFingerprint='FORD_SYNTHETIC_REPORT_TEST', steerControlType=structs.CarParams.SteerControlType.curvature,
                        safetyConfigs=[structs.CarParams.SafetyConfig()])
  packer, bus = CANPacker('ford_lincoln_base_pt'), CanBus(cp)
  messages = []
  speed = SPEEDS[0]
  for i in range(250):
    t = 10.+i*.01
    curvature = (.5 if i < 105 else -.5)/speed**2
    if i % 5 == 0:
      m = event('lateralManeuverPlan', t)
      m.lateralManeuverPlan.desiredCurvature = curvature
      m.lateralManeuverPlan.fordChannelTest = {'runId': 1, 'channel': channel, 'phase': 'maneuver', 'speed': speed}
      messages.append(m)
    m = event('carState', t)
    m.carState.vEgo, m.carState.steeringAngleDeg = speed, 16. if i < 110 else -16.
    messages.append(m)
    m = event('controlsState', t)
    m.controlsState.curvature = curvature*.8 if i > 10 else 0.
    m.controlsState.desiredCurvature = curvature
    messages.append(m)
    m = event('carControl', t)
    m.carControl.latActive = True
    m.carControl.orientationNED = [0., 0., 0.]
    messages.append(m)
    messages.append(event('carOutput', t))
    c0, c1 = (24.5*curvature, 0.) if channel == 'c0' else (0., speed*curvature)
    address, data, src = create_lat_ctl2_msg(packer, bus, 2, -c0, -c1, 0., 0., i % 16)
    m = event('sendcan', t)
    m.sendcan[0].address, m.sendcan[0].dat, m.sendcan[0].src = address, data, src
    messages.append(m)
  m = event('alertDebug', 12.5)
  m.alertDebug.alertText1 = 'Complete'
  messages.append(m)
  commands, problems = channel_commands(messages, cp, channel, 10_000_000_000)
  assert not problems
  legacy_collector = ChannelRuns()
  for msg in messages:
    legacy_collector.add(msg)
  assert not legacy_collector.runs  # CLI dispatches these targets to the normal report
  assert (commands[:, 2 if channel == 'c0' else 1] == 0.).all()
  captured = []
  savefig = generator.plt.Figure.savefig

  def capture_figure(fig, *args, **kwargs):
    captured.append([axis.get_ylabel() for axis in fig.axes])
    # Render the real figure at preview resolution to keep this check fast.
    savefig(fig, *args, **(kwargs | {'dpi': 40}))

  monkeypatch.setattr(generator.plt.Figure, 'savefig', capture_figure)
  opened = []
  monkeypatch.setattr(generator.webbrowser, 'open_new_tab', opened.append)
  monkeypatch.setattr(generator, '__file__', str(tmp_path/'generate_report.py'))
  generator.report('FORD_SYNTHETIC_REPORT_TEST', f'synthetic-{channel}', None, cp,
                   SimpleNamespace(gitCommit='synthetic only', gitBranch='test', gitRemote='local'),
                   [(f'step right 15mph {channel.upper()}', [messages])])
  output = Path(opened[0])
  html = output.read_text()
  output.rename(tmp_path/output.name)
  assert f'Normal maneuver target through {channel.upper()} only' in html
  assert 'invalid maneuver!' not in html
  assert captured == [['Lateral Accel (m/s^2)', 'Wheel angle (deg)', 'Velocity (mph)', 'Jerk (m/s^3)', 'Roll (deg)', 'C0 sent (m)', 'C1 sent (rad)']]
  assert 'data:image/webp;base64,' in html
  # A live nonzero unused field must invalidate the isolated-channel measurement.
  assert 'channel isolation failed' in channel_commands(messages, cp, 'c1' if channel == 'c0' else 'c0', 10_000_000_000)[1]
