import jwt
import os
import requests
import unicodedata
from datetime import datetime, timedelta, UTC
from openpilot.system.hardware.hw import Paths
from openpilot.system.version import get_version

# name: jwt signature algorithm
KEYS = {"id_rsa": "RS256",
        "id_ecdsa": "ES256"}


class BaseApi:
  def __init__(self, dongle_id, api_host, user_agent="openpilot-"):
    self.dongle_id = dongle_id
    self.api_host = api_host
    self.user_agent = user_agent
    self.jwt_algorithm, self.private_key, _ = self.get_key_pair()

  def get(self, *args, **kwargs):
    return self.request('GET', *args, **kwargs)

  def post(self, *args, **kwargs):
    return self.request('POST', *args, **kwargs)

  def request(self, method, endpoint, timeout=None, access_token=None, **params):
    return self.api_get(endpoint, method=method, timeout=timeout, access_token=access_token, **params)

  def _get_token(self, payload_extra=None, expiry_hours=1, **extra_payload):
    now = datetime.now(UTC).replace(tzinfo=None)
    payload = {
      'identity': self.dongle_id,
      'nbf': now,
      'iat': now,
      'exp': now + timedelta(hours=expiry_hours),
      **extra_payload
    }
    if payload_extra is not None:
      payload.update(payload_extra)
    token = jwt.encode(payload, self.private_key, algorithm=self.jwt_algorithm)
    if isinstance(token, bytes):
      token = token.decode('utf8')
    return token

  def get_token(self, payload_extra=None, expiry_hours=1):
    return self._get_token(payload_extra, expiry_hours)

  def remove_non_ascii_chars(self, text):
    normalized_text = unicodedata.normalize('NFD', text)
    ascii_encoded_text = normalized_text.encode('ascii', 'ignore')
    return ascii_encoded_text.decode()

  def api_get(self, endpoint, method='GET', timeout=None, access_token=None, session=None, json=None, **params):
    headers = {}
    if access_token is not None:
      headers['Authorization'] = "JWT " + access_token

    version = self.remove_non_ascii_chars(get_version())
    headers['User-Agent'] = self.user_agent + version

    # TODO: add session to Api
    req = requests if session is None else session
    return req.request(method, f"{self.api_host}/{endpoint}", timeout=timeout, headers=headers, json=json, params=params)

  @staticmethod
  def get_key_pair() -> tuple[str, str, str] | tuple[None, None, None]:
    for key in KEYS:
      if os.path.isfile(Paths.persist_root() + f'/comma/{key}') and os.path.isfile(Paths.persist_root() + f'/comma/{key}.pub'):
        with open(Paths.persist_root() + f'/comma/{key}') as private, open(Paths.persist_root() + f'/comma/{key}.pub') as public:
          return KEYS[key], private.read(), public.read()
    return None, None, None
