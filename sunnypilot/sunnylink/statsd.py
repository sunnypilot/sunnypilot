#!/usr/bin/env python3
import base64
import json
import os
import threading
import traceback

import zmq
import time
import uuid
from pathlib import Path
from collections import defaultdict
from datetime import datetime, UTC

from openpilot.common.params import Params
from cereal.messaging import SubMaster
from openpilot.system.hardware.hw import Paths
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware import HARDWARE
from openpilot.common.file_helpers import atomic_write_in_dir
from openpilot.system.version import get_build_metadata
from openpilot.system.loggerd.config import STATS_DIR_FILE_LIMIT, STATS_SOCKET, STATS_FLUSH_TIME_S
from openpilot.system.statsd import METRIC_TYPE, StatLogSP
from openpilot.common.realtime import Ratekeeper

STATSLOGSP = StatLogSP(intercept=False)

def sp_stats(end_event):
  """Collect sunnypilot-specific statistics and send as raw metrics."""
  rk = Ratekeeper(.1, print_delay_threshold=None)
  statlogsp = STATSLOGSP
  params = Params()

  def flatten_dict(d, parent_key='', sep='.'):
    items = {}
    if isinstance(d, dict):
      for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        items.update(flatten_dict(v, new_key, sep=sep))
    elif isinstance(d, (list, tuple)):
      for i, v in enumerate(d):
        new_key = f"{parent_key}[{i}]"
        items.update(flatten_dict(v, new_key, sep=sep))
    else:
      items[parent_key] = d
    return items

  # Collect sunnypilot parameters
  stats_dict = {}

  param_keys = [
    'SunnylinkEnabled',
    'AutoLaneChangeBsmDelay',
    'AutoLaneChangeTimer',
    'CarPlatformBundle',
    'CurrentRoute',
    'DevUIInfo',
    'EnableCopyparty',
    'IntelligentCruiseButtonManagement',
    'QuietMode',
    'RainbowMode',
    'ShowAdvancedControls',
    'Mads',
    'MadsMainCruiseAllowed',
    'MadsSteeringMode',
    'MadsUnifiedEngagementMode',
    'ModelManager_ActiveBundle',
    'ModelManager_Favs',
    'EnableSunnylinkUploader',
    'SunnylinkEnabled',
    'InstallDate',
    'UptimeOffroad',
    'UptimeOnroad',
  ]

  while not end_event.is_set():
    try:
      for key in param_keys:

        try:
          value = params.get(key)
        except Exception as e:
          stats_dict[key] = e
          continue

        if value is None:
          continue

        if isinstance(value, (dict, list, tuple)):
          stats_dict.update(flatten_dict(value, key))
        else:
          stats_dict[key] = value

      if stats_dict:
        statlogsp.raw('sunnypilot.device_params', stats_dict)
    except Exception as e:
      cloudlog.error(f"Exception {e}")
    finally:
      rk.keep_time()


def stats_main(end_event):
  comma_dongle_id = Params().get("DongleId")
  sunnylink_dongle_id = Params().get("SunnylinkDongleId")

  def get_influxdb_line(measurement: str, value: float | dict[str, float], timestamp: datetime, tags: dict) -> str:
    res = f"{measurement}"
    for k, v in tags.items():
      res += f",{k}={str(v)}"
    res += " "

    if isinstance(value, float):
      value = {'value': value}

    for k, v in value.items():
      res += f"{k}={str(v)},"

    res += f"sunnylink_dongle_id=\"{sunnylink_dongle_id}\",comma_dongle_id=\"{comma_dongle_id}\" {int(timestamp.timestamp() * 1e9)}\n"
    return res

  def get_influxdb_line_raw(measurement: str, value: dict, timestamp: datetime, tags: dict) -> str:
    res = f"{measurement}"
    try:
      custom_tags = ""
      for k, v in tags.items():
        custom_tags += f",{k}={str(v)}"
      res += custom_tags

      fields = ""
      for k, v in value.items():
        # Skip complex types - only keep simple scalar values
        if isinstance(v, (dict, list, bytes, bytearray)):
          continue

        fields += f"{k}={json.dumps(v)},"

      res += f" {fields}"
    except Exception as e:
      cloudlog.error(f"Unable to get influxdb line for: {value}")
      res += f",invalid=1 reason={e},"

    res += f"sunnylink_dongle_id=\"{sunnylink_dongle_id}\",comma_dongle_id=\"{comma_dongle_id}\" {int(timestamp.timestamp() * 1e9)}\n"
    return res

  # open statistics socket
  ctx = zmq.Context.instance()
  sock = ctx.socket(zmq.PULL)
  sock.bind(f"{STATS_SOCKET}_sp")

  STATS_DIR = Paths.stats_sp_root()

  # initialize stats directory
  Path(STATS_DIR).mkdir(parents=True, exist_ok=True)

  build_metadata = get_build_metadata()

  # initialize tags
  tags = {
    'started': False,
    'version': build_metadata.openpilot.version,
    'branch': build_metadata.channel,
    'dirty': build_metadata.openpilot.is_dirty,
    'origin': build_metadata.openpilot.git_normalized_origin,
    'deviceType': HARDWARE.get_device_type(),
  }

  # subscribe to deviceState for started state
  sm = SubMaster(['deviceState'])

  idx = 0
  boot_uid = str(uuid.uuid4())[:8]
  last_flush_time = time.monotonic()
  gauges = {}
  samples: dict[str, list[float]] = defaultdict(list)
  raws: dict = defaultdict()
  try:
    while not end_event.is_set():
      started_prev = sm['deviceState'].started
      sm.update()

      # Update metrics
      while True:
        try:
          metric = sock.recv_string(zmq.NOBLOCK)
          try:
            metric_type = metric.split('|')[1]
            metric_name = metric.split(':')[0]
            metric_value_raw = metric.split('|')[0].split(':')[1]

            if metric_type == METRIC_TYPE.GAUGE:
              metric_value = float(metric_value_raw)
              gauges[metric_name] = metric_value
            elif metric_type == METRIC_TYPE.SAMPLE:
              metric_value = float(metric_value_raw)
              samples[metric_name].append(metric_value)
            elif metric_type == METRIC_TYPE.RAW:
              raws[metric_name] = metric_value_raw
            else:
              cloudlog.event("unknown metric type", metric_type=metric_type)
          except Exception:
            print(traceback.format_exc())
            cloudlog.event("malformed metric", metric=metric)
        except zmq.error.Again:
          break

      # flush when started state changes or after FLUSH_TIME_S
      if (time.monotonic() > last_flush_time + STATS_FLUSH_TIME_S) or (sm['deviceState'].started != started_prev):
        result = ""
        current_time = datetime.now(UTC)
        tags['started'] = sm['deviceState'].started

        for key, value in raws.items():
          decoded_value = json.loads(base64.b64decode(value).decode('utf-8'))
          result += get_influxdb_line_raw(key, decoded_value, current_time, tags)

        for key, value in gauges.items():
          result += get_influxdb_line(f"gauge.{key}", value, current_time, tags)

        for key, values in samples.items():
          values.sort()
          sample_count = len(values)
          sample_sum = sum(values)

          stats = {
            'count': sample_count,
            'min': values[0],
            'max': values[-1],
            'mean': sample_sum / sample_count,
          }
          for percentile in [0.05, 0.5, 0.95]:
            value = values[int(round(percentile * (sample_count - 1)))]
            stats[f"p{int(percentile * 100)}"] = value

          result += get_influxdb_line(f"sample.{key}", stats, current_time, tags)

        # clear intermediate data
        gauges.clear()
        samples.clear()
        last_flush_time = time.monotonic()

        # check that we aren't filling up the drive
        if len(os.listdir(STATS_DIR)) < STATS_DIR_FILE_LIMIT:
          if len(result) > 0:
            stats_path = os.path.join(STATS_DIR, f"{boot_uid}_{idx}")
            with atomic_write_in_dir(stats_path) as f:
              f.write(result)
            idx += 1
        else:
          cloudlog.error("stats dir full")
  finally:
    sock.close()
    ctx.term()


def main():
  rk = Ratekeeper(1, print_delay_threshold=None)
  end_event = threading.Event()

  threads = [
    threading.Thread(target=stats_main, args=(end_event,)),
    threading.Thread(target=sp_stats, args=(end_event,)),
  ]

  for t in threads:
    t.start()

  try:
    while all(t.is_alive() for t in threads):
      rk.keep_time()
  finally:
    end_event.set()

  for t in threads:
    t.join()


if __name__ == "__main__":
  main()
