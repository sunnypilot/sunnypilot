import base64
import gzip
import json
from sunnypilot.sunnylink.api import SunnylinkApi, UNREGISTERED_SUNNYLINK_DONGLE_ID
from openpilot.common.params import Params, ParamKeyType
from openpilot.system.version import is_prebuilt


def get_sunnylink_status(params=None) -> tuple[bool, bool]:
  """Get the status of Sunnylink on the device. Returns a tuple of (is_sunnylink_enabled, is_registered)."""
  params = params or Params()
  is_sunnylink_enabled = params.get_bool("SunnylinkEnabled")
  is_registered = params.get("SunnylinkDongleId") not in (None, UNREGISTERED_SUNNYLINK_DONGLE_ID)
  return is_sunnylink_enabled, is_registered


def sunnylink_ready(params=None) -> bool:
  """Check if the device is ready to communicate with Sunnylink. That means it is enabled and registered."""
  params = params or Params()
  is_sunnylink_enabled, is_registered = get_sunnylink_status(params)
  return is_sunnylink_enabled and is_registered


def use_sunnylink_uploader(params) -> bool:
  """Check if the device is ready to use Sunnylink and the uploader is enabled."""
  return sunnylink_ready(params) and params.get_bool("EnableSunnylinkUploader")


def sunnylink_need_register(params=None) -> bool:
  """Check if the device needs to be registered with Sunnylink."""
  params = params or Params()
  is_sunnylink_enabled, is_registered = get_sunnylink_status(params)
  return is_sunnylink_enabled and not is_registered


def register_sunnylink():
  """Register the device with Sunnylink if it is enabled."""
  extra_args = {}

  if not Params().get_bool("SunnylinkEnabled"):
    print("Sunnylink is not enabled. Exiting.")
    exit(0)

  if not is_prebuilt():
    extra_args = {
      "verbose": True,
      "timeout": 60
    }

  sunnylink_id = SunnylinkApi(None).register_device(None, **extra_args)
  print(f"SunnyLinkId: {sunnylink_id}")


def get_api_token():
  """Get the API token for the device."""
  params = Params()
  sunnylink_dongle_id = params.get("SunnylinkDongleId")
  sunnylink_api = SunnylinkApi(sunnylink_dongle_id)
  token = sunnylink_api.get_token()
  print(f"API Token: {token}")


def get_param_as_byte(param_name: str, params=None) -> bytes | None:
  """Get a parameter as bytes. Returns None if the parameter does not exist."""
  params = params or Params() # Use existing Params instance if provided
  param = params.get(param_name)
  if param is None:
    return None

  param_type = params.get_type(param_name)
  if param_type == ParamKeyType.BYTES:
    return bytes(param)
  elif param_type == ParamKeyType.JSON:
    return json.dumps(param).encode('utf-8')
  return str(param).encode('utf-8')


def save_param_from_base64_encoded_string(param_name: str, base64_encoded_data: str, is_compressed=False) -> None:
  """Save a parameter from bytes. Overwrites the parameter if it already exists."""
  params = Params()
  # Find real param name (with correct casing)
  param_type = params.get_type(param_name)
  value = base64.b64decode(base64_encoded_data)

  if is_compressed:
    value = gzip.decompress(value)

  # We convert to string anything that isn't bytes first. We later transform further.
  param_value = _convert_param_to_type(value, param_type)
  params.put(param_name, param_value)


def _convert_param_to_type(value: bytes, param_type: ParamKeyType) -> bytes | str | int | float | bool | dict | None:
  """
  Convert a byte value to the specified param type. Used internally when getting a Param to convert it to the right type.
  If this method looks familiar, it's because on SP we have a similar one in openpilot/sunnypilot/car/__init__.py.
  """

  # We convert to string anything that isn't bytes first. We later transform further.
  if param_type != ParamKeyType.BYTES:
    value = value.decode('utf-8')  # type: ignore

  if param_type == ParamKeyType.STRING:
    value = value
  elif param_type == ParamKeyType.BOOL:
    value = value.lower() in ('true', '1', 'yes')  # type: ignore
  elif param_type == ParamKeyType.INT:
    value = int(value)  # type: ignore
  elif param_type == ParamKeyType.FLOAT:
    value = float(value)  # type: ignore
  elif param_type == ParamKeyType.TIME:
    value = str(value)  # type: ignore
  elif param_type == ParamKeyType.JSON:
    value = json.loads(value)

  return value
