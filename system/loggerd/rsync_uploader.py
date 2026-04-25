#!/usr/bin/env python3
import os
import stat
import time
import subprocess
from glob import glob

from cereal import log
import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.system.hardware.hw import Paths
from openpilot.system.loggerd.xattr_cache import getxattr, setxattr
from openpilot.common.swaglog import cloudlog

NetworkType = log.DeviceState.NetworkType
RSYNC_UPLOAD_ATTR_NAME = 'user.rsync_upload'
RSYNC_UPLOAD_ATTR_VALUE = b'1'
KEY_PATH = '/data/rsync_key'

class RsyncUploader:
  def __init__(self):
    self.params = Params()

  def is_upload_allowed(self, sm):
    try:
      if int(self.params.get("DashcamUploaderProvider") or 0) != 2:
        return False
    except Exception:
      return False
      
    sync_mode = self.params.get("DashcamUploaderSyncMode")
    if sync_mode is None or sync_mode == b"0":
      return False

    network_type = sm['deviceState'].networkType
    metered = sm['deviceState'].networkMetered

    if sync_mode == b"1": # WiFi Only
      return network_type == NetworkType.wifi and not metered
    elif sync_mode == b"2": # WiFi + LTE
      return network_type != NetworkType.none
      
    return False

  def list_files(self):
    video_raw = self.params.get("DashcamUploaderVideoMode")
    try:
      vm = int(video_raw)
    except Exception:
      vm = 0
    upload_logs = self.params.get_bool("DashcamUploaderUploadLogs")
    
    target_exts = []
    if vm == 1:
      target_exts.extend(["qcamera.ts"])
    elif vm == 2:
      target_exts.extend(["fcamera.hevc", "vcamera.hevc", "ecamera.hevc"])

    if upload_logs:
      target_exts.extend([".bz2", ".qlog", ".rlog", ".json"])

    log_root = Paths.log_root()
    files_to_upload = []

    if not os.path.isdir(log_root):
      return files_to_upload

    for d in os.listdir(log_root):
      path = os.path.join(log_root, d)
      if not os.path.isdir(path):
        continue

      try:
        names = os.listdir(path)
        for name in names:
          if any(name.endswith(ext) for ext in target_exts) or any(name == ext for ext in target_exts):
            fn = os.path.join(path, name)
            is_uploaded = getxattr(fn, RSYNC_UPLOAD_ATTR_NAME) == RSYNC_UPLOAD_ATTR_VALUE
            if not is_uploaded:
              files_to_upload.append((name, fn))
      except OSError:
        continue

    return files_to_upload

  def prepare_key(self, key_str):
    try:
      # Write key to disk and ensure correct permissions (required by SSH)
      with open(KEY_PATH, 'w') as f:
        f.write(key_str)
      os.chmod(KEY_PATH, stat.S_IRUSR | stat.S_IWUSR)
      return True
    except Exception as e:
      cloudlog.error(f"Failed to write Rsync SSH key: {e}")
      return False

  def upload_file(self, name, fn, target, do_delete):
    try:
      sz = os.path.getsize(fn)
      if sz == 0:
        if do_delete:
          try: os.remove(fn)
          except Exception: pass
        else:
          setxattr(fn, RSYNC_UPLOAD_ATTR_NAME, RSYNC_UPLOAD_ATTR_VALUE)
        return True

      cmd = [
        "rsync",
        "-avz",
        "-e", f"ssh -i {KEY_PATH} -o StrictHostKeyChecking=no",
      ]
      
      if do_delete:
        cmd.append("--remove-source-files")

      cmd.append(fn)
      cmd.append(target)

      cloudlog.info(f"Rsync executing: {' '.join(cmd)}")
      result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

      if result.returncode == 0:
        cloudlog.info(f"Rsync Uploaded {name} successfully.")
        if not do_delete:
          try:
            setxattr(fn, RSYNC_UPLOAD_ATTR_NAME, RSYNC_UPLOAD_ATTR_VALUE)
          except OSError:
            pass
        return True
      else:
        cloudlog.error(f"Rsync Put Failed (Code: {result.returncode}): {result.stderr}")
        return False
        
    except subprocess.TimeoutExpired:
      cloudlog.error(f"Rsync Upload Timeout: {name}")
      return False
    except Exception as e:
      cloudlog.error(f"Rsync Upload Exception: {str(e)}")
      return False

  def step(self, sm):
    if not self.is_upload_allowed(sm):
      return False

    target = self.params.get("DashcamUploaderRsyncTarget")
    if not target:
      return False
    target = target.decode('utf8').strip()

    key_str = self.params.get("DashcamUploaderRsyncKey")
    if not key_str:
      cloudlog.warning("Rsync Uploader missing private key")
      return False
    key_str = key_str.decode('utf8').replace('\\n', '\n') # unescape newlines if needed

    if not self.prepare_key(key_str):
      return False

    files = self.list_files()
    if not files:
      return False

    do_delete = self.params.get_bool("DashcamUploaderDeleteSynced")
    uploaded_any = False

    for name, fn in files[:5]:
      success = self.upload_file(name, fn, target, do_delete)
      if success:
        uploaded_any = True
      time.sleep(1)
      
    return uploaded_any


def main():
  sm = messaging.SubMaster(['deviceState'])
  uploader = RsyncUploader()

  while True:
    sm.update(0)
    uploaded = False
    if sm['deviceState'].networkType != NetworkType.none:
      uploaded = uploader.step(sm)
    
    if uploaded:
      time.sleep(1)
    else:
      time.sleep(10)

if __name__ == "__main__":
  main()
