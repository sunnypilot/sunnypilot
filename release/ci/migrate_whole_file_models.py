#!/usr/bin/env python3
"""One-off migration of a chunked driving_models manifest to whole files (selector version 20).

For every model in the source manifest the .chunkNNofMM files are downloaded, joined and checked
against download_uri.sha256, which has always been the hash of the whole file. The whole pkl is
uploaded beside its chunks and HuggingFace's stored LFS hash is compared with the manifest before
the entry is accepted. The target manifest is the source with the chunk lists dropped, the model
type set and the selector version bumped; nothing else moves. Old clients keep reading the source
manifest and its chunks.

Rerunnable: a model whose whole file is already stored with the right hash is not transferred
again. The target manifest is only written when every selected model migrated, so it never lists
a model that cannot be downloaded.

Delete this script and its workflow once the catalog is on whole files.
"""
import argparse
import hashlib
import json
import posixpath
import re
import shutil
import sys
import tempfile
import time
import urllib.parse
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from huggingface_hub import HfApi
from huggingface_hub import constants as hf_constants
from huggingface_hub.utils import disable_progress_bars

RESOLVE = "/resolve/main/"
DOWNLOAD_ATTEMPTS = 3
BLOCK = 1 << 20


def repo_path(url: str) -> str:
  """'https://huggingface.co/datasets/o/n/resolve/main/models/x/y.pkl' -> 'models/x/y.pkl' (unquoted)."""
  path = urllib.parse.urlparse(url).path
  if RESOLVE not in path:
    raise ValueError(f"not a HuggingFace resolve URL: {url}")
  return urllib.parse.unquote(path.split(RESOLVE, 1)[1])


def dest_url(hf_repo: str, path: str) -> str:
  # the same quoting as make_model_url in the docs repo's json_parser.py: each path segment on its own
  quoted = "/".join(urllib.parse.quote(segment) for segment in path.split("/"))
  return f"{hf_constants.ENDPOINT}/datasets/{hf_repo}{RESOLVE}{quoted}"


def chunk_urls(artifact: dict) -> list[str]:
  folder = posixpath.dirname(artifact["download_uri"]["url"])
  return [f"{folder}/{urllib.parse.quote(chunk['file_name'])}" for chunk in artifact["chunks"]]


def download(session: requests.Session, url: str, dest: Path, expected_sha256: str) -> None:
  """Stream url to dest, retried on transport errors and on a hash mismatch."""
  last: Exception | None = None
  for attempt in range(DOWNLOAD_ATTEMPTS):
    try:
      digest = hashlib.sha256()
      with session.get(url, stream=True, timeout=60) as response, open(dest, "wb") as f:
        response.raise_for_status()
        for block in response.iter_content(BLOCK):
          f.write(block)
          digest.update(block)
      if digest.hexdigest() != expected_sha256:
        raise ValueError(f"sha256 mismatch for {url}")
      return
    except (requests.RequestException, ValueError) as e:
      last = e
      time.sleep(2 * (attempt + 1))
  raise RuntimeError(f"giving up on {url}: {last}")


def join_chunks(chunks: list[Path], whole: Path) -> str:
  digest = hashlib.sha256()
  with open(whole, "wb") as out:
    for chunk in chunks:
      with open(chunk, "rb") as f:
        for block in iter(lambda: f.read(BLOCK), b""):
          out.write(block)
          digest.update(block)
  return digest.hexdigest()


def stored_file(api: HfApi, hf_repo: str, path: str) -> tuple[str, int] | None:
  """(sha256, size) of the LFS object HuggingFace holds at path, None when absent."""
  for entry in api.get_paths_info(hf_repo, [path], repo_type="dataset"):
    lfs = getattr(entry, "lfs", None)
    sha256 = getattr(lfs, "sha256", None) if lfs is not None else None
    if sha256:
      return sha256, int(entry.size)
  return None


def range_probe(session: requests.Session, url: str, size: int) -> None:
  """The client fetches whole files as byte ranges, so the stored file must answer one."""
  with session.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=30) as response:
    total = response.headers.get("Content-Range", "").rpartition("/")[2]
    if response.status_code != 206 or total != str(size):
      raise RuntimeError(f"{url}: HTTP {response.status_code}, Content-Range total {total!r}; expected 206 and {size}")


def migrate_artifact(api: HfApi, session: requests.Session, hf_repo: str, name: str, artifact: dict,
                     work_dir: Path, workers: int, dry_run: bool) -> tuple[str, int, str]:
  """Make sure the whole file for artifact is stored under hf_repo with the manifest's hash.
  Returns (url, size, outcome) with outcome one of 'kept', 'uploaded', 'verified (dry run)'."""
  expected = artifact["download_uri"]["sha256"]
  path = repo_path(artifact["download_uri"]["url"])
  url = dest_url(hf_repo, path)

  stored = stored_file(api, hf_repo, path)
  if stored is not None and stored[0] == expected:
    range_probe(session, url, stored[1])
    return url, stored[1], "kept"
  if not artifact.get("chunks"):
    raise RuntimeError(f"{name}: no chunks to join and no whole file with hash {expected} stored at {path}")

  model_dir = Path(tempfile.mkdtemp(prefix="model-", dir=work_dir))
  try:
    chunk_paths = [model_dir / chunk["file_name"] for chunk in artifact["chunks"]]
    with ThreadPoolExecutor(max_workers=workers) as pool:
      list(pool.map(lambda job: download(session, *job),
                    zip(chunk_urls(artifact), chunk_paths, [chunk["sha256"] for chunk in artifact["chunks"]], strict=True)))
    whole = model_dir / posixpath.basename(path)
    joined = join_chunks(chunk_paths, whole)
    for chunk_path in chunk_paths:
      chunk_path.unlink()
    if joined != expected:
      raise RuntimeError(f"{name}: joined chunks hash to {joined}, manifest says {expected}")
    size = whole.stat().st_size
    if dry_run:
      return url, size, "verified (dry run)"

    api.upload_file(path_or_fileobj=str(whole), path_in_repo=path, repo_id=hf_repo, repo_type="dataset",
                    commit_message=f"Whole file for {name}: {posixpath.basename(path)}")
  finally:
    shutil.rmtree(model_dir, ignore_errors=True)

  stored = stored_file(api, hf_repo, path)
  if stored is None or stored[0] != expected:
    raise RuntimeError(f"{name}: HuggingFace holds {stored} at {path} after upload, expected hash {expected}")
  range_probe(session, url, size)
  return url, size, "uploaded"


def migrate_manifest(src: dict, *, hf_repo: str, api: HfApi, session: requests.Session, selector_version: int, model_type: str,
                     only: set[str] | None = None, limit: int | None = None, workers: int = 8, work_dir: Path | None = None,
                     dry_run: bool = False, log: Callable[[str], None] = lambda line: print(line, flush=True)) -> dict:
  """The whole-file manifest for src. Raises before anything is written if a model cannot be migrated."""
  if "tinygrad_ref" not in src:
    raise ValueError("source manifest has no tinygrad_ref; the client's manifest test requires one")
  bundles = [bundle for bundle in src["bundles"] if only is None or bundle["short_name"] in only]
  if only is not None and (missing := only - {bundle["short_name"] for bundle in bundles}):
    raise ValueError(f"not in the source manifest: {', '.join(sorted(missing))}")
  if limit is not None:
    bundles = bundles[:limit]
  if not bundles:
    raise ValueError("no bundles selected")

  work_dir = Path(tempfile.mkdtemp(prefix="migrate-", dir=work_dir))
  migrated = []
  try:
    for i, bundle in enumerate(bundles, 1):
      out = json.loads(json.dumps(bundle))
      out["minimum_selector_version"] = str(selector_version)
      for model in out["models"]:
        model["type"] = model_type
        artifact = model["artifact"]
        started = time.monotonic()
        url, size, outcome = migrate_artifact(api, session, hf_repo, bundle["short_name"], artifact, work_dir, workers, dry_run)
        artifact.pop("chunks", None)
        artifact["download_uri"]["url"] = url
        log(f"[{i}/{len(bundles)}] {bundle['short_name']}: {outcome}, {size / 1e6:.1f} MB, {time.monotonic() - started:.0f} s")
      migrated.append(out)
  finally:
    shutil.rmtree(work_dir, ignore_errors=True)

  dst = {key: value for key, value in src.items() if key != "bundles"}
  dst["bundles"] = migrated
  return dst


def collapse_overrides(json_text: str) -> str:
  # one line per overrides dict, as json_parser.py writes it
  def replacer(match):
    items = [line.strip().rstrip(",") for line in match.group(2).splitlines() if line.strip()]
    return f'{match.group(1)}{{ {", ".join(items)} }}'
  return re.sub(r'("overrides": ){\s*([^}]*)\s*}', replacer, json_text)


def write_manifest(path: Path, manifest: dict) -> None:
  path.write_text(collapse_overrides(json.dumps(manifest, indent=2)) + "\n", encoding="utf-8")


def main() -> int:
  parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument("--src-json", required=True, type=Path, help="chunked manifest to read, e.g. docs/docs/driving_models_v22.json")
  parser.add_argument("--dst-json", required=True, type=Path, help="whole-file manifest to write, e.g. docs/docs/driving_models_v23.json")
  parser.add_argument("--hf-repo", required=True, help="dataset that receives the whole files; chunks are read from the source manifest's URLs")
  parser.add_argument("--selector-version", type=int, default=20)
  parser.add_argument("--model-type", default="driving")
  parser.add_argument("--only", default="", help="comma-separated short names; empty means every bundle")
  parser.add_argument("--limit", type=int, default=None, help="stop after this many bundles (rehearsals)")
  parser.add_argument("--workers", type=int, default=8, help="parallel chunk downloads per model")
  parser.add_argument("--work-dir", type=Path, default=None, help="scratch space for one model at a time")
  parser.add_argument("--dry-run", action="store_true", help="download and verify only: no uploads, no manifest")
  args = parser.parse_args()
  disable_progress_bars()  # the upload bars are per-file tqdm output, unreadable in a CI log

  src = json.loads(args.src_json.read_text(encoding="utf-8"))
  only = {name.strip() for name in args.only.split(",") if name.strip()} or None
  try:
    dst = migrate_manifest(src, hf_repo=args.hf_repo, api=HfApi(), session=requests.Session(), selector_version=args.selector_version,
                           model_type=args.model_type, only=only, limit=args.limit, workers=args.workers, work_dir=args.work_dir,
                           dry_run=args.dry_run)
  except Exception as e:
    print(f"migration stopped, nothing written: {e}", file=sys.stderr)
    return 1

  if args.dry_run:
    print(f"dry run: {len(dst['bundles'])} bundle(s) verified, {args.dst_json} not written", flush=True)
    return 0
  write_manifest(args.dst_json, dst)
  print(f"{args.dst_json} written with {len(dst['bundles'])} bundle(s) at selector version {args.selector_version}", flush=True)
  return 0


if __name__ == "__main__":
  sys.exit(main())
