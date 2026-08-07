#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import argparse
import os
import re

from openpilot.sunnypilot import get_file_hash
from openpilot.common.basedir import BASEDIR
from openpilot.sunnypilot.mapd import MAPD_PATH

MAPD_HASH_PATH = os.path.join(BASEDIR, "sunnypilot", "mapd", "tests", "mapd_hash")
MAPD_VERSION_PATH = os.path.join(BASEDIR, "sunnypilot", "mapd", "mapd_installer.py")


def update_mapd_hash():
  mapd_hash = get_file_hash(MAPD_PATH)

  with open(MAPD_HASH_PATH, "w") as f:
    f.write(mapd_hash)

  print(f"Generated and updated new mapd hash to {MAPD_HASH_PATH}")


def get_current_mapd_version(path: str) -> str:
  print("[GET CURRENT MAPD VERSION]")
  with open(path) as f:
    for line in f:
      if line.strip().startswith("VERSION"):
        # Match VERSION = 'v1.11.0' or VERSION="v1.11.0" (with optional spaces)
        match = re.search(r'VERSION\s*=\s*[\'"]([^\'"]+)[\'"]', line)
        if match:
          ver = match.group(1)
          print(f'Current mapd version: "{ver}"')
          return ver
        else:
          print("[ERROR] VERSION line found but no quoted value detected.")
          return ""
  print("[ERROR] VERSION not found in file!")
  return ""


def update_mapd_version(ver: str, path: str):
  print("[CHANGE CURRENT MAPD VERSION]")

  with open(path) as f:
    lines = f.readlines()

  found = False
  new_lines = []
  for line in lines:
    if not found and line.startswith("VERSION ="):
      new_lines.append(f'VERSION = "{ver}"\n')
      found = True
      new_lines.extend(lines[lines.index(line) + 1:])
      break
    else:
      new_lines.append(line)

  if not found:
    print("[ERROR] VERSION line not found! Aborting without writing.")
    return

  with open(path, "w") as f:
    f.writelines(new_lines)

  print(f'New mapd version: "{ver}"')
  print("[DONE]")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Update mapd version and hash")
  parser.add_argument("--new_ver", type=str, help="New mapd version")
  args = parser.parse_args()

  if not args.new_ver:
    print("Warning: No new mapd version provided. Use --new_ver to specify")
    print("Example:")
    print("  python sunnypilot/mapd/update_version.py --new_ver \"v1.12.0\"")
    print("Current mapd version and hash will not be updated! (aborted)")
    exit(0)

  current_ver = get_current_mapd_version(MAPD_VERSION_PATH)
  new_ver = f"{args.new_ver}"
  if current_ver == new_ver:
    print(f'Proposed mapd version: "{new_ver}"')
    confirm = input("Proposed mapd version is the same as the current mapd version. Confirm? (y/n): ").upper().strip()
    if confirm != "Y":
      print("Current mapd version and hash will not be updated! (aborted)")
      exit(0)

  update_mapd_version(new_ver, MAPD_VERSION_PATH)
  update_mapd_hash()
