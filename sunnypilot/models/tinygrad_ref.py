import os
from openpilot.common.basedir import BASEDIR


def get_tinygrad_ref():
  repo_path = os.path.join(BASEDIR, "tinygrad_repo")
  git_path = os.path.join(repo_path, ".git")
  try:
    if os.path.isdir(git_path):
      git_dir = git_path
    else:
      with open(git_path) as f:
        line = f.read().strip()
      git_dir = os.path.join(repo_path, line[8:])
    with open(os.path.join(git_dir, "HEAD")) as f:
      ref = f.read().strip()
    if ref.startswith("ref:"):
      with open(os.path.join(git_dir, ref.split(" ", 1)[1])) as f:
        return f.read().strip()
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
  ref_file = os.path.join(os.path.dirname(__file__), "tinygrad_ref")
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
