import json
from openpilot.sunnypilot.sunnylink.athena.sunnylinkd import getParamsAllKeysV1


def test_get_params_all_keys_v1():
  response = getParamsAllKeysV1()
  assert "keys" in response

  keys_json = response["keys"]
  params_list = json.loads(keys_json)

  assert isinstance(params_list, list)
  assert len(params_list) > 0

  # Check structure of first item
  first_param = params_list[0]
  assert "key" in first_param
  assert "type" in first_param
  assert "default_value" in first_param

  if "_extra" in first_param:
    assert isinstance(first_param["_extra"], dict)
    assert "default" not in first_param["_extra"]
    assert "type" not in first_param["_extra"]

  # Check specific parameter if known
  # e.g. "AccessToken"
  access_token = next((p for p in params_list if p["key"] == "AccessToken"), None)
  assert access_token is not None
  assert "_extra" in access_token
  assert access_token["_extra"]["title"] == "AccessToken"

  # Check rich metadata parameter
  # e.g. "CustomAccIncrementsEnabled"
  custom_acc = next((p for p in params_list if p["key"] == "CustomAccIncrementsEnabled"), None)
  assert custom_acc is not None
  assert "_extra" in custom_acc
  assert custom_acc["_extra"]["title"] == "Custom ACC Increments"
  assert custom_acc["_extra"]["description"] == "Enable custom ACC increments."
