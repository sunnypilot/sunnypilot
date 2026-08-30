#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import os
import tempfile

import requests
from huggingface_hub import HfApi
from tqdm import tqdm

from openpilot.tools.lib.route import Route

REPO_ID = os.environ.get("SUNNYPILOT_CAR_SEGMENTS_REPO_ID", "sunnypilot/sunnypilotCarSegments")


def upload_route(route_name: str, dry_run: bool = False) -> None:
  route = Route(route_name)
  log_paths = route.log_paths()
  valid_segments = [(i, url) for i, url in enumerate(log_paths) if url is not None]

  print(f"Route: {route_name}")
  print(f"Segments: {len(valid_segments)}/{len(log_paths)}")

  if not valid_segments:
    print("No segments found.")
    return

  api = HfApi()

  with tempfile.TemporaryDirectory() as tmpdir:
    for seg_idx, url in tqdm(valid_segments, desc="Uploading"):
      filename = url.split("?")[0].rsplit("/", 1)[-1]
      local_path = os.path.join(tmpdir, f"{seg_idx}_{filename}")
      resp = requests.get(url, stream=True)
      resp.raise_for_status()
      with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
          f.write(chunk)

      repo_path = f"segments/{route_name.replace('|', '/')}/{seg_idx}/{filename}"

      if dry_run:
        size_mb = os.path.getsize(local_path) / 1024 / 1024
        print(f"  [{seg_idx}] {size_mb:.1f} MB -> {repo_path}")
      else:
        api.upload_file(
          path_or_fileobj=local_path,
          path_in_repo=repo_path,
          repo_id=REPO_ID,
          repo_type="dataset",
        )

  print("Done.")


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Upload route rlogs to sunnypilot HuggingFace dataset")
  parser.add_argument("route", help="Route ID (e.g. 5beb9b58bd12b691/0000010a--a51155e496)")
  parser.add_argument("--dry-run", action="store_true", help="Download and show sizes without uploading")
  args = parser.parse_args()

  upload_route(args.route, dry_run=args.dry_run)
