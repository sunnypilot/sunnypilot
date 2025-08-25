import requests

from sunnypilot.models.tinygrad_ref import get_tinygrad_ref
from sunnypilot.models.fetcher import ModelFetcher


def fetch_tinygrad_ref():
  response = requests.get(ModelFetcher.MODEL_URL, timeout=10)
  response.raise_for_status()
  json_data = response.json()
  return json_data.get("tinygrad_ref")


def test_tinygrad_ref():
  current_ref = get_tinygrad_ref()
  remote_ref = fetch_tinygrad_ref()
  assert remote_ref == current_ref, (
    f"""tinygrad_repo ref does not match remote tinygrad_ref of current compiled driving models json.
  Current: {current_ref}
  Remote: {remote_ref}
  Please run build-all workflow to update models."""
  )
  print("tinygrad_repo ref matches current compiled driving models json ref.")
