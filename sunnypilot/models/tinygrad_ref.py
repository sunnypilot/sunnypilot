import os
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

def write_ref_file(ref_file, ref):
  with open(ref_file, "w") as f:
    f.write(ref + "\n")

def main():
  ref_file = os.path.join(os.path.dirname(__file__), "tests", "tinygrad_ref")
  current_ref = get_tinygrad_ref()
  if not current_ref:
    print("Could not determine tinygrad_repo ref.")
    return
  file_ref = read_ref_file(ref_file)
  if file_ref != current_ref:
    print(f"Updating tinygrad_ref file: {file_ref} -> {current_ref}")
    write_ref_file(ref_file, current_ref)
  else:
    print("tinygrad_ref is up to date.")

if __name__ == "__main__":
  main()
