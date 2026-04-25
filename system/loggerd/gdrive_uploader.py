#!/usr/bin/env python3
import os
import time
import json
import requests
import datetime
import threading
from glob import glob

from cereal import log
import cereal.messaging as messaging
from openpilot.common.params import Params
from openpilot.system.hardware.hw import Paths
from openpilot.system.loggerd.xattr_cache import getxattr, setxattr
from openpilot.common.swaglog import cloudlog

NetworkType = log.DeviceState.NetworkType
GD_UPLOAD_ATTR_NAME = 'user.gd_upload'
GD_UPLOAD_ATTR_VALUE = b'1'

class GDriveUploader:
  def __init__(self):
    self.params = Params()

  def get_token(self, auth_json_str):
    try:
      auth = json.loads(auth_json_str)
      client_id = auth.get("client_id")
      client_secret = auth.get("client_secret")
      refresh_token = auth.get("refresh_token")
      
      if not all([client_id, client_secret, refresh_token]):
        return None

      resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
          "client_id": client_id,
          "client_secret": client_secret,
          "refresh_token": refresh_token,
          "grant_type": "refresh_token"
        },
        timeout=10
      )
      
      if resp.status_code == 200:
        return resp.json().get("access_token")
      else:
        cloudlog.error(f"GDrive Token Refresh Failed: {resp.text}")
        return None
    except Exception as e:
      cloudlog.error(f"GDrive Token Parsing Error: {str(e)}")
      return None

  def is_upload_allowed(self, sm):
    provider = self.params.get("DashcamUploaderProvider")
    if provider != b"2":
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
    video_mode = self.params.get("DashcamUploaderVideoMode") or b"0"
    upload_logs = self.params.get_bool("DashcamUploaderUploadLogs")
    
    target_exts = []
    if video_mode == b"1":
      target_exts.extend(["qcamera.ts"])
    elif video_mode == b"2":
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
            is_uploaded = getxattr(fn, GD_UPLOAD_ATTR_NAME) == GD_UPLOAD_ATTR_VALUE
            if not is_uploaded:
              files_to_upload.append((name, fn))
      except OSError:
        continue

    return files_to_upload

  def upload_file(self, access_token, name, fn, folder_id):
    try:
      sz = os.path.getsize(fn)
      do_delete = self.params.get_bool("DashcamUploaderDeleteSynced")
      
      if sz == 0:
        if do_delete:
          try: os.remove(fn)
          except Exception: pass
        else:
          setxattr(fn, GD_UPLOAD_ATTR_NAME, GD_UPLOAD_ATTR_VALUE)
        return True

      # Standard MIME types
      mime_type = "video/mp4"
      if name.endswith(".json"):
        mime_type = "application/json"
      elif name.endswith(".bz2"):
        mime_type = "application/x-bzip2"
      
      # 1. Initiate Resumable Session
      metadata = {"name": name}
      if folder_id:
        metadata["parents"] = [folder_id]

      init_resp = requests.post(
        "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable",
        headers={
          "Authorization": f"Bearer {access_token}",
          "Content-Type": "application/json",
          "X-Upload-Content-Type": mime_type
        },
        json=metadata,
        timeout=10
      )
      
      if init_resp.status_code != 200:
        cloudlog.error(f"GDrive Upload Init Failed: {init_resp.text}")
        return False

      upload_url = init_resp.headers.get("Location")
      if not upload_url:
        return False

      # 2. Upload Data
      # For very large files, chunked upload is better, but stream loading is okay for <100MB files typically
      with open(fn, 'rb') as f:
        put_resp = requests.put(
          upload_url,
          data=f,
          headers={"Content-Length": str(sz)},
          timeout=300 # Wait up to 5 min for file transfer
        )

      if put_resp.status_code in [200, 201]:
        cloudlog.info(f"GDrive Uploaded {name} successfully.")
        if do_delete:
          try:
            os.remove(fn)
            cloudlog.info(f"Deleted source file: {fn}")
          except OSError as e:
            cloudlog.error(f"Failed to delete source file {fn}: {e}")
        else:
          try:
            setxattr(fn, GD_UPLOAD_ATTR_NAME, GD_UPLOAD_ATTR_VALUE)
          except OSError:
            pass
        return True
      else:
        cloudlog.error(f"GDrive Put Failed: {put_resp.text}")
        return False
        
    except Exception as e:
      cloudlog.error(f"GDrive Upload Exception: {str(e)}")
      return False

  def step(self, sm):
    # Check preconditions
    if not self.is_upload_allowed(sm):
      return False

    auth_json_str = self.params.get("DashcamUploaderGDAuth")
    if not auth_json_str:
      return False

    if isinstance(auth_json_str, bytes):
      auth_json_str = auth_json_str.decode('utf8')

    folder_id = self.params.get("DashcamUploaderGDFolder")
    if folder_id:
      if isinstance(folder_id, bytes):
        folder_id = folder_id.decode('utf8').strip()

    # Get un-uploaded files
    files = self.list_files()
    if not files:
      return False

    # Get Token
    access_token = self.get_token(auth_json_str)
    if not access_token:
      cloudlog.warning("GDrive Uploader has zero valid access tokens")
      return False

    # Upload files (limit to e.g. 5 per cycle to prevent endless blocks)
    uploaded_any = False
    for name, fn in files[:5]:
      success = self.upload_file(access_token, name, fn, folder_id)
      if success:
        uploaded_any = True
      time.sleep(1) # Breath
      
    return uploaded_any


def main():
  sm = messaging.SubMaster(['deviceState'])
  uploader = GDriveUploader()

  while True:
    sm.update(0)
    uploaded = False
    if sm['deviceState'].networkType != NetworkType.none:
      uploaded = uploader.step(sm)
    
    # Sleep
    if uploaded:
      time.sleep(1)
    else:
      time.sleep(10)

if __name__ == "__main__":
  main()
