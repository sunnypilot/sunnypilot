#!/usr/bin/env python3
import os
import random
import requests
import threading
import time
import traceback
import datetime
from collections.abc import Iterator
from urllib.parse import urljoin, quote

from cereal import log
import cereal.messaging as messaging
from openpilot.common.utils import get_upload_stream
from openpilot.common.params import Params
from openpilot.common.realtime import set_core_affinity
from openpilot.system.hardware.hw import Paths
from openpilot.system.loggerd.xattr_cache import getxattr, setxattr
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.webdav.utils import get_webdav_config

NetworkType = log.DeviceState.NetworkType
UPLOAD_ATTR_NAME = 'user.webdav.upload'
UPLOAD_ATTR_VALUE = b'1'

MAX_UPLOAD_SIZES = {
  "qlog": 25*1e6,  # can't be too restrictive here since we use qlogs to find
  # bugs, including ones that can cause massive log sizes
  "qcam": 5*1e6,
}

allow_sleep = bool(os.getenv("UPLOADER_SLEEP", "1"))
force_wifi = os.getenv("FORCEWIFI") is not None
fake_upload = os.getenv("FAKEUPLOAD") is not None


class FakeRequest:
  def __init__(self):
    self.headers = {"Content-Length": "0"}


class FakeResponse:
  """Fake response for testing. Returns 201 Created which is the semantically
  correct status code for WebDAV PUT operations that create new resources."""
  def __init__(self):
    self.status_code = 201
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


class WebDAVUploader:
  def __init__(self, dongle_id: str, root: str):
    self.dongle_id = dongle_id
    self.root = root

    self.params = Params()

    # stats for last successfully uploaded file
    self.last_filename = ""

    self.immediate_folders = ["crash/", "boot/"]
    self.immediate_priority = {"qlog": 0, "qlog.zst": 0, "qcamera.ts": 1}

  def list_upload_files(self, metered: bool) -> Iterator[tuple[str, str, str]]:
    r = self.params.get("AthenadRecentlyViewedRoutes")
    requested_routes = [] if r is None else [route for route in r.split(",") if route]

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
          cloudlog.event("webdav_uploader_getxattr_failed", key=key, fn=fn)
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

    for name, key, fn in upload_files:
      if name in self.immediate_priority:
        return name, key, fn

    return None

  def _ensure_remote_directory(self, endpoint: str, path: str, auth: tuple | None) -> bool:
    """Ensure the remote directory exists by creating parent directories."""
    # Build path components
    parts = path.strip('/').split('/')
    current_path = ""

    for part in parts[:-1]:  # Skip the filename
      current_path = f"{current_path}/{part}" if current_path else part
      dir_url = urljoin(endpoint.rstrip('/') + '/', quote(current_path) + '/')

      try:
        # Try MKCOL to create directory (will fail if exists, which is fine)
        response = requests.request('MKCOL', dir_url, auth=auth, timeout=10)
        # 201 = created, 405 = already exists (method not allowed)
        if response.status_code not in (201, 405):
          cloudlog.debug("webdav_mkdir status %d for %s", response.status_code, dir_url)
      except Exception:
        cloudlog.exception("webdav_mkdir failed for %s", dir_url)
        return False

    return True

  def do_upload(self, key: str, fn: str) -> requests.Response | FakeResponse:
    _, endpoint, folder, username, password = get_webdav_config(self.params)

    if not endpoint:
      raise ValueError("WebDAV endpoint not configured")

    # Warn if not using HTTPS
    if not endpoint.lower().startswith('https://'):
      cloudlog.warning("WebDAV endpoint is not using HTTPS - credentials will be sent in cleartext")

    auth = (username, password) if username and password is not None else None

    # Build the upload URL with optional folder prefix and dongle_id
    # URL structure: {endpoint}/{folder}/{dongle_id}/{key}
    # If folder is not set or empty, uses: {endpoint}/{dongle_id}/{key}
    folder_stripped = folder.strip('/') if folder else ""
    if folder_stripped:
      upload_path = f"{folder_stripped}/{self.dongle_id}/{key}"
    else:
      upload_path = f"{self.dongle_id}/{key}"
    upload_url = urljoin(endpoint.rstrip('/') + '/', quote(upload_path))

    cloudlog.debug("webdav upload_url %s", upload_url)

    if fake_upload:
      return FakeResponse()

    # Ensure parent directory exists
    if not self._ensure_remote_directory(endpoint, upload_path, auth):
      raise Exception("Could not ensure remote directory exists")

    stream = None
    try:
      compress = key.endswith('.zst') and not fn.endswith('.zst')
      stream, _ = get_upload_stream(fn, compress)
      response = requests.put(upload_url, data=stream, auth=auth, timeout=30)
      return response
    finally:
      if stream:
        stream.close()

  def upload(self, name: str, key: str, fn: str, network_type: int, metered: bool) -> bool:
    try:
      sz = os.path.getsize(fn)
    except OSError:
      cloudlog.exception("webdav_upload: getsize failed")
      return False

    cloudlog.event("webdav_upload_start", key=key, fn=fn, sz=sz, network_type=network_type, metered=metered)

    if sz == 0:
      # tag files of 0 size as uploaded
      success = True
    elif name in MAX_UPLOAD_SIZES and sz > MAX_UPLOAD_SIZES[name]:
      cloudlog.event("webdav_uploader_too_large", key=key, fn=fn, sz=sz)
      success = True
    else:
      start_time = time.monotonic()

      stat = None
      last_exc = None
      try:
        stat = self.do_upload(key, fn)
      except Exception as e:
        last_exc = (e, traceback.format_exc())

      if stat is not None and stat.status_code in (200, 201, 204):
        self.last_filename = fn
        dt = time.monotonic() - start_time
        content_length = int(stat.request.headers.get("Content-Length", 0))
        speed = (content_length / 1e6) / dt if dt > 0 else 0
        cloudlog.event("webdav_upload_success", key=key, fn=fn, sz=sz, content_length=content_length,
                       network_type=network_type, metered=metered, speed=speed)
        success = True
      elif stat is not None:
        success = False
        cloudlog.event("webdav_upload_failed with content", stat=stat, exc=last_exc, key=key, fn=fn, sz=sz,
                       network_type=network_type, metered=metered, error=stat.text[:500] if stat.text else "")
      else:
        success = False
        cloudlog.event("webdav_upload_failed", stat=stat, exc=last_exc, key=key, fn=fn, sz=sz,
                       network_type=network_type, metered=metered)

    if success:
      # tag file as uploaded
      try:
        setxattr(fn, UPLOAD_ATTR_NAME, UPLOAD_ATTR_VALUE)
      except OSError:
        cloudlog.event("webdav_uploader_setxattr_failed", key=key, fn=fn, sz=sz)

    return success

  def step(self, network_type: int, metered: bool) -> bool | None:
    d = self.next_file_to_upload(metered)
    if d is None:
      return None

    name, key, fn = d

    # qlogs and bootlogs need to be compressed before uploading
    if key.endswith(('qlog', 'rlog')) or (key.startswith('boot/') and not key.endswith('.zst')):
      key += ".zst"

    return self.upload(name, key, fn, network_type, metered)


def main(exit_event: threading.Event | None = None) -> None:
  if exit_event is None:
    exit_event = threading.Event()

  try:
    set_core_affinity([0, 1, 2, 3])
  except Exception:
    cloudlog.exception("failed to set core affinity")

  clear_locks(Paths.log_root())

  params = Params()
  dongle_id = params.get("DongleId")

  if dongle_id is None:
    cloudlog.info("webdav_uploader missing dongle_id")
    raise Exception("webdav_uploader can't start without dongle id")

  sm = messaging.SubMaster(['deviceState'])
  uploader = WebDAVUploader(dongle_id, Paths.log_root())

  backoff = 0.1
  while not exit_event.is_set():
    sm.update(0)
    offroad = params.get_bool("IsOffroad")
    network_type = sm['deviceState'].networkType if not force_wifi else NetworkType.wifi
    if network_type == NetworkType.none:
      if allow_sleep:
        time.sleep(60 if offroad else 5)
      continue

    success = uploader.step(sm['deviceState'].networkType.raw, sm['deviceState'].networkMetered)
    if success is None:
      backoff = 60 if offroad else 5
    elif success:
      backoff = 0.1
    else:
      cloudlog.info("webdav_upload backoff %r", backoff)
      backoff = min(backoff*2, 120)
    if allow_sleep:
      time.sleep(backoff + random.uniform(0, backoff))


if __name__ == "__main__":
  main()
