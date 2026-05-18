"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from enum import IntEnum
import threading
import requests
import time
import json
import pyray as rl

from cereal import messaging
from openpilot.common.params import Params
from openpilot.common.swaglog import cloudlog
from openpilot.sunnypilot.sunnylink.api import UNREGISTERED_SUNNYLINK_DONGLE_ID, SunnylinkApi
from openpilot.system.ui.sunnypilot.lib.styles import style


class RoleType(IntEnum):
  READONLY = 0
  SPONSOR = 1
  ADMIN = 2


class SponsorTier(IntEnum):
  FREE = 0
  NOVICE = 1
  SUPPORTER = 2
  CONTRIBUTOR = 3
  BENEFACTOR = 4
  GUARDIAN = 5


class User:
  device_id: str
  user_id: str
  created_at: int
  updated_at: int
  token_hash: str

  def __init__(self, json_data):
    self.device_id = json_data.get("device_id")
    self.user_id = json_data.get("user_id")
    self.created_at = json_data.get("created_at")
    self.updated_at = json_data.get("updated_at")
    self.token_hash = json_data.get("token_hash")


class Role:
  role_type: str
  role_tier: str

  def __init__(self, json_data):
    self.role_type = json_data.get("role_type")
    self.role_tier = json_data.get("role_tier")


def _parse_roles(roles: str) -> list[Role]:
  lst_roles = []
  try:
    roles_list = json.loads(roles)
    for r in roles_list:
      try:
        role = Role(r)
        lst_roles.append(role)
      except Exception as e:
        cloudlog.exception(f"Failed to parse role {r}: {e}")
    return lst_roles
  except Exception as e:
    cloudlog.exception(f"Error parsing roles: {e}")
    return []


def _parse_users(users: str) -> list[User]:
  lst_users = []
  try:
    users_list = json.loads(users)
    for u in users_list:
      try:
        user = User(u)
        lst_users.append(user)
      except Exception as e:
        cloudlog.exception(f"Failed to parse user {u}: {e}")
    return lst_users
  except Exception as e:
    cloudlog.exception(f"Error parsing users: {e}")
    return []


class SunnylinkState:
  FETCH_INTERVAL = 5.0  # seconds between API calls
  API_TIMEOUT = 10.0  # seconds for API requests
  SLEEP_INTERVAL = 0.5  # seconds to sleep between checks in the worker thread
  NOT_PAIRED_USERNAMES = ["unregisteredsponsor", "temporarysponsor"]

  def __init__(self):
    self._params = Params()
    self._lock = threading.Lock()
    self._session = requests.Session()  # reuse session to reduce SSL handshake overhead
    self._running = False
    self._thread = None
    self._sm = messaging.SubMaster(['deviceState'])

    self._roles: list[Role] = []
    self._users: list[User] = []
    self.sponsor_tier: SponsorTier = SponsorTier.FREE
    self.sunnylink_dongle_id = self._params.get("SunnylinkDongleId")
    self._api = SunnylinkApi(self.sunnylink_dongle_id)

    self._panel_open = False

    self._load_initial_state()

  def _load_initial_state(self) -> None:
    roles_cache = self._params.get("SunnylinkCache_Roles")
    users_cache = self._params.get("SunnylinkCache_Users")
    if roles_cache is not None:
      self._roles = _parse_roles(roles_cache)
      self.sponsor_tier = self._get_highest_tier()
    if users_cache is not None:
      self._users = _parse_users(users_cache)

  def _get_highest_tier(self) -> SponsorTier:
    role_tier = SponsorTier.FREE
    for role in self._roles:
      try:
        if RoleType[role.role_type.upper()] == RoleType.SPONSOR:
          role_tier = max(role_tier, SponsorTier[role.role_tier.upper()])
      except Exception as e:
        cloudlog.exception(f"Error parsing role {role}: {e} for dongle id {self.sunnylink_dongle_id}")
    return role_tier

  def _fetch_roles(self) -> None:
    if not self.sunnylink_dongle_id or self.sunnylink_dongle_id == UNREGISTERED_SUNNYLINK_DONGLE_ID:
      return

    try:
      token = self._api.get_token()
      response = self._api.api_get(f"device/{self.sunnylink_dongle_id}/roles", method='GET', access_token=token, session=self._session)
      if response.status_code == 200:
        roles = response.text
        self._params.put("SunnylinkCache_Roles", roles)
        with self._lock:
          self._roles = _parse_roles(roles)
          sponsor_tier = self._get_highest_tier()
          if sponsor_tier != self.sponsor_tier:
            self.sponsor_tier = sponsor_tier
            cloudlog.info(f"Sunnylink sponsor tier updated to {sponsor_tier.name}")
    except Exception as e:
      cloudlog.exception(f"Failed to fetch sunnylink roles: {e} for dongle id {self.sunnylink_dongle_id}")

  def _fetch_users(self) -> None:
    if not self.sunnylink_dongle_id or self.sunnylink_dongle_id == UNREGISTERED_SUNNYLINK_DONGLE_ID:
      return

    try:
      token = self._api.get_token()
      response = self._api.api_get(f"device/{self.sunnylink_dongle_id}/users", method='GET', access_token=token, session=self._session)
      if response.status_code == 200:
        users = response.text
        self._params.put("SunnylinkCache_Users", users)
        with self._lock:
          self._users = _parse_users(users)
    except Exception as e:
      cloudlog.exception(f"Failed to fetch sunnylink users: {e} for dongle id {self.sunnylink_dongle_id}")

  def _worker_thread(self) -> None:
    while self._running:
      with self._lock:
        panel_open = self._panel_open

      if panel_open:
        self._sm.update()
        if self.is_connected():
          self._fetch_roles()
          self._fetch_users()

      for _ in range(int(self.FETCH_INTERVAL / self.SLEEP_INTERVAL)):
        if not self._running:
          break
        time.sleep(self.SLEEP_INTERVAL)

  def start(self) -> None:
    if self._thread and self._thread.is_alive():
      return
    self._running = True
    self._thread = threading.Thread(target=self._worker_thread, daemon=True)
    self._thread.start()

  def stop(self) -> None:
    self._running = False
    if self._thread and self._thread.is_alive():
      self._thread.join(timeout=1.0)

  def get_sponsor_tier(self) -> SponsorTier:
    with self._lock:
      return self.sponsor_tier

  def is_sponsor(self) -> bool:
    with self._lock:
      is_sponsor = any(role.role_type.upper() == RoleType.SPONSOR.name and role.role_tier.upper() != SponsorTier.FREE.name
                       for role in self._roles)
      return is_sponsor

  def is_paired(self) -> bool:
    with self._lock:
      is_paired = any(user.user_id not in self.NOT_PAIRED_USERNAMES for user in self._users)
      return is_paired

  def is_connected(self) -> bool:
    network_type = self._sm["deviceState"].networkType
    return bool(network_type != 0)

  def get_sponsor_tier_color(self) -> rl.Color:
    tier = self.get_sponsor_tier()

    if tier == SponsorTier.GUARDIAN:
      return rl.Color(255, 215, 0, 255)
    elif tier == SponsorTier.BENEFACTOR:
      return rl.Color(60, 179, 113, 255)
    elif tier == SponsorTier.CONTRIBUTOR:
      return rl.Color(70, 130, 180, 255)
    elif tier == SponsorTier.SUPPORTER:
      return rl.Color(147, 112, 219, 255)
    else:
      return style.ITEM_TEXT_VALUE_COLOR

  def set_settings_open(self, _open: bool) -> None:
    with self._lock:
      self._panel_open = _open

  def __del__(self):
    self.stop()
