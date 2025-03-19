"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import base64
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any

from openpilot.common.git import get_branch
from openpilot.common.params import Params, ParamKeyType
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.system.hardware.hw import Paths
from openpilot.system.version import get_version

from cereal import messaging, custom
from sunnypilot.sunnylink.api import SunnylinkApi
from sunnypilot.sunnylink.backups.utils import decrypt_compressed_data, encrypt_compress_data, SnakeCaseEncoder


class BackupManagerSP:
  """Manages device configuration backups to/from sunnylink"""

  def __init__(self):
    self.params = Params()
    self.device_id = self.params.get("SunnylinkDongleId", encoding="utf8")
    self.api = SunnylinkApi(self.device_id)
    self.pm = messaging.PubMaster(["backupManagerSP"])

    # Status tracking
    self.backup_status = custom.BackupManagerSP.Status.idle
    self.restore_status = custom.BackupManagerSP.Status.idle
    self.backup_history: List[custom.BackupManagerSP.BackupInfo] = []
    self.current_backup: Optional[custom.BackupManagerSP.BackupInfo] = None
    self.backup_progress = 0.0
    self.restore_progress = 0.0
    self.last_error = ""

    # Keys used for encryption/decryption
    self.key_path = Path(f"{Paths.persist_root()}/comma/id_rsa")

  def _report_status(self) -> None:
    """Reports current backup manager state through messaging system"""
    msg = messaging.new_message('backupManagerSP', valid=True)
    backup_state = msg.backupManagerSP

    backup_state.backupStatus = self.backup_status
    backup_state.restoreStatus = self.restore_status
    backup_state.backupProgress = self.backup_progress
    backup_state.restoreProgress = self.restore_progress
    backup_state.lastError = self.last_error

    if self.current_backup:
      backup_state.currentBackup = self.current_backup

    backup_state.backupHistory = self.backup_history

    self.pm.send('backupManagerSP', msg)

  def _create_backup_info(self, backup_data: Dict) -> custom.BackupManagerSP.BackupInfo:
    """Creates a BackupInfo object from API response data"""
    backup_info = custom.BackupManagerSP.BackupInfo()
    backup_info.deviceId = backup_data.get("device_id", "")
    backup_info.version = backup_data.get("version", 0)
    backup_info.isEncrypted = backup_data.get("is_encrypted", True)
    backup_info.createdAt = backup_data.get("created_at", "")
    backup_info.updatedAt = backup_data.get("updated_at", "")

    # Parse sunnypilot version
    sp_version = backup_data.get("sunnypilot_version", {})
    backup_info.sunnypilotVersion.major = sp_version.get("major", 0)
    backup_info.sunnypilotVersion.minor = sp_version.get("minor", 0)
    backup_info.sunnypilotVersion.patch = sp_version.get("patch", 0)
    backup_info.sunnypilotVersion.build = sp_version.get("build", 0)
    backup_info.sunnypilotVersion.branch = sp_version.get("branch", "")

    # Parse metadata
    metadata_entries = []
    for entry in backup_data.get("backup_metadata", []):
      metadata = custom.BackupManagerSP.MetadataEntry.new_message()
      metadata.key = entry.get("key", "")
      metadata.value = entry.get("value", "")
      metadata.tags = entry.get("tags", [])
      metadata_entries.append(metadata)

    backup_info.metadata = metadata_entries
    return backup_info

  def _collect_config_data(self) -> Dict[str, Any]:
    """Collects configuration data to be backed up"""
    # This would collect parameters or other data that needs to be backed up
    # Implementation depends on what specifically needs to be backed up
    config_data = {}

    params_to_backup = [k.decode('utf-8') for k in self.params.all_keys(ParamKeyType.BACKUP)]
    for param in params_to_backup:
      value = self.params.get(param)
      if value is not None:
        config_data[param] = base64.b64encode(value).decode('utf-8')

    return config_data

  async def create_backup(self) -> bool:
    """Creates and uploads a new backup to sunnylink"""
    try:
      self.backup_status = custom.BackupManagerSP.Status.inProgress
      self.backup_progress = 0.0
      self._report_status()

      # Collect configuration data
      config_data = self._collect_config_data()
      self.backup_progress = 25.0
      self._report_status()

      # Serialize and encrypt config data
      config_json = json.dumps(config_data)
      encrypted_config = encrypt_compress_data(config_json, self.key_path)
      self.backup_progress = 50.0
      self._report_status()
      
      backup_info = custom.BackupManagerSP.BackupInfo()
      backup_info.deviceId = self.device_id
      backup_info.config = encrypted_config
      backup_info.isEncrypted = True
      backup_info.createdAt = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
      backup_info.updatedAt = backup_info.createdAt
      backup_info.sunnypilotVersion = self._get_current_version()
      backup_info.metadata = [
          custom.BackupManagerSP.MetadataEntry(key="creator", value="BackupManagerSP"),
          custom.BackupManagerSP.MetadataEntry(key="all_values_encoded", value="True"),
          custom.BackupManagerSP.MetadataEntry(key="AES", value="256")
        ]

      payload = json.loads(json.dumps(backup_info.to_dict(), cls=SnakeCaseEncoder))
      self.backup_progress = 75.0
      self._report_status()

      # Upload to sunnylink
      result = self.api.api_get(f"backup/{self.device_id}", method='PUT', access_token=self.api.get_token(), json=payload)

      if result:
        self.current_backup = self._create_backup_info(result.json())
        self.backup_status = custom.BackupManagerSP.Status.completed
        self.backup_progress = 100.0
      else:
        self.backup_status = custom.BackupManagerSP.Status.failed
        self.last_error = "Failed to upload backup"

      self._report_status()
      return self.backup_status == custom.BackupManagerSP.Status.completed

    except Exception as e:
      cloudlog.exception(f"Error creating backup: {str(e)}")
      self.backup_status = custom.BackupManagerSP.Status.failed
      self.last_error = str(e)
      self._report_status()
      return False

  async def restore_backup(self, version: Optional[int] = None) -> bool:
    """Restores a backup from sunnylink"""
    try:
      self.restore_status = custom.BackupManagerSP.Status.inProgress
      self.restore_progress = 0.0
      self._report_status()

      # Get backup data from API
      endpoint = f"backup/{self.device_id}"
      if version is not None:
        endpoint = f"{endpoint}/{version}"

      backup_data = self.api.api_get(endpoint, access_token=self.api.get_token())
      if not backup_data:
        raise Exception(f"No backup found for device {self.device_id}")

      self.restore_progress = 25.0
      self._report_status()

      # Get encrypted config
      encrypted_config = backup_data.json().get("config", "")
      if not encrypted_config:
        raise Exception("Empty backup configuration")

      self.restore_progress = 50.0
      self._report_status()

      # Decrypt config
      config_json = decrypt_compressed_data(encrypted_config, self.key_path)
      config_data = json.loads(config_json)

      self.restore_progress = 75.0
      self._report_status()

      # Apply configuration
      backup_metadata = backup_data.json().get("backup_metadata", [])
      all_values_encoded = next((entry.get("value") for entry in backup_metadata if entry.get("key") == "all_values_encoded"), None)
      self._apply_config(config_data, str(all_values_encoded).lower() == "true")

      self.restore_status = custom.BackupManagerSP.Status.completed
      self.restore_progress = 100.0
      self._report_status()
      return True

    except Exception as e:
      cloudlog.exception(f"Error restoring backup: {str(e)}")
      self.restore_status = custom.BackupManagerSP.Status.failed
      self.last_error = str(e)
      self._report_status()
      return False

  def _apply_config(self, config_data: Dict[str, str], all_values_encoded=False) -> None:
    """Applies configuration data from a backup"""
    # Implementation depends on what specifically was backed up
    for param, encoded_value in config_data.items():
      try:
        value = encoded_value
        if all_values_encoded:
          value = base64.b64decode(encoded_value)
        self.params.put(param, value)
      except Exception as e:
        cloudlog.error(f"Failed to restore param {param}: {str(e)}")


  def _get_current_version(self) -> custom.BackupManagerSP.Version:
    """Gets current sunnypilot version information"""
    # This implementation would depend on how version info is stored
    # Example implementation:
    version_info = custom.BackupManagerSP.Version()
    versioning = get_version().split('.')
    version_info.major = int(versioning[0]) if len(versioning) > 0 else 0
    version_info.minor = int(versioning[1]) if len(versioning) > 1 else 0
    version_info.patch = int(versioning[2]) if len(versioning) > 2 else 0
    version_info.build = int(versioning[3]) if len(versioning) > 3 else 0
    version_info.branch = get_branch()
    return version_info

  async def main_thread(self) -> None:
    """Main thread for backup management"""
    rk = Ratekeeper(1, print_delay_threshold=None)

    while True:
      try:
        # Check for backup command
        if self.params.get_bool("BackupManager_CreateBackup"):
          try:
            await self.create_backup()
          finally:
            self.params.remove("BackupManager_CreateBackup")

        # Check for restore command
        restore_version = self.params.get("BackupManager_RestoreVersion", encoding="utf8")
        if restore_version:
          try:
            version = int(restore_version) if restore_version.isdigit() else None
            await self.restore_backup(version)
          finally:
            self.params.remove("BackupManager_RestoreVersion")

        self._report_status()
        rk.keep_time()

      except Exception as e:
        cloudlog.exception(f"Error in backup manager main thread: {str(e)}")
        self.last_error = str(e)
        self._report_status()
        rk.keep_time()


def main():
  import asyncio
  asyncio.run(BackupManagerSP().main_thread())


if __name__ == "__main__":
  main()