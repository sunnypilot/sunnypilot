#!/usr/bin/env python3
"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import argparse
import hashlib
import json
import tempfile

from huggingface_hub import HfApi, hf_hub_download


def hash_file(path: str) -> str:
  digest = hashlib.sha256()
  with open(path, 'rb') as f:
    while block := f.read(1024 * 1024):
      digest.update(block)
  return digest.hexdigest()


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("--hf-repo", required=True)
  parser.add_argument("--hf-defaults-path", required=True)
  parser.add_argument("--artifact-name", required=True)
  parser.add_argument("--model-dir", required=True)
  parser.add_argument("--onnx-path", required=True)
  parser.add_argument("--onnx-ref", required=True)
  parser.add_argument("--model-name", required=True)
  parser.add_argument("--tinygrad-ref", required=True)
  parser.add_argument("--run-number", required=True)
  args = parser.parse_args()

  api = HfApi()
  onnx_sha256 = hash_file(args.onnx_path)
  short_ref = args.onnx_ref[:8]
  safe_name = args.model_name.replace(" ", "-")
  folder_name = f"model-{safe_name}-{short_ref}-{args.run_number}"

  print(f"ONNX hash: {onnx_sha256}")
  print(f"ONNX ref: {args.onnx_ref} (short: {short_ref})")
  print(f"Folder: {folder_name}")

  metadata_path = f"{args.model_dir}/metadata.json"
  with open(metadata_path) as f:
    metadata = json.load(f)

  bundle = metadata['bundles'][0]
  bundle['display_name'] = args.model_name
  bundle['onnx_sha256'] = onnx_sha256
  bundle['onnx_ref'] = args.onnx_ref

  artifact = bundle['models'][0]['artifact']
  hf_base = f"https://huggingface.co/datasets/{args.hf_repo}/resolve/main/{args.hf_defaults_path}/{folder_name}"
  artifact['download_uri']['url'] = f"{hf_base}/{artifact['file_name']}"
  for chunk in artifact.get('chunks', []):
    chunk['url'] = f"{hf_base}/{chunk['file_name']}"

  print(f"Uploading model to {args.hf_defaults_path}/{folder_name}/")
  api.upload_folder(
    folder_path=args.model_dir,
    path_in_repo=f"{args.hf_defaults_path}/{folder_name}",
    repo_id=args.hf_repo,
    repo_type="dataset",
  )

  json_filename = f"{args.hf_defaults_path}/default_models.json"
  try:
    local_path = hf_hub_download(repo_id=args.hf_repo, repo_type='dataset', filename=json_filename)
    with open(local_path) as f:
      defaults_json = json.load(f)
  except Exception:
    defaults_json = {"tinygrad_ref": args.tinygrad_ref, "bundles": []}

  defaults_json['tinygrad_ref'] = args.tinygrad_ref

  existing_idx = next((i for i, b in enumerate(defaults_json['bundles'])
                       if b.get('onnx_sha256') == onnx_sha256), None)
  if existing_idx is not None:
    defaults_json['bundles'][existing_idx] = bundle
  else:
    defaults_json['bundles'].append(bundle)

  print(json.dumps(defaults_json, indent=2))

  with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(defaults_json, f, indent=2)
    tmp_path = f.name

  api.upload_file(
    path_or_fileobj=tmp_path,
    path_in_repo=json_filename,
    repo_id=args.hf_repo,
    repo_type="dataset",
  )

  print(f"Updated {json_filename}")


if __name__ == "__main__":
  main()
