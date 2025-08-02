import os
import sys
import subprocess
from openpilot.common.basedir import BASEDIR

def get_tinygrad_ref():
  repo_path = os.path.join(BASEDIR, "tinygrad_repo")
  try:
    ref = subprocess.check_output([
      "git", "-C", repo_path, "rev-parse", "HEAD"
    ], encoding="utf-8").strip()
    return ref
  except Exception as e:
    print(f"Error getting tinygrad_repo ref: {e}")
    return None

def read_ref_file(ref_file):
  if not os.path.exists(ref_file):
    return None
  with open(ref_file) as f:
    return f.read().strip()

def test_tinygrad_ref():
  ref_file = os.path.join(os.path.dirname(__file__), "tinygrad_ref")
  current_ref = get_tinygrad_ref()
  file_ref = read_ref_file(ref_file)
  if file_ref != current_ref:
    print("tinygrad_repo ref does not match tinygrad_ref file. Please run python3 sunnypilot/models/tinygrad_ref.py to update.")
    sys.exit(1)
  print("tinygrad_repo ref matches tinygrad_ref file.")

if __name__ == "__main__":
  test_tinygrad_ref()
