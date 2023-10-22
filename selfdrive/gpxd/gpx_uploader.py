#!/usr/bin/env python3
# The MIT License
#
# Copyright (c) 2019-, Rick Lan, dragonpilot community, and a number of other of contributors.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os
import time
from cereal import log
import cereal.messaging as messaging
from common.params import Params
from common.realtime import set_core_affinity, Ratekeeper
from selfdrive.athena.registration import register
from system.swaglog import cloudlog
from system.version import get_version

# for uploader
from system.loggerd.xattr_cache import getxattr, setxattr
import glob
import requests
import json

NetworkType = log.DeviceState.NetworkType

RATE = 1

# customisable values
GPX_LOG_PATH = '/data/media/0/gpx_logs/'
LOG_HERTZ = 1/10  # 0.1 Hz = 10 sec, higher for higher accuracy, 10hz seems fine

# uploader
UPLOAD_ATTR_NAME = 'user.upload'
UPLOAD_ATTR_VALUE = b'1'
LOG_PATH = '/data/media/0/gpx_logs/'

# osm api
VERSION_URL = 'https://api.openstreetmap.org/api/versions'
UPLOAD_URL = 'https://sunnypilot.com/osm/gpx_uploader.php'

_DEBUG = False


def _debug(msg):
  if not _DEBUG:
    return
  print(msg, flush=True)


def _get_is_uploaded(filename):
  _debug("%s is uploaded: %s" % (filename, getxattr(filename, UPLOAD_ATTR_NAME) is not None))
  return getxattr(filename, UPLOAD_ATTR_NAME) is not None


def _set_is_uploaded(filename):
  _debug("%s set to uploaded" % filename)
  setxattr(filename, UPLOAD_ATTR_NAME, UPLOAD_ATTR_VALUE)


def _get_files_to_be_uploaded():
  files = sorted(filter(os.path.isfile, glob.glob(LOG_PATH + '*')))
  files_to_be_uploaded = []
  for file in files:
    if not _get_is_uploaded(file):
      files_to_be_uploaded.append(file)
  return files_to_be_uploaded


class GpxUploader:
  def __init__(self, sm):
    self.sm = sm
    self.param_s = Params()
    self.rk = Ratekeeper(RATE, print_delay_threshold=None)

    self._delete_after_upload = self.param_s.get_bool('GpxDeleteAfterUpload')
    self._car_model = "Unknown Model"
    # read model from LiveParameters
    params = self.param_s.get("LiveParameters")
    if params is not None:
      params = json.loads(params)
      self._car_model = params.get('carFingerprint', self._car_model)
    self._sp_version = get_version()
    _debug("GpxUploader init - _delete_after_upload = %s" % self._delete_after_upload)
    _debug("GpxUploader init - _car_model = %s" % self._car_model)
    self.api_headers = {"User-Agent": f"sunnypilot-{self._sp_version}-{register()}"}

  def update(self):
    while True:
      self.sm.update(0)
      files = _get_files_to_be_uploaded()
      network_type = self.sm['deviceState'].networkType
      if len(files) == 0 or not self._is_online():
        _debug("run - not online or no files")
      elif network_type != NetworkType.wifi:
        _debug("run - not on Wi-Fi")
      elif not self.param_s.get_bool("DisableOnroadUploads") or self.param_s.get_bool("IsOffroad"):
        for file in files:
          if self._do_upload(file):
            if self._delete_after_upload:
              _debug("run - _delete_after_upload")
              os.remove(file)
            else:
              _debug("run - set_is_uploaded")
              _set_is_uploaded(file)
      # sleep for 300 secs if offroad
      # otherwise sleep 60 secs
      time.sleep(300 if self.param_s.get_bool("IsOffroad") else 60)
      self.rk.keep_time()

  def _is_online(self):
    try:
      r = requests.get(VERSION_URL, headers=self.api_headers)
      _debug("is_online? status_code = %s" % r.status_code)
      return r.status_code >= 200
    except Exception as e:
      print(f'Online check error: {e}')
      return False

  def _do_upload(self, filename):
    fn = os.path.basename(filename)
    data = {
      'description': "Routes from sunnypilot %s (%s)." % (self._sp_version, self._car_model),
      'visibility': 'identifiable'
    }
    files = {
      "file": (fn, open(filename, 'rb'))
    }
    try:
      r = requests.post(UPLOAD_URL, files=files, data=data, headers=self.api_headers)
      _debug("do_upload - %s - %s" % (filename, r.status_code))
      return r.status_code == 200
    except Exception as e:
      print(f'Upload error: {e}')
      return False

  def gpx_uploader_thread(self):
    try:
      set_core_affinity([0, 1, 2, 3])
    except Exception:
      cloudlog.exception("gpx_uploader: failed to set core affinity")

    self.update()


def main(sm=None):
  if sm is None:
    sm = messaging.SubMaster(['deviceState'])

  gpx_uploader = GpxUploader(sm)
  gpx_uploader.gpx_uploader_thread()


if __name__ == "__main__":
  main()
