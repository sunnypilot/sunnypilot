import os
from sunnypilot.models.tinygrad_ref import get_tinygrad_ref, read_ref_file


def test_tinygrad_ref():
  ref_file = os.path.join(os.path.dirname(__file__), "tinygrad_ref")
  current_ref = get_tinygrad_ref()
  file_ref = read_ref_file(ref_file)
  assert file_ref == current_ref, (
    "tinygrad_repo ref does not match tinygrad_ref file. Please run python3 sunnypilot/models/tinygrad_ref.py to update."
  )
  print("tinygrad_repo ref matches tinygrad_ref file.")

if __name__ == "__main__":
  test_tinygrad_ref()
