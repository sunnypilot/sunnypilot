from openpilot.common.api.comma_connect import CommaConnectApi


class Api:
  def __init__(self, dongle_id):
    self.service = CommaConnectApi(dongle_id)

  def request(self, method, endpoint, **params):
    return self.service.request(method, endpoint, **params)

  def get(self, *args, **kwargs):
    return self.service.get(*args, **kwargs)

  def post(self, *args, **kwargs):
    return self.service.post(*args, **kwargs)

  def get_token(self, payload_extra=None, expiry_hours=1):
    return self.service.get_token(payload_extra, expiry_hours)


def api_get(endpoint, method='GET', timeout=None, access_token=None, session=None, **params):
  return CommaConnectApi(None).api_get(endpoint, method, timeout, access_token, session, **params)


def get_key_pair() -> tuple[str, str, str] | tuple[None, None, None]:
  return CommaConnectApi(None).get_key_pair()
