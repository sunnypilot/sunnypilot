#!/usr/bin/env python3
"""Isolated, disengaged camera/modeld bench. Never starts controls or pandad."""
import argparse
import csv
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

from openpilot.cereal import messaging
from openpilot.common.basedir import BASEDIR
from openpilot.common.hardware import HARDWARE
from openpilot.common.params import Params
from openpilot.common.prefix import OpenpilotPrefix


def main():
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('--seconds', type=float, default=180)
  parser.add_argument('--output', type=Path, required=True)
  parser.add_argument('--small', action='store_true')
  parser.add_argument('--engaged-until', type=float, default=0.0,
                      help='fake an engaged selfdriveState for this many seconds, so the join has to wait for a window')
  parser.add_argument('--write-chunk', type=int, choices=[16384, 32768, 65536, 131072, 262144, 524288],
                      help='bench-only FunctionFS write quantum override, in bytes')
  args = parser.parse_args()
  if args.seconds <= 0:
    parser.error('--seconds must be positive')
  live = Params()
  if not live.get_bool('IsOffroad'):
    raise SystemExit('bench requires the real device to remain offroad')
  # USB and cameras are physical resources, even with isolated messaging.
  for proc in Path('/proc').glob('[0-9]*/cmdline'):
    try:
      argv = proc.read_bytes().split(b'\0')
    except (OSError, ProcessLookupError):
      continue
    if argv and (Path(os.fsdecode(argv[0])).name == 'camerad' or
                 b'openpilot.selfdrive.modeld.modeld' in argv or
                 b'openpilot.sunnypilot.accelerators.jetlink.jetlinkd' in argv):
      raise SystemExit(f'physical resource already owned by {proc.parent.name}: {argv[:3]}')
  keys = ('CarParamsPersistent', 'CalibrationParams', 'JetlinkModel', 'JetlinkSpec', 'JetlinkEngineReady', 'JetlinkEndpoint')
  saved = {key: live.get(key) for key in keys}
  if saved['CarParamsPersistent'] is None:
    raise SystemExit('no saved CarParams; bench cannot choose a vehicle configuration')
  args.output.mkdir(parents=True, exist_ok=False)
  stop = False

  def stop_requested(*_):
    nonlocal stop
    stop = True

  signal.signal(signal.SIGTERM, stop_requested)
  signal.signal(signal.SIGINT, stop_requested)
  children, files, rows = [], [], []
  # Keep artifacts under the explicit output directory; no live Params writes.
  with OpenpilotPrefix() as prefix:
    params = Params()
    for key, value in saved.items():
      if value is not None:
        params.put(key, value, block=True)
    params.put('CarParams', saved['CarParamsPersistent'], block=True)
    params.put_bool('JetlinkEnabled', not args.small, block=True)
    pm = messaging.PubMaster(['selfdriveState', 'carState', 'carControl', 'deviceState', 'extrinsicsCalibration'])
    sm = messaging.SubMaster(['modelV2', 'modelDataV2SP'])
    calibration = None
    if saved['CalibrationParams'] is not None:
      calibration = messaging.log_from_bytes(saved['CalibrationParams'])
    print(f'isolated prefix={prefix.prefix} output={args.output}', flush=True)
    HARDWARE.set_power_save(False)
    try:
      model_command = [sys.executable, '-m', 'openpilot.selfdrive.modeld.modeld']
      if args.write_chunk is not None:
        model_command = [sys.executable, '-c',
                         'from jetlink.transport.ffs import FfsTransport; '
                         + f'FfsTransport.write_chunk={args.write_chunk}; '
                         + 'import runpy; runpy.run_module("openpilot.selfdrive.modeld.modeld", run_name="__main__")']
      for name, command in (
        ('camerad', [str(Path(BASEDIR) / 'openpilot/system/camerad/camerad')]),
        ('modeld', model_command)):
        log = (args.output / f'{name}.log').open('w')
        files.append(log)
        children.append(subprocess.Popen(command, cwd=BASEDIR, stdout=log, stderr=subprocess.STDOUT))
      start = last = time.monotonic()
      tick = 0
      with (args.output / 'frames.csv').open('w') as stream:
        writer = csv.writer(stream)
        writer.writerow(['elapsed_s', 'frame_id', 'big', 'valid', 'exec_ms', 'drop_pct', 'age_ms', 'accel_state', 'available'])
        while not stop and time.monotonic() - start < args.seconds:
          if any(child.poll() is not None for child in children):
            raise RuntimeError('camera/modeld exited; inspect captured logs')
          if tick % 100 == 0 and not live.get_bool('IsOffroad'):
            raise RuntimeError('real ignition changed: stopping bench')
          engaged = time.monotonic() - start < args.engaged_until
          for service in ('selfdriveState', 'carState', 'carControl'):
            message = messaging.new_message(service)
            message.valid = True
            if service == 'carState':
              message.carState.standstill = True
            elif service == 'selfdriveState':
              # The promotion gate reads these three; faking them engaged holds the join back.
              message.selfdriveState.enabled = engaged
            elif service == 'carControl':
              message.carControl.latActive = engaged
              message.carControl.longActive = engaged
            pm.send(service, message)
          if tick % 10 == 0:
            device = messaging.new_message('deviceState')
            device.valid = True
            device.deviceState.deviceType = HARDWARE.get_device_type()
            pm.send('deviceState', device)
            if calibration is not None:
              message = calibration.as_builder()
              message.logMonoTime = time.monotonic_ns()
              pm.send('extrinsicsCalibration', message)
          sm.update(0)
          if sm.updated['modelV2']:
            model = sm['modelV2']
            status = sm['modelDataV2SP']
            row = (time.monotonic() - start, model.frameId, int(model.big), int(sm.valid['modelV2']),
                   model.modelExecutionTime * 1000, model.frameDropPerc,
                   (sm.logMonoTime['modelV2'] - model.timestampEof) / 1e6,
                   str(status.acceleratorState), int(status.bigModelAvailable))
            rows.append(row)
            writer.writerow(row)
          if time.monotonic() - last >= 10:
            last = time.monotonic()
            stream.flush()
            print(f't={last-start:.0f}s frames={len(rows)} big={sum(r[2] for r in rows)} engaged={engaged}',
                  f'latest={rows[-1] if rows else None}', flush=True)
          tick += 1
          time.sleep(max(0, start + tick * 0.01 - time.monotonic()))
    finally:
      for child in reversed(children):
        if child.poll() is None:
          child.send_signal(signal.SIGINT)
      for child in children:
        try:
          child.wait(timeout=5)
        except subprocess.TimeoutExpired:
          child.kill()
          child.wait(timeout=5)
      for log in files:
        log.close()
      # Power saving belongs to hardwared if real ignition changed.
      if live.get_bool('IsOffroad'):
        HARDWARE.set_power_save(True)
  summary = {}
  for label, subset in [('all', rows), ('big', [r for r in rows if r[2]]), ('small', [r for r in rows if not r[2]])]:
    if subset:
      # the state column is text, so pick the numeric columns before numpy sees the rows
      values = np.asarray([row[:7] for row in subset], dtype=float)
      summary[label] = {'frames': len(subset), 'exec_p50_p99_p999_max_ms': np.percentile(values[:, 4], [50, 99, 99.9, 100]).tolist(),
                        'over_50ms': int((values[:, 4] > 50).sum()), 'max_drop_pct': float(values[:, 5].max()),
                        'lagging_frames': int((values[:, 5] > 1).sum()), 'invalid_frames': int((values[:, 3] == 0).sum()),
                        'states': sorted({row[7] for row in subset})}
  (args.output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
  print(json.dumps(summary, indent=2), flush=True)
  if not rows or (not args.small and not any(row[2] for row in rows)):
    raise SystemExit('bench did not exercise the requested model')


if __name__ == '__main__':
  main()
