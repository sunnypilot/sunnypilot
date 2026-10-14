#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import os
os.environ["GMMU"] = "0"
import argparse
import hashlib
import json
import multiprocessing
import shutil
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

import requests

from openpilot.sunnypilot.modeld_v2.helpers import load_model, tinygrad_identity
from openpilot.sunnypilot.models.fetcher import ModelFetcher


def _download(url: str, path: str, sha256: str) -> bool:
  digest = hashlib.sha256()
  with requests.get(url, stream=True, timeout=60) as response, open(path, "wb") as file:
    response.raise_for_status()
    for chunk in response.iter_content(chunk_size=16 << 20):
      file.write(chunk)
      digest.update(chunk)
  return digest.hexdigest() == sha256


def main():
  parser = argparse.ArgumentParser(description="Build the chestnut boot caches for every chestnut model in the registry")
  parser.add_argument("--work-dir", required=True, help="where models are downloaded, two at most, emptied when done")
  parser.add_argument("--upload-dir", required=True, help="caches laid out like the huggingface repo, for one hf upload")
  parser.add_argument("--docs-dir", required=True, help="a gh-pages checkout of the registry repo: its docs/caches/<tinygrad identity>.json is updated")
  args = parser.parse_args()

  identity, spawn = tinygrad_identity(), multiprocessing.get_context("spawn")
  manifest_path = os.path.join(args.docs_dir, "docs", "caches", f"{identity}.json")
  manifest = json.load(open(manifest_path)) if os.path.isfile(manifest_path) else {}  # caches already built for this tinygrad are kept
  registry = json.load(open(os.path.join(args.docs_dir, "docs", os.path.basename(ModelFetcher.MODEL_URL_CHESTNUT))))
  artifacts = {model["artifact"]["file_name"]: model["artifact"]["download_uri"] for bundle in registry["bundles"]
               for model in bundle.get("models", []) if "artifact" in model}
  todo = [(name, uri) for name, uri in artifacts.items() if name not in manifest]
  os.makedirs(args.work_dir, exist_ok=True)
  with ThreadPoolExecutor(max_workers=1) as pool:
    def fetch(index):
      return pool.submit(_download, todo[index][1]["url"], os.path.join(args.work_dir, todo[index][0]), todo[index][1]["sha256"]) if index < len(todo) else None
    pending = fetch(0)
    try:
      for index, (name, uri) in enumerate(todo):
        downloaded, pending, path = pending, fetch(index + 1), os.path.join(args.work_dir, name)
        try:
          if not downloaded.result():
            print(f"skipping {name}: hash mismatch")
            continue
          (worker := spawn.Process(target=load_model, args=(path,))).start()
          worker.join()
          if worker.exitcode != 0 or not os.path.isfile(f"{path}.cache"):
            print(f"skipping {name}: load failed with exit code {worker.exitcode}")
            continue
          repo_path = urllib.parse.unquote(urllib.parse.urlparse(uri["url"]).path.split("/resolve/main/", 1)[1]) + f".{identity[:16]}.cache"
          os.makedirs(os.path.dirname(destination := os.path.join(args.upload_dir, repo_path)), exist_ok=True)
          shutil.move(f"{path}.cache", destination)
          with open(destination, "rb") as file:
            manifest[name] = {"url": uri["url"] + f".{identity[:16]}.cache", "sha256": hashlib.sha256(file.read()).hexdigest()}
          print(f"built {name}")
        except Exception as e:
          print(f"skipping {name}: {e}")
        finally:
          for leftover in (path, f"{path}.cache"):
            if os.path.exists(leftover):
              os.remove(leftover)
    finally:
      if pending is not None:
        pending.cancel()
      pool.shutdown(wait=True)
      shutil.rmtree(args.work_dir, ignore_errors=True)

  os.makedirs(os.path.dirname(manifest_path), exist_ok=True)
  with open(manifest_path, "w") as file:
    json.dump(manifest, file, indent=2, sort_keys=True)
  print(f"{len(manifest.keys() & artifacts.keys())}/{len(artifacts)} chestnut caches for tinygrad {identity}")


if __name__ == "__main__":
  main()
