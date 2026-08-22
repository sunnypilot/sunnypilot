#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import urllib.request
from datetime import datetime, UTC
from pathlib import Path


def hash_file(path: str) -> str:
  digest = hashlib.sha256()
  with open(path, 'rb') as f:
    while block := f.read(1024 * 1024):
      digest.update(block)
  return digest.hexdigest()


def fetch_catalog(catalog_url: str) -> dict:
  with urllib.request.urlopen(catalog_url) as resp:
    return json.loads(resp.read())


def find_default_bundle(catalog: dict, default_name: str) -> dict | None:
  for bundle in catalog.get('bundles', []):
    if bundle.get('display_name', '').startswith(default_name):
      return bundle
  return None


def _collect_local_chunks(model_dir: Path) -> tuple[list[dict], str, int]:
  canonical_name = "big_driving_tinygrad.pkl"
  chunk_files = sorted(model_dir.glob("*.chunk*"))
  if not chunk_files:
    chunk_files = sorted(model_dir.glob("driving_*_tinygrad.pkl.chunk*"))

  chunks = []
  for f in chunk_files:
    if f.suffix == '.chunkmanifest':
      continue
    name = f.name
    canonical = re.sub(r'driving_.*_tinygrad', 'big_driving_tinygrad', name)
    chunks.append({"file_name": canonical, "sha256": hash_file(str(f)), "src": str(f)})

  num_chunks = len(chunks)

  # hash all chunks together for the full pkl hash
  digest = hashlib.sha256()
  for c in chunks:
    with open(c['src'], 'rb') as fh:
      while block := fh.read(1024 * 1024):
        digest.update(block)
  pkl_sha256 = digest.hexdigest()

  return chunks, pkl_sha256, num_chunks


def _prepare_from_catalog(args, onnx_hash: str) -> tuple[str, dict]:
  catalog = fetch_catalog(args.catalog_url)
  tinygrad_ref = catalog.get('tinygrad_ref', '')
  print(f"Catalog tinygrad_ref: {tinygrad_ref}")

  bundle = find_default_bundle(catalog, args.default_name)
  if not bundle:
    print(f"No bundle found starting with '{args.default_name}'", file=sys.stderr)
    sys.exit(1)

  print(f"Found bundle: {bundle['display_name']} (ref={bundle.get('ref', '?')})")

  artifact = bundle['models'][0]['artifact']
  source_chunks = artifact.get('chunks', [])
  source_url = artifact['download_uri']['url']
  pkl_sha256 = artifact['download_uri']['sha256']

  canonical_name = "big_driving_tinygrad.pkl"
  num_chunks = len(source_chunks)

  tmpdir = tempfile.mkdtemp()
  big_dir = os.path.join(tmpdir, "big")
  os.makedirs(big_dir)

  chunk_hashes = []
  for i, chunk in enumerate(source_chunks):
    src_chunk_name = chunk['file_name']
    canonical_chunk = f"{canonical_name}.chunk{i+1:02d}of{num_chunks:02d}"
    chunk_url = source_url.rsplit('/', 1)[0] + '/' + src_chunk_name
    dest_path = os.path.join(big_dir, canonical_chunk)

    print(f"  {src_chunk_name} -> {canonical_chunk}")
    if not args.dry_run:
      urllib.request.urlretrieve(chunk_url, dest_path)
      actual_hash = hash_file(dest_path)
      if actual_hash != chunk['sha256']:
        print(f"  Hash mismatch for {canonical_chunk}", file=sys.stderr)
        sys.exit(1)
      chunk_hashes.append({"file_name": canonical_chunk, "sha256": actual_hash})
    else:
      chunk_hashes.append({"file_name": canonical_chunk, "sha256": chunk['sha256']})

  manifest = {
    "big": {
      "name": args.default_name,
      "onnx_sha256": onnx_hash,
      "tinygrad_ref": tinygrad_ref,
      "source_ref": bundle.get('ref', ''),
      "artifact": {
        "file_name": canonical_name,
        "sha256": pkl_sha256,
        "num_chunks": num_chunks,
        "chunks": chunk_hashes
      },
      "updated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
  }

  return big_dir, manifest


def _prepare_from_local(args, onnx_hash: str) -> tuple[str, dict]:
  model_dir = Path(args.model_dir)
  chunks, pkl_sha256, num_chunks = _collect_local_chunks(model_dir)

  if not chunks:
    print(f"No chunk files found in {model_dir}", file=sys.stderr)
    sys.exit(1)

  canonical_name = "big_driving_tinygrad.pkl"
  tmpdir = tempfile.mkdtemp()
  big_dir = os.path.join(tmpdir, "big")
  os.makedirs(big_dir)

  chunk_hashes = []
  for c in chunks:
    dest = os.path.join(big_dir, c['file_name'])
    os.link(c['src'], dest) if not args.dry_run else None
    chunk_hashes.append({"file_name": c['file_name'], "sha256": c['sha256']})

  tinygrad_ref = args.tinygrad_ref or ''

  manifest = {
    "big": {
      "name": args.default_name,
      "onnx_sha256": onnx_hash,
      "tinygrad_ref": tinygrad_ref,
      "source_ref": "",
      "artifact": {
        "file_name": canonical_name,
        "sha256": pkl_sha256,
        "num_chunks": num_chunks,
        "chunks": chunk_hashes
      },
      "updated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    }
  }

  return big_dir, manifest


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--onnx-path", required=True)
  parser.add_argument("--model-dir", help="Local directory with compiled model chunks (skips catalog)")
  parser.add_argument("--tinygrad-ref", help="Tinygrad ref (used with --model-dir)")
  parser.add_argument("--catalog-url", default="https://raw.githubusercontent.com/sunnypilot/sunnypilot-models/refs/heads/gh-pages/docs/driving_models_usbgpu_v21.json")
  parser.add_argument("--default-name", default="Lebowski")
  parser.add_argument("--hf-repo", default="sunnypilot/sunnypilot_models_v1")
  parser.add_argument("--dry-run", action="store_true")
  args = parser.parse_args()

  onnx_hash = hash_file(args.onnx_path)
  print(f"ONNX hash: {onnx_hash}")

  if args.model_dir:
    big_dir, manifest = _prepare_from_local(args, onnx_hash)
  else:
    big_dir, manifest = _prepare_from_catalog(args, onnx_hash)

  manifest_path = os.path.join(os.path.dirname(big_dir), "manifest.json")
  with open(manifest_path, 'w') as f:
    json.dump(manifest, f, indent=2)

  print(json.dumps(manifest, indent=2))

  if args.dry_run:
    print("[DRY RUN]")
    return

  try:
    from huggingface_hub import HfApi
  except ImportError:
    print("pip install huggingface_hub", file=sys.stderr)
    sys.exit(1)

  api = HfApi()

  api.upload_file(
    path_or_fileobj=manifest_path,
    path_in_repo="models/defaults/manifest.json",
    repo_id=args.hf_repo,
    repo_type="dataset",
  )

  api.upload_folder(
    folder_path=big_dir,
    path_in_repo="models/defaults/big",
    repo_id=args.hf_repo,
    repo_type="dataset",
  )

  print("Done.")


if __name__ == "__main__":
  main()
