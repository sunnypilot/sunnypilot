"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import hashlib
import http.server
import json
import os
import socketserver
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import requests

from openpilot.common.test import OpenpilotTestCase
from release.ci import migrate_whole_file_models as migrate

SRC_REPO = "sunnypilot/sunnypilot_models_v1"
DST_REPO = "fork/sunnypilot_models_v1"


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


class RepoHandler(http.server.BaseHTTPRequestHandler):
  """Serves /datasets/<repo>/resolve/main/<path> from a dict per repo; honours single byte ranges like HuggingFace."""
  repos: dict[str, dict[str, bytes]] = {}

  def do_GET(self):
    _, _, repo_and_path = self.path.partition("/datasets/")
    repo, _, path = urllib.parse.unquote(repo_and_path).partition(migrate.RESOLVE)
    body = self.repos.get(repo, {}).get(path)
    if body is None:
      self.send_response(404)
      self.end_headers()
      return
    range_header = self.headers.get("Range", "")
    if range_header.startswith("bytes="):
      start, _, end = range_header[6:].partition("-")
      start, end = int(start), int(end)
      self.send_response(206)
      self.send_header("Content-Range", f"bytes {start}-{end}/{len(body)}")
      body = body[start:end + 1]
    else:
      self.send_response(200)
    self.send_header("Content-Length", str(len(body)))
    self.end_headers()
    self.wfile.write(body)

  def log_message(self, *_):
    pass


class FakeHfApi:
  """Enough of HfApi for the script: LFS metadata lookup and file upload, backed by the served dict."""

  def __init__(self, files: dict[str, bytes]):
    self.files = files
    self.uploads: list[str] = []

  def get_paths_info(self, repo_id, paths, repo_type):
    assert repo_id == DST_REPO and repo_type == "dataset"
    return [SimpleNamespace(path=p, size=len(self.files[p]), lfs=SimpleNamespace(sha256=sha256(self.files[p]))) for p in paths if p in self.files]

  def upload_file(self, *, path_or_fileobj, path_in_repo, repo_id, repo_type, commit_message):
    assert repo_id == DST_REPO and repo_type == "dataset" and commit_message
    self.files[path_in_repo] = Path(path_or_fileobj).read_bytes()
    self.uploads.append(path_in_repo)


class TestMigrateWholeFileModels(OpenpilotTestCase):
  FOLDER = "models/recompiled9/model-Lav2 Model (January 24, 2024)-117"
  FILE = "driving_lav2_model_january_24_2024_tinygrad.pkl"

  @classmethod
  def setUpClass(cls):
    super().setUpClass()
    cls.server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), RepoHandler)
    cls.server.daemon_threads = True
    threading.Thread(target=cls.server.serve_forever, daemon=True).start()
    cls.endpoint = f"http://127.0.0.1:{cls.server.server_address[1]}"

  @classmethod
  def tearDownClass(cls):
    cls.server.shutdown()
    cls.server.server_close()
    super().tearDownClass()

  def setUp(self):
    super().setUp()
    self.whole = os.urandom(3 * 1024 + 517)
    self.chunks = [self.whole[:2048], self.whole[2048:]]
    self.src_files = {f"{self.FOLDER}/{self.FILE}.chunk{i + 1:02d}of02": chunk for i, chunk in enumerate(self.chunks)}
    self.dst_files: dict[str, bytes] = {}
    RepoHandler.repos = {SRC_REPO: self.src_files, DST_REPO: self.dst_files}
    self.api = FakeHfApi(self.dst_files)
    self.session = requests.Session()
    patcher = mock.patch.object(migrate.hf_constants, "ENDPOINT", self.endpoint)
    patcher.start()
    self.addCleanup(patcher.stop)
    patcher = mock.patch.object(migrate.time, "sleep")
    patcher.start()
    self.addCleanup(patcher.stop)

  def bundle(self, short_name="LAV2", index=3):
    quoted_folder = urllib.parse.quote(self.FOLDER)
    return {
      "short_name": short_name, "display_name": f"{short_name} (January 24, 2024)", "is_20hz": False, "is_big": False, "ref": "abc",
      "environment": "release", "runner": "tinygrad", "index": index, "minimum_selector_version": "19", "generation": "12",
      "overrides": {"folder": "Release Models", "lat": ".1", "long": ".3"},
      "models": [{"type": "chunked", "artifact": {
        "file_name": self.FILE,
        "download_uri": {"url": f"{self.endpoint}/datasets/{SRC_REPO}{migrate.RESOLVE}{quoted_folder}/{self.FILE}", "sha256": sha256(self.whole)},
        "chunks": [{"file_name": f"{self.FILE}.chunk{i + 1:02d}of02", "sha256": sha256(chunk)} for i, chunk in enumerate(self.chunks)],
      }}],
    }

  def manifest(self, *bundles):
    return {"tinygrad_ref": "e837e367", "bundles": list(bundles)}

  def run_migration(self, src, **kwargs):
    return migrate.migrate_manifest(src, hf_repo=DST_REPO, api=self.api, session=self.session, selector_version=20, model_type="driving",
                                    log=lambda _: None, **kwargs)

  def test_joins_uploads_and_rewrites_entry(self):
    dst = self.run_migration(self.manifest(self.bundle()))
    path = f"{self.FOLDER}/{self.FILE}"
    assert self.api.uploads == [path]
    assert self.dst_files[path] == self.whole
    assert dst["tinygrad_ref"] == "e837e367"
    bundle = dst["bundles"][0]
    assert bundle["minimum_selector_version"] == "20"
    assert bundle["index"] == 3 and bundle["overrides"] == {"folder": "Release Models", "lat": ".1", "long": ".3"}
    model = bundle["models"][0]
    assert model["type"] == "driving"
    assert "chunks" not in model["artifact"]
    assert model["artifact"]["download_uri"] == {"url": f"{self.endpoint}/datasets/{DST_REPO}{migrate.RESOLVE}{urllib.parse.quote(self.FOLDER)}/{self.FILE}",
                                                 "sha256": sha256(self.whole)}
    # the URL the manifest carries must be fetchable by ranges, as the client does it
    assert requests.get(model["artifact"]["download_uri"]["url"], headers={"Range": "bytes=0-0"}).status_code == 206

  def test_rerun_keeps_stored_file_without_transfer(self):
    self.dst_files[f"{self.FOLDER}/{self.FILE}"] = self.whole
    with mock.patch.object(migrate, "download", side_effect=AssertionError("must not download")):
      dst = self.run_migration(self.manifest(self.bundle()))
    assert self.api.uploads == []
    assert "chunks" not in dst["bundles"][0]["models"][0]["artifact"]

  def test_stale_stored_file_is_replaced(self):
    self.dst_files[f"{self.FOLDER}/{self.FILE}"] = b"an older build under the same name"
    self.run_migration(self.manifest(self.bundle()))
    assert self.dst_files[f"{self.FOLDER}/{self.FILE}"] == self.whole

  def test_whole_hash_mismatch_stops_before_upload(self):
    bad = self.bundle()
    bad["models"][0]["artifact"]["download_uri"]["sha256"] = sha256(b"not the joined file")
    with self.assertRaisesRegex(RuntimeError, "joined chunks hash"):
      self.run_migration(self.manifest(self.bundle("OK", 1), bad))
    assert self.api.uploads == [f"{self.FOLDER}/{self.FILE}"]  # the good bundle before it; the bad one never uploaded

  def test_corrupt_chunk_is_retried_then_fails(self):
    self.src_files[f"{self.FOLDER}/{self.FILE}.chunk02of02"] = b"corrupt"
    with self.assertRaisesRegex(RuntimeError, "giving up"):
      self.run_migration(self.manifest(self.bundle()))
    assert self.api.uploads == []

  def test_dry_run_verifies_without_uploading(self):
    dst = self.run_migration(self.manifest(self.bundle()), dry_run=True)
    assert self.api.uploads == [] and self.dst_files == {}
    assert "chunks" not in dst["bundles"][0]["models"][0]["artifact"]

  def test_only_and_limit_select_bundles(self):
    src = self.manifest(self.bundle("A", 1), self.bundle("B", 2), self.bundle("C", 3))
    assert [b["short_name"] for b in self.run_migration(src, only={"C", "A"})["bundles"]] == ["A", "C"]
    assert [b["short_name"] for b in self.run_migration(src, limit=2)["bundles"]] == ["A", "B"]
    with self.assertRaisesRegex(ValueError, "not in the source manifest: Z"):
      self.run_migration(src, only={"Z"})

  def test_unchunked_entry_needs_a_stored_file(self):
    plain = self.bundle()
    del plain["models"][0]["artifact"]["chunks"]
    with self.assertRaisesRegex(RuntimeError, "no chunks to join"):
      self.run_migration(self.manifest(plain))
    self.dst_files[f"{self.FOLDER}/{self.FILE}"] = self.whole
    assert self.run_migration(self.manifest(plain))["bundles"][0]["models"][0]["type"] == "driving"

  def test_missing_tinygrad_ref_is_refused(self):
    with self.assertRaisesRegex(ValueError, "tinygrad_ref"):
      self.run_migration({"bundles": [self.bundle()]})

  def test_repo_path_and_dest_url_round_trip(self):
    url = "https://huggingface.co/datasets/sunnypilot/sunnypilot_models_v1/resolve/main/models/recompiled23/model-Terrible%20Model%20%28August%2015%2C%202026%29-117/driving_terrible_model_tinygrad.pkl"
    path = migrate.repo_path(url)
    assert path == "models/recompiled23/model-Terrible Model (August 15, 2026)-117/driving_terrible_model_tinygrad.pkl"
    with mock.patch.object(migrate.hf_constants, "ENDPOINT", "https://huggingface.co"):
      assert migrate.dest_url("sunnypilot/sunnypilot_models_v1", path) == url

  def test_written_manifest_matches_parser_style(self):
    dst = self.run_migration(self.manifest(self.bundle()))
    with tempfile.TemporaryDirectory() as d:
      out = Path(d) / "driving_models_v23.json"
      migrate.write_manifest(out, dst)
      text = out.read_text()
    assert '"overrides": { "folder": "Release Models", "lat": ".1", "long": ".3" }' in text
    assert json.loads(text) == dst


if __name__ == "__main__":
  unittest.main()
