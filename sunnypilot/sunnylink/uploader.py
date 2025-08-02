#!/usr/bin/env python3
import bz2
import datetime
import io
import json
import os
import random
import threading
import time
import traceback
from collections.abc import Iterator
from typing import BinaryIO

import requests
from openpilot.common.params import Params
from openpilot.common.realtime import set_core_affinity
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths
from openpilot.system.loggerd.xattr_cache import getxattr, setxattr

import cereal.messaging as messaging
from cereal import log
from sunnypilot.sunnylink.api import SunnylinkApi

NetworkType = log.DeviceState.NetworkType
UPLOAD_ATTR_NAME = 'user.sunny.upload'

UPLOAD_ATTR_VALUE = b'1'

UPLOAD_QLOG_QCAM_MAX_SIZE = 5 * 1e6  # MB

allow_sleep = bool(os.getenv("UPLOADER_SLEEP", "1"))
force_wifi = os.getenv("FORCEWIFI") is not None
fake_upload = os.getenv("FAKEUPLOAD") is not None

OFFROAD_TRANSITION_TIMEOUT = 900.  # wait until offroad for 15 minutes before allowing uploads


class FakeRequest:
  def __init__(self):
    self.headers = {"Content-Length": "0"}


class FakeResponse:
  def __init__(self):
    self.status_code = 200
    self.request = FakeRequest()


def get_directory_sort(d: str) -> list[str]:
  # ensure old format is sorted sooner
  o = ["0", ] if d.startswith("2024-") else ["1", ]
  return o + [s.rjust(10, '0') for s in d.rsplit('--', 1)]


def listdir_by_creation(d: str) -> list[str]:
  if not os.path.isdir(d):
    return []

  try:
    paths = [f for f in os.listdir(d) if os.path.isdir(os.path.join(d, f))]
    paths = sorted(paths, key=get_directory_sort)
    return paths
  except OSError:
    cloudlog.exception("listdir_by_creation failed")
    return []


def clear_locks(root: str) -> None:
  for logdir in os.listdir(root):
    path = os.path.join(root, logdir)
    try:
      for fname in os.listdir(path):
        if fname.endswith(".lock"):
          os.unlink(os.path.join(path, fname))
    except OSError:
      cloudlog.exception("clear_locks failed")


class Uploader:
  def __init__(self, dongle_id: str, root: str):
    self.dongle_id = dongle_id
    self.api = SunnylinkApi(dongle_id)
    self.root = root

    self.params = Params()

    # stats for last successfully uploaded file
    self.last_filename = ""

    self.immediate_folders = ["crash/", "boot/"]
    self.immediate_priority = {"qlog": 0, "qlog.bz2": 0, "qcamera.ts": 1}

  def list_upload_files(self, metered: bool) -> Iterator[tuple[str, str, str]]:
    r = self.params.get("AthenadRecentlyViewedRoutes", encoding="utf8")
    requested_routes = [] if r is None else r.split(",")

    for logdir in listdir_by_creation(self.root):
      path = os.path.join(self.root, logdir)
      try:
        names = os.listdir(path)
      except OSError:
        continue

      if any(name.endswith(".lock") for name in names):
        continue

      for name in sorted(names, key=lambda n: self.immediate_priority.get(n, 1000)):
        key = os.path.join(logdir, name)
        fn = os.path.join(path, name)
        # skip files already uploaded
        try:
          ctime = os.path.getctime(fn)
          is_uploaded = getxattr(fn, UPLOAD_ATTR_NAME) == UPLOAD_ATTR_VALUE
        except OSError:
          cloudlog.event("uploader_getxattr_failed", key=key, fn=fn)
          # deleter could have deleted, so skip
          continue
        if is_uploaded:
          continue

        # limit uploading on metered connections
        if metered:
          dt = datetime.timedelta(hours=12)
          if logdir in self.immediate_folders and (datetime.datetime.now() - datetime.datetime.fromtimestamp(ctime)) < dt:
            continue

          if name == "qcamera.ts" and not any(logdir.startswith(r.split('|')[-1]) for r in requested_routes):
            continue

        yield name, key, fn

  def next_file_to_upload(self, metered: bool) -> tuple[str, str, str] | None:
    upload_files = list(self.list_upload_files(metered))

    for name, key, fn in upload_files:
      if any(f in fn for f in self.immediate_folders):
        return name, key, fn

    return next(
      ((name, key, fn)
       for name, key, fn in upload_files if name in self.immediate_priority),
      None,
    )

  def do_upload(self, key: str, fn: str):
    url_resp = self.api.get(
      f"device/{self.dongle_id}/upload_url/",
      timeout=10,
      path=key,
      access_token=self.api.get_token(),
    )
    if url_resp.status_code == 412:
      return url_resp

    url_resp_json = json.loads(url_resp.text)
    url = url_resp_json['url']
    headers = url_resp_json['headers']
    cloudlog.debug("sunnylink upload_url %s | Headers: %s", url, headers)

    if fake_upload:
      return FakeResponse()

    with open(fn, "rb") as f:
      data: BinaryIO
      if key.endswith('.bz2') and not fn.endswith('.bz2'):
        compressed = bz2.compress(f.read())
        data = io.BytesIO(compressed)
      else:
        data = f

      return requests.put(url, data=data, headers=headers, timeout=10)

  def upload(self, name: str, key: str, fn: str, network_type: int, metered: bool) -> bool:
    try:
      sz = os.path.getsize(fn)
    except OSError:
      cloudlog.exception("upload: getsize failed")
      return False

    cloudlog.event("upload_start", key=key, fn=fn, sz=sz, network_type=network_type, metered=metered)

    if sz == 0:
      # tag files of 0 size as uploaded
      success = True
    elif name in self.immediate_priority and sz > UPLOAD_QLOG_QCAM_MAX_SIZE:
      cloudlog.event("uploader_too_large", key=key, fn=fn, sz=sz)
      success = True
    else:
      start_time = time.monotonic()

      stat = None
      last_exc = None
      try:
        stat = self.do_upload(key, fn)
      except Exception as e:
        last_exc = (e, traceback.format_exc())

      if stat is not None and stat.status_code in (200, 201, 412):
        self.last_filename = fn
        dt = time.monotonic() - start_time
        if stat.status_code == 412:
          cloudlog.event("upload_ignored", key=key, fn=fn, sz=sz, network_type=network_type, metered=metered)
        else:
          content_length = int(stat.request.headers.get("Content-Length", 0))
          speed = (content_length / 1e6) / dt
          cloudlog.event("upload_success", key=key, fn=fn, sz=sz, content_length=content_length,
                         network_type=network_type, metered=metered, speed=speed)
        success = True
      elif stat is not None:  # 401, 403... Not sure why they were up to begin with
        success = False
        cloudlog.event("upload_failed with content", stat=stat, exc=last_exc, key=key, fn=fn, sz=sz, network_type=network_type, metered=metered,
                       error=stat.content.decode("utf-8"))
      else:
        success = False
        cloudlog.event("upload_failed", stat=stat, exc=last_exc, key=key, fn=fn, sz=sz, network_type=network_type, metered=metered)

    if success:
      # tag file as uploaded
      try:
        setxattr(fn, UPLOAD_ATTR_NAME, UPLOAD_ATTR_VALUE)
      except OSError:
        cloudlog.event("uploader_setxattr_failed", exc=last_exc, key=key, fn=fn, sz=sz)

    return success

  def step(self, network_type: int, metered: bool) -> bool | None:
    d = self.next_file_to_upload(metered)
    if d is None:
      return None

    name, key, fn = d

    # qlogs and bootlogs need to be compressed before uploading
    if key.endswith(('qlog', 'rlog')) or (key.startswith('boot/') and not key.endswith('.bz2')):
      key += ".bz2"

    return self.upload(name, key, fn, network_type, metered)


def main(exit_event: threading.Event = None) -> None:
  if exit_event is None:
    exit_event = threading.Event()

  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  clear_locks(Paths.log_root())

  params = Params()
  dongle_id = params.get("SunnylinkDongleId", encoding='utf8')

  offroad_transition_prev = 0.
  offroad_last = False

  if dongle_id is None:
    cloudlog.info("uploader missing dongle_id")
    raise Exception("uploader can't start without dongle id")

  sm = messaging.SubMaster(['deviceState'])
  uploader = Uploader(dongle_id, Paths.log_root())

  backoff = 0.1
  while not exit_event.is_set():
    sm.update(0)

    offroad = params.get_bool("IsOffroad")
    t = time.monotonic()
    if offroad and not offroad_last and t > 300.:
      offroad_transition_prev = time.monotonic()
    offroad_last = offroad

    network_type = NetworkType.wifi if force_wifi else sm['deviceState'].networkType
    if network_type == NetworkType.none:
      if allow_sleep:
        time.sleep(60 if offroad else 5)
      continue

    if params.get_bool("DisableOnroadUploads"):
      if not offroad or (offroad_transition_prev > 0. and t - offroad_transition_prev < OFFROAD_TRANSITION_TIMEOUT):
        if not offroad:
          cloudlog.info("not uploading: onroad uploads disabled")
        else:
          wait_minutes = int(OFFROAD_TRANSITION_TIMEOUT / 60)
          time_left = OFFROAD_TRANSITION_TIMEOUT - (t - offroad_transition_prev)
          if time_left > 2.0 * 60.0:
            time_left_str = f"{int(time_left / 60)} minute(s)"
          else:
            time_left_str = f"{int(time_left)} seconds(s)"
          cloudlog.info(f"not uploading: waiting until offroad for {wait_minutes} minutes; {time_left_str} left")
        if allow_sleep:
          time.sleep(60)
        continue

    success = uploader.step(sm['deviceState'].networkType.raw, sm['deviceState'].networkMetered)
    if success is None:
      backoff = 60 if offroad else 5
    elif success:
      backoff = 0.1
    else:
      cloudlog.info("upload backoff %r", backoff)
      backoff = min(backoff * 2, 120)
    if allow_sleep:
      time.sleep(backoff + random.uniform(0, backoff))


if __name__ == "__main__":
  main()
