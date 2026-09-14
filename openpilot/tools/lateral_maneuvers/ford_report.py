"""Report raw Ford channel pulses without treating them as curvature targets."""
import base64
import io
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from opendbc.can import CANParser
from opendbc.car.ford.fordcan import CanBus, calculate_lat_ctl2_checksum
from openpilot.common.constants import CV
from openpilot.selfdrive.controls.lib.ford_channel_test import is_channel_plan

SERVICES = {'lateralManeuverPlan', 'carControl', 'carState', 'carStateSP', 'sendcan'}


@dataclass
class Run:
  run_id: int
  channel: str
  speed: float
  messages: list = field(default_factory=list)
  outcome: str = 'incomplete'


class ChannelRuns:
  def __init__(self):
    self.runs = []
    self.current = None

  def add(self, msg):
    kind = msg.which()
    if kind == 'lateralManeuverPlan' and is_channel_plan(msg.lateralManeuverPlan):
      test = msg.lateralManeuverPlan.fordChannelTest
      active = msg.valid and str(test.phase) in ('baseline', 'pulse', 'release')
      if active and (self.current is None or self.current.run_id != test.runId):
        self.current = Run(test.runId, str(test.channel), test.speed)
        self.runs.append(self.current)
      if not active and self.current is not None:
        self.current.outcome = str(test.phase)
        self.current.messages.append(msg)
        self.current = None
    if self.current is not None and kind in SERVICES:
      self.current.messages.append(msg)


def first_sustained(t, mask, duration=.05):
  start = None
  previous = None
  for stamp, passed in zip(t, mask, strict=True):
    if not passed or (previous is not None and stamp-previous > .05):
      start = None
    if passed:
      if start is None:
        start = stamp
      if stamp-start >= duration:
        return float(start)
    previous = stamp
  return None


def analyze(run, CP):
  parser = CANParser('ford_lincoln_base_pt', [('LateralMotionControl2', 100)], CanBus(CP).main)
  address = parser.dbc.name_to_msg['LateralMotionControl2'].address
  plans, wheels, commands = [], [], []
  problems = set()
  if run.outcome != 'complete':
    problems.add(run.outcome)
  for msg in sorted(run.messages, key=lambda m: m.logMonoTime):
    t, kind = msg.logMonoTime*1e-9, msg.which()
    if kind != 'lateralManeuverPlan' and not msg.valid:
      problems.add(f'invalid {kind}')
    if kind == 'lateralManeuverPlan':
      p = msg.lateralManeuverPlan.fordChannelTest
      plans.append((t, str(p.phase), p.delta))
    elif kind == 'carState':
      cs = msg.carState
      wheels.append((t, cs.steeringAngleDeg, cs.vEgo*CV.MS_TO_MPH))
      if cs.steeringPressed or abs(cs.steeringTorque) > 1. or cs.gasPressed or cs.brakePressed:
        problems.add('driver input')
      if not cs.canValid or cs.steerFaultTemporary or cs.steerFaultPermanent or not cs.cruiseState.enabled:
        problems.add('vehicle fault')
      if abs(cs.vEgo-run.speed) > .7:
        problems.add('speed out of range')
    elif kind == 'carControl' and not msg.carControl.latActive:
      problems.add('lateral inactive')
    elif kind == 'carStateSP':
      p = msg.carStateSP.fordPscmStatus
      if not p.valid or not -.005 <= t-p.canMonoTime*1e-9 <= .15 or p.denied or p.limit in (2, 3) or p.lateralState != 2:
        problems.add('PSCM invalid, denied or limited')
    elif kind == 'sendcan':
      for packet in msg.sendcan:
        if packet.address == address and packet.src == CanBus(CP).main:
          parser.update([msg.logMonoTime, [(packet.address, packet.dat, packet.src)]])
          wire = parser.vl['LateralMotionControl2']
          commands.append((t, -wire['LatCtlPathOffst_L_Actl'], -wire['LatCtlPath_An_Actl']))
          if wire['LatCtl_D2_Rq'] != 2 or wire['LatCtlCurv_No_Actl'] != 0. or wire['LatCtlCrv_NoRate2_Actl'] != 0.:
            problems.add('unexpected CAN mode or C2/C3')
          if wire['LatCtlPath_No_Cs'] != calculate_lat_ctl2_checksum(int(wire['LatCtl_D2_Rq']), int(wire['LatCtlPath_No_Cnt']), packet.dat):
            problems.add('CAN checksum')
  seen = {m.which() for m in run.messages}
  if missing := SERVICES-seen:
    problems.add('missing '+', '.join(sorted(missing)))
  pulse = next((t for t, phase, _ in plans if phase == 'pulse'), None)
  release = next((t for t, phase, _ in plans if phase == 'release'), None)
  if not plans or plans[0][1] != 'baseline' or pulse is None or release is None:
    problems.add('missing test phases')
  data = {'problems': problems, 'plans': plans, 'wheels': np.array(wheels), 'commands': np.array(commands), 'pulse': pulse, 'release': release,
              'onset': None, 'peak': None, 'residual': None, 'wire_on': None, 'wire_off': None, 'threshold': None, 'delta': None}
  if len(wheels) < 10 or len(commands) < 10:
    problems.add('insufficient wheel or CAN samples')
  if pulse is None or release is None or len(wheels) < 10 or len(commands) < 10:
    return data
  w, c = data['wheels'], data['commands']
  if not np.isfinite(w).all() or not np.isfinite(c).all():
    problems.add('nonfinite data')
    return data
  for name, samples in (('wheel', w), ('CAN', c)):
    if np.max(np.diff(samples[:, 0])) > .1:
      problems.add(f'{name} data gap')
  bw, bc = w[(w[:, 0] >= pulse-.2) & (w[:, 0] < pulse)], c[(c[:, 0] >= pulse-.2) & (c[:, 0] < pulse)]
  if len(bw) < 3 or len(bc) < 3:
    problems.add('insufficient baseline')
    return data
  base_angle, base_command = np.median(bw[:, 1]), np.median(bc[:, 1:], axis=0)
  selected = 1 if run.channel == 'c0' else 2
  other = 2 if selected == 1 else 1
  held = c[c[:, 0] >= plans[0][0]+.06]  # allow the initial plan to reach controlsd and the sender
  if not len(held) or np.max(np.abs(held[:, other]-base_command[other-1])) > (1e-5 if other == 2 else 1e-4):
    problems.add('other field changed')
  delta = next(d for _, p, d in plans if p == 'pulse')
  tolerance = .00026 if selected == 2 else .0051
  pulse_samples = c[(c[:, 0] >= pulse) & (c[:, 0] < release)]
  matching = pulse_samples[np.abs(pulse_samples[:, selected]-base_command[selected-1]-delta) < tolerance]
  if not len(matching):
    problems.add('pulse absent from CAN')
    return data
  on = matching[0, 0]
  release_samples = c[c[:, 0] >= release]
  returned = release_samples[np.abs(release_samples[:, selected]-base_command[selected-1]) < tolerance]
  off = returned[0, 0] if len(returned) else None
  if off is None:
    problems.add('release absent from CAN')
  # Ignore the one-cycle boundary uncertainty; verify the rest of each phase.
  for start, end, expected in ((pulse+.06, release, base_command[selected-1]+delta),
                                (release+.06, c[-1, 0]+.001, base_command[selected-1])):
    samples = c[(c[:, 0] >= start) & (c[:, 0] < end)]
    if not len(samples) or np.max(np.abs(samples[:, selected]-expected)) > tolerance:
      problems.add('selected field not held')
  response = w[w[:, 0] >= on]
  change = response[:, 1]-base_angle
  threshold = max(.5, 3.*float(np.ptp(bw[:, 1])))
  onset = first_sustained(response[:, 0], np.abs(change) >= threshold)
  tail = response[response[:, 0] >= response[-1, 0]-.2]
  data.update(onset=None if onset is None else onset-on, peak=float(np.max(np.abs(change))),
              residual=float(np.mean(tail[:, 1])-base_angle), wire_on=on, wire_off=off, threshold=threshold, delta=delta,
              base_angle=base_angle)
  return data


def report(platform, route, CP, ID, runs, output_dir=None):
  output_dir = Path(output_dir) if output_dir else Path(__file__).parent/'lateral_reports'
  output_dir.mkdir(parents=True, exist_ok=True)
  output = output_dir/f'{platform}_{route.replace("/", "_").replace("|", "_")}_ford_channels.html'
  html = ['<!doctype html><meta charset="utf-8"><title>Ford C0 / C1 test</title>',
          '<style>body{font:17px system-ui;max-width:1050px;margin:40px auto;padding:0 24px;color:#18232e}img{width:100%}.bad{color:#a21c24}</style>',
          '<h1>Ford C0 / C1 test</h1>', f'<p>{escape(platform)} · {escape(route)}<br>Commit {escape(ID.gitCommit)}</p>',
          '<p>Each pulse holds the other field constant. All plots use left-positive coordinates. '
          + 'C0 and C1 pulse sizes are not assumed to produce equal steering. These measurements describe these trials; '
          + 'they do not establish a universal PSCM delay or predict intersection turns.</p>',
          '<p>Onset means wheel movement from baseline exceeding max(0.5°, 3 × baseline range) for 50 ms, '
          + 'timed from the first changed CAN command. Peak covers the pulse and release. Residual is the last 200 ms '
          + 'of wheel angle minus baseline. A larger response can cross the onset threshold earlier without having less delay.</p>']
  for index, run in enumerate(runs, 1):
    d = analyze(run, CP)
    direction = ('left' if d['delta'] > 0 else 'right') if d['delta'] is not None else 'unknown direction'
    title = f'{index}. {run.channel.upper()} {direction} · {run.speed*CV.MS_TO_MPH:.0f} mph'
    html.append(f'<h2>{escape(title)}</h2>')
    if d['problems']:
      html.append(f'<p class="bad">Exclude from comparison: {escape(", ".join(sorted(d["problems"])))}</p>')
    else:
      html.append('<p>Complete; command isolation and logged validity checks passed.</p>')
    if d['peak'] is not None:
      onset = f'{d["onset"]:.3f} s' if d['onset'] is not None else 'not detected'
      html.append(f'<p>Onset: <b>{onset}</b> (threshold {d["threshold"]:.2f}°) · '
                  + f'Peak movement: <b>{d["peak"]:.2f}°</b> · End residual: <b>{d["residual"]:+.2f}°</b></p>')
    if not len(d['wheels']) or not len(d['commands']):
      html.append('<p>Insufficient wheel or CAN data to plot.</p>')
      continue
    origin = d['wire_on'] if d['wire_on'] is not None else d['commands'][0, 0]
    fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True, layout='constrained')
    c, w = d['commands'], d['wheels']
    axes[0].step(c[:, 0]-origin, c[:, 1], where='post', label='C0 sent', color='#007ea7')
    axes[1].step(c[:, 0]-origin, c[:, 2], where='post', label='C1 sent', color='#ba5d07')
    axes[2].plot(w[:, 0]-origin, w[:, 1]-d.get('base_angle', w[0, 1]), label='Wheel movement', color='#7d3fa2')
    axes[3].plot(w[:, 0]-origin, w[:, 2], label='Speed', color='#007453')
    for ax, label in zip(axes, ('C0 (m)', 'C1 (rad)', 'Wheel Δ (°)', 'Speed (mph)'), strict=True):
      ax.set_ylabel(label)
      ax.grid(alpha=.2)
      ax.legend(loc='upper right')
      if d['wire_on'] is not None:
        ax.axvline(0., color='#444', linestyle='--')
      if d['wire_off'] is not None:
        ax.axvline(d['wire_off']-origin, color='#444', linestyle=':')
    axes[-1].set_xlabel('Seconds from CAN pulse start · dotted line = CAN return to baseline')
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120)
    plt.close(fig)
    html.append(f'<img alt="{escape(title)} command and wheel response" src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">')
  output.write_text(''.join(html))
  return output
