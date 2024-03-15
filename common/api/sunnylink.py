import os
import time
import jwt
import json
from pathlib import Path
from datetime import datetime, timedelta
from openpilot.common.params import Params
from openpilot.system.hardware import HARDWARE
from openpilot.system.hardware.hw import Paths

from openpilot.common.api.base import BaseApi

API_HOST = os.getenv('SUNNYLINK_API_HOST', 'https://stg.api.sunnypilot.ai')
UNREGISTERED_SUNNYLINK_DONGLE_ID = "UnregisteredDevice"
MAX_RETRIES = 6


class SunnylinkApi(BaseApi):
  def __init__(self, dongle_id):
    super().__init__(dongle_id, API_HOST)
    self.user_agent = "sunnypilot-"
    self.spinner = None

  def get_token(self, expiry_hours=1):
    # Add your additional data here
    additional_data = {}
    return super()._get_token(expiry_hours, **additional_data)

  def _status_update(self, message):
    print(message)
    if self.spinner:
      self.spinner.update(message)
      time.sleep(0.5)

  def _resolve_dongle_ids(self, params):
    sunnylink_dongle_id = params.get("SunnylinkDongleId", encoding='utf-8')
    comma_dongle_id = self.dongle_id or params.get("DongleId", encoding='utf-8')
    return sunnylink_dongle_id, comma_dongle_id

  def _resolve_imeis(self, params):
    imei1, imei2 = None, None
    imei_try = 0
    while imei1 is None and imei2 is None and imei_try < MAX_RETRIES:
      try:
        imei1, imei2 = params.get("IMEI", encoding='utf8') or HARDWARE.get_imei(0), HARDWARE.get_imei(1)
      except Exception:
        self._status_update(f"Error getting imei, trying again... [{imei_try+1}/{MAX_RETRIES}]")
        time.sleep(1)
      imei_try += 1
    return imei1, imei2

  def _resolve_serial(self, params):
    serial = params.get("HardwareSerial", encoding='utf8') or HARDWARE.get_serial()
    return serial

  def register_device(self, spinner=None, timeout=60, verbose=False):
    self.spinner = spinner
    params = Params()

    sunnylink_dongle_id, comma_dongle_id = self._resolve_dongle_ids(params)

    if comma_dongle_id is None:
      self._status_update("Comma dongle ID not found, deferring sunnylink's registration to comma's registration process.")
      return None

    imei1, imei2 = self._resolve_imeis(params)
    serial = self._resolve_serial(params)

    if sunnylink_dongle_id not in (None, UNREGISTERED_SUNNYLINK_DONGLE_ID):
      return sunnylink_dongle_id

    privkey_path = Path(Paths.persist_root()+"/comma/id_rsa")
    pubkey_path = Path(Paths.persist_root()+"/comma/id_rsa.pub")

    if not pubkey_path.is_file():
      sunnylink_dongle_id = UNREGISTERED_SUNNYLINK_DONGLE_ID
      self._status_update("Public key not found, setting dongle ID to unregistered.")
    else:
      with pubkey_path.open() as f1, privkey_path.open() as f2:
        public_key = f1.read()
        private_key = f2.read()

      start_time = time.monotonic()
      backoff = 1
      while True:
        register_token = jwt.encode({'register': True, 'exp': datetime.utcnow() + timedelta(hours=1)}, private_key, algorithm='RS256')
        try:
          if verbose or time.monotonic() - start_time < timeout / 2:
            self._status_update("Registering device to sunnylink...")
          elif time.monotonic() - start_time >= timeout / 2:
            self._status_update("Still registering device to sunnylink...")

          resp = self.api_get("v2/pilotauth/", method='POST', timeout=15, imei=imei1, imei2=imei2, serial=serial, comma_dongle_id=comma_dongle_id, public_key=public_key, register_token=register_token)

          if resp.status_code != 200:
            raise Exception(f"Failed to register with sunnylink. Status code: {resp.status_code}")
          else:
            dongleauth = json.loads(resp.text)
            sunnylink_dongle_id = dongleauth["dongle_id"]
            if sunnylink_dongle_id:
              self._status_update("Device registered successfully.")
              break
        except Exception as e:
          if verbose:
            self._status_update(f"Waiting {backoff}s before retry, Exception occurred during registration: [{str(e)}]")
          backoff = min(backoff * 2, 60)
          time.sleep(backoff)

        if time.monotonic() - start_time > timeout:
          self._status_update(f"Giving up on sunnylink's registration after {timeout}s. Will retry on next boot.")
          time.sleep(3)
          break

    if sunnylink_dongle_id:
      params.put("SunnylinkDongleId", sunnylink_dongle_id)

    self.spinner = None
    return sunnylink_dongle_id
