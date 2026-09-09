"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import contextlib
import glob
import hashlib
import http.server
import json
import math
import os
import re
import tempfile
import threading
import time
import unittest
from typing import Any
from unittest import mock

import requests

from openpilot.cereal import custom
from openpilot.common.hardware import hw
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.models import manager as manager_module
from openpilot.sunnypilot.models.fetcher import ModelFetcher, get_cached_bundles
from openpilot.sunnypilot.models import helpers
from openpilot.sunnypilot.models.helpers import (get_active_bundle, get_active_source, get_selected_bundle,
                                                  resolve_bundle_by_ref, validate_active_bundles)
from openpilot.sunnypilot.models.manager import DownloadCancelled, ModelManagerSP

FILE_NAME = 'driving_test_tinygrad.pkl'
# non-repeating bytes so a misordered or duplicated piece changes the assembled file
WHOLE_BODY = bytes(range(256)) * 40
PIECE = 1000  # test piece size -> 11 pieces, the last one short
NUM_PIECES = math.ceil(len(WHOLE_BODY) / PIECE)


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def piece_range(index: int) -> tuple[int, int]:
  """Inclusive byte range the client is expected to request for piece `index`."""
  start = index * PIECE
  return start, min(start + PIECE, len(WHOLE_BODY)) - 1


class DownloadHandler(http.server.BaseHTTPRequestHandler):
  """Serves WHOLE_BODY with byte-range support. Class attributes are reset per test."""
  request_ranges: list[tuple[int, int] | None] = []  # None: no (honored) Range header
  fail_ranges: dict[tuple[int, int], int] = {}  # range -> HTTP status, every time
  fail_once: set[tuple[int, int]] = set()  # ranges that 503 on their first request only
  fail_times: dict[tuple[int, int], int] = {}  # range -> how many more requests 503 before it succeeds
  stall_ranges: set[tuple[int, int]] = set()
  stall_event: threading.Event | None = None
  stall_released_by_event: bool | None = None
  support_ranges = True
  corrupt = False

  def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
    pass

  def do_GET(self):
    cls = type(self)
    if not self.path.endswith('/' + FILE_NAME):
      self.send_response(404)
      self.end_headers()
      return

    body = WHOLE_BODY
    if cls.corrupt:
      body = body[:5000] + bytes([body[5000] ^ 0xFF]) + body[5001:]

    rng = None
    match = re.fullmatch(r'bytes=(\d+)-(\d+)', self.headers.get('Range', ''))
    if match and cls.support_ranges:
      rng = (int(match.group(1)), int(match.group(2)))
    cls.request_ranges.append(rng)

    if rng in cls.fail_ranges:
      self.send_response(cls.fail_ranges[rng])
      self.end_headers()
      return
    if rng in cls.fail_once:
      cls.fail_once.discard(rng)
      self.send_response(503)
      self.end_headers()
      return
    if rng is not None and cls.fail_times.get(rng, 0) > 0:
      cls.fail_times[rng] -= 1
      self.send_response(503)
      self.end_headers()
      return

    if rng is None:
      payload = body
      self.send_response(200)
    else:
      start, end = rng
      payload = body[start:end + 1]
      self.send_response(206)
      self.send_header('Content-Range', f'bytes {start}-{end}/{len(body)}')
    self.send_header('Content-Length', str(len(payload)))
    self.end_headers()

    if rng in cls.stall_ranges:
      # write a little, then hold the connection until the test releases it
      self.wfile.write(payload[:100])
      self.wfile.flush()
      if cls.stall_event is not None:
        cls.stall_released_by_event = cls.stall_event.wait(timeout=5)
      self.wfile.write(payload[100:])
    else:
      self.wfile.write(payload)


@contextlib.contextmanager
def threaded_server(handler):
  """One thread per request, so parallel range requests are served concurrently."""
  server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
  thread = threading.Thread(target=server.serve_forever)
  thread.start()
  try:
    yield f'http://127.0.0.1:{server.server_port}'
  finally:
    server.shutdown()
    server.server_close()
    thread.join()


class ManagerDownloadTestBase(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    DownloadHandler.request_ranges = []
    DownloadHandler.fail_ranges = {}
    DownloadHandler.fail_once = set()
    DownloadHandler.fail_times = {}
    DownloadHandler.stall_ranges = set()
    DownloadHandler.stall_event = None
    DownloadHandler.stall_released_by_event = None
    DownloadHandler.support_ranges = True
    DownloadHandler.corrupt = False

    self._tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self._tmp.cleanup)
    self.dest = self._tmp.name

    for name, value in (('PIECE_SIZE', PIECE), ('REPORT_INTERVAL', 0.05), ('PIECE_BACKOFF', 0.01), ('RETRY_BACKOFF', 0.01)):
      patcher = mock.patch.object(manager_module, name, value)
      patcher.start()
      self.addCleanup(patcher.stop)

    self.reported: list[float] = []
    self.reported_statuses: list[int] = []

    self.manager = ModelManagerSP.__new__(ModelManagerSP)
    self.manager.params = mock.MagicMock()
    self.manager.params.get.return_value = b'0'  # not cancelled
    self.manager._download_ref = b'0'
    self.manager.pm = mock.MagicMock()
    self.manager.pm.send.side_effect = self._record_progress
    self.manager.selected_bundle = None
    self.manager.active_bundle = None
    self.manager.available_models = []
    self.manager.chestnut_present = False
    self.manager._block_size = 256
    self.manager._download_start_times = {}

  def _record_progress(self, *args) -> None:
    """Runs on every real _report_status send."""
    artifact = getattr(self, 'artifact', None)
    if artifact is not None:
      self.reported.append(float(artifact.downloadProgress.progress))
      status = artifact.downloadProgress.status
      self.reported_statuses.append(getattr(status, 'raw', status))  # .raw: _DynamicEnum is not int()-able

  def make_artifact(self):
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.init('models', 1)
    artifact = bundle.models[0].artifact
    artifact.fileName = FILE_NAME
    artifact.downloadUri.uri = self.base_url + '/' + FILE_NAME
    artifact.downloadUri.sha256 = sha256(WHOLE_BODY)
    self._bundle = bundle
    self.artifact = artifact
    return artifact

  @property
  def path(self) -> str:
    return os.path.join(self.dest, FILE_NAME)

  @property
  def sidecar(self) -> str:
    return manager_module._sidecar_path(self.path)

  def resume_state(self) -> dict:
    with open(self.sidecar) as f:
      return json.load(f)

  def write_resume_state(self, done: list[int], total: int = len(WHOLE_BODY), file_size: int | None = None,
                         file_sha256: str = sha256(WHOLE_BODY)) -> None:
    """An interrupted download: a full-size file holding the `done` pieces plus its sidecar."""
    with open(self.path, 'wb') as f:
      f.truncate(len(WHOLE_BODY) if file_size is None else file_size)
      for i in done:
        f.seek(i * PIECE)
        f.write(WHOLE_BODY[i * PIECE:(i + 1) * PIECE])
    with open(self.sidecar, 'w') as f:
      json.dump({"total": total, "piece_size": PIECE, "ranged": True, "sha256": file_sha256, "done": done}, f)

  @staticmethod
  def piece_requests() -> list[tuple[int, int]]:
    """Honored ranges minus the one-byte size probe."""
    return [r for r in DownloadHandler.request_ranges if r is not None and r != (0, 0)]

  def run_with_server(self, fn):
    with threaded_server(DownloadHandler) as base_url:
      self.base_url = base_url
      return fn()

  def download_file(self):
    artifact = self.make_artifact()
    asyncio.run(self.manager._download_file(artifact.downloadUri.uri, self.path, artifact))
    return artifact

  def read_path(self) -> bytes:
    with open(self.path, 'rb') as f:
      return f.read()

  def _make_params_with_store(self):
    params = mock.MagicMock()
    store = {}

    def get(key, *args, **kwargs):
      return store.get(key, b"0")  # b"0" -> download not cancelled

    def put(key, value, *args, **kwargs):
      store[key] = value

    params.get.side_effect = get
    params.put.side_effect = put
    return params, store


class TestManagerDownload(ManagerDownloadTestBase):
  """Exercises the real parallel byte-range _download_file against a local server."""

  def test_download_file_writes_exact_bytes(self):
    def body():
      artifact = self.download_file()
      assert self.read_path() == WHOLE_BODY
      assert not os.path.exists(self.sidecar), "resume sidecar must go once every piece has landed"
      assert artifact.fileName not in self.manager._download_start_times
    self.run_with_server(body)

  def test_pieces_tile_the_file(self):
    def body():
      self.download_file()
      expected = [piece_range(i) for i in range(NUM_PIECES)]
      assert sorted(self.piece_requests()) == expected
    self.run_with_server(body)

  def test_pieces_download_in_parallel(self):
    """The stalled piece is only released once every other piece has been requested. A serial
    downloader would sit on it until the server's stall timeout instead."""
    def body():
      DownloadHandler.stall_ranges = {piece_range(0)}
      DownloadHandler.stall_event = threading.Event()
      others = {piece_range(i) for i in range(1, NUM_PIECES)}

      def release_when_others_requested():
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not others <= set(self.piece_requests()):
          time.sleep(0.01)
        DownloadHandler.stall_event.set()

      threading.Thread(target=release_when_others_requested).start()
      self.download_file()
      assert DownloadHandler.stall_released_by_event is True, "other pieces did not download while one was stalled"
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_speed_and_eta_reported(self):
    def body():
      artifact = self.download_file()
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.downloading
      assert artifact.downloadProgress.speed > 0
      assert artifact.downloadProgress.eta >= 1
    self.run_with_server(body)

  def test_progress_is_monotonic_and_bounded(self):
    def body():
      self.download_file()
      assert self.reported, "expected progress reports"
      for a, b in zip(self.reported, self.reported[1:], strict=False):
        assert b >= a, f"progress went backwards: {a} -> {b}"
      assert max(self.reported) <= 99.0, f"progress must stay <=99 until verify, got {max(self.reported)}"
    self.run_with_server(body)

  def test_fallback_when_server_ignores_ranges(self):
    """A 200 to the range probe means whole bodies only: one plain stream, same result."""
    def body():
      DownloadHandler.support_ranges = False
      self.download_file()
      assert self.read_path() == WHOLE_BODY
      assert DownloadHandler.request_ranges == [None, None], "expected the probe plus one whole-body request"
      assert not os.path.exists(self.sidecar)
    self.run_with_server(body)

  def test_http_error_propagates(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 404}
      with self.assertRaises(requests.exceptions.HTTPError):
        self.download_file()
      assert os.path.isfile(self.sidecar), "a failed download stays marked incomplete"
      assert 1 not in self.resume_state()["done"]
    self.run_with_server(body)

  def test_transient_error_is_retried(self):
    def body():
      DownloadHandler.fail_once = {piece_range(2)}
      self.download_file()
      assert self.read_path() == WHOLE_BODY
      assert self.piece_requests().count(piece_range(2)) == 2
    self.run_with_server(body)

  def test_cancellation_via_download_ref(self):
    """Removing DownloadRef mid-transfer cancels the download and keeps the finished pieces. One piece
    is held back so the transfer spans several reporter ticks; the ref vanishes on the second."""
    def body():
      DownloadHandler.stall_ranges = {piece_range(5)}
      DownloadHandler.stall_event = threading.Event()
      threading.Timer(0.3, DownloadHandler.stall_event.set).start()
      checks = {"n": 0}

      def get(key):
        if key == "ModelManager_DownloadRef":
          checks["n"] += 1
          return b"ref" if checks["n"] <= 1 else None
        return b"0"

      self.manager.params.get.side_effect = get
      self.manager._download_ref = b"ref"
      with self.assertRaises(DownloadCancelled):
        self.download_file()
      assert checks["n"] >= 2, "cancel must have been polled while the transfer was running"
      state = self.resume_state()
      assert state["done"] and 5 not in state["done"], "a cancel must record the finished pieces for resume"
      assert os.path.getsize(self.path) == len(WHOLE_BODY)
    self.run_with_server(body)

  def test_cancel_stops_a_running_piece(self):
    """A worker blocked on a slow piece exits at its next block once cancelled."""
    def body():
      DownloadHandler.stall_ranges = {piece_range(3)}
      DownloadHandler.stall_event = threading.Event()
      self.manager.params.get.return_value = None  # cancelled
      threading.Timer(0.3, DownloadHandler.stall_event.set).start()
      with self.assertRaises(DownloadCancelled):
        self.download_file()
      assert 3 not in self.resume_state()["done"], "cancelled piece must not be recorded as complete"
    self.run_with_server(body)

  def test_replaced_download_ref_queues_instead_of_cancelling(self):
    """Selecting another model mid-transfer lets the running download finish."""
    def body():
      self.manager.params.get.side_effect = lambda key: b"other-ref" if key == "ModelManager_DownloadRef" else None
      self.manager._download_ref = b"ref"
      self.download_file()
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_resume_skips_complete_pieces(self):
    """Pieces recorded in the sidecar are kept and not re-requested; progress starts above their share."""
    def body():
      self.write_resume_state(done=[0, 4])
      self.download_file()
      requested = self.piece_requests()
      assert piece_range(0) not in requested and piece_range(4) not in requested, "complete piece was re-downloaded"
      assert self.read_path() == WHOLE_BODY
      assert min(self.reported) >= 2 * PIECE / len(WHOLE_BODY) * 100 - 1, "progress must not restart below the resumed share"
      assert not os.path.exists(self.sidecar)
    self.run_with_server(body)

  def test_resume_state_for_another_layout_is_ignored(self):
    """A sidecar written for a different file size (the model was republished) starts over."""
    def body():
      self.write_resume_state(done=[0], total=len(WHOLE_BODY) + 1)
      self.download_file()
      assert piece_range(0) in self.piece_requests()
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_resume_state_for_other_content_is_ignored(self):
    """A sidecar for different bytes of the same name and size (the model was republished) starts over."""
    def body():
      self.write_resume_state(done=[0], file_sha256="0" * 64)
      self.download_file()
      assert piece_range(0) in self.piece_requests()
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_malformed_resume_state_starts_over(self):
    """A sidecar that is not the expected JSON object is ignored, never fatal."""
    def body():
      layout = {"total": len(WHOLE_BODY), "piece_size": PIECE, "ranged": True, "sha256": sha256(WHOLE_BODY)}
      for junk in (b'[]', b'{"total": ', json.dumps({**layout, "done": 3}).encode(), json.dumps({**layout, "done": ["0", None]}).encode()):
        with open(self.path, 'wb') as f:
          f.truncate(len(WHOLE_BODY))
        with open(self.sidecar, 'wb') as f:
          f.write(junk)
        DownloadHandler.request_ranges = []
        self.download_file()
        assert sorted(self.piece_requests()) == [piece_range(i) for i in range(NUM_PIECES)], f"sidecar {junk!r} must be ignored"
        assert self.read_path() == WHOLE_BODY
        assert not os.path.exists(self.sidecar)
    self.run_with_server(body)

  def test_resume_needs_a_full_size_file(self):
    """A sidecar whose file was truncated underneath it is not trusted."""
    def body():
      self.write_resume_state(done=[0], file_size=PIECE)
      self.download_file()
      assert piece_range(0) in self.piece_requests()
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_pieces_and_resume_state_are_synced_to_disk(self):
    """Every piece is fdatasync'd before it is recorded, and the sidecar is fsync'd: a power loss
    mid-download must never leave resume state naming bytes that never reached flash."""
    def body():
      with mock.patch.object(manager_module.os, 'fdatasync', wraps=os.fdatasync) as piece_sync, \
           mock.patch.object(manager_module.os, 'fsync', wraps=os.fsync) as state_sync:
        self.download_file()
      assert piece_sync.call_count == NUM_PIECES, f"expected one fdatasync per piece, got {piece_sync.call_count}"
      assert state_sync.call_count >= 2, "sidecar file and directory must be fsync'd"
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_repeat_downloads_are_stable(self):
    """Back-to-back runs must produce identical bytes and leak no start-time state."""
    def body():
      for _ in range(2):
        self.download_file()
        assert self.read_path() == WHOLE_BODY
        assert self.manager._download_start_times == {}
    self.run_with_server(body)


class TestProcessArtifact(ManagerDownloadTestBase):
  """Verification, cleanup and resume policy around the download."""

  def test_downloaded_file_verifies_and_ends_idle(self):
    def body():
      artifact = self.make_artifact()
      asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert self.read_path() == WHOLE_BODY
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.downloaded
      assert artifact.downloadProgress.progress == 100
      assert artifact.downloadProgress.speed == 0
      assert artifact.downloadProgress.eta == 0
    self.run_with_server(body)

  def test_hash_mismatch_discards_file_and_parts(self):
    def body():
      DownloadHandler.corrupt = True
      artifact = self.make_artifact()
      with self.assertRaises(ValueError):
        asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert not os.path.isfile(self.path)
      assert not os.path.exists(self.sidecar), "a corrupt file must not be resumed from"
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed
    self.run_with_server(body)

  def test_transport_error_keeps_resume_state(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 500}
      artifact = self.make_artifact()
      with self.assertRaises(requests.exceptions.HTTPError):
        asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert os.path.isfile(self.path) and os.path.isfile(self.sidecar), "finished pieces must survive a transport error"
      assert self.resume_state()["done"]
    self.run_with_server(body)

  def test_interrupted_download_resumes_without_reverifying(self):
    """A file with a sidecar is known incomplete: skip hashing it and pick up where it stopped."""
    def body():
      self.write_resume_state(done=[0, 1, 2])
      artifact = self.make_artifact()
      asyncio.run(self.manager._process_artifact(artifact, self.dest))
      ds = custom.ModelManagerSP.DownloadStatus
      assert self.reported_statuses[0] == ds.downloading, "an in-progress download is not verified first"
      assert piece_range(0) not in self.piece_requests()
      assert self.read_path() == WHOLE_BODY
      assert artifact.downloadProgress.status == ds.downloaded
    self.run_with_server(body)

  def test_cached_file_skips_network(self):
    def body():
      with open(self.path, 'wb') as f:
        f.write(WHOLE_BODY)
      artifact = self.make_artifact()
      asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert DownloadHandler.request_ranges == [], "cached file must not hit the network"
      ds = custom.ModelManagerSP.DownloadStatus
      assert self.reported_statuses == [ds.verifying, ds.cached]
      assert artifact.downloadProgress.progress == 100
    self.run_with_server(body)

  def test_legacy_chunk_files_are_purged(self):
    """Chunk files from a pre-v20 download would shadow the whole file in open_file_chunked."""
    def body():
      for suffix in ('.chunkmanifest', '.chunk01of02', '.chunk02of02'):
        with open(self.path + suffix, 'wb') as f:
          f.write(b'2' if suffix == '.chunkmanifest' else b'legacy')
      artifact = self.make_artifact()
      asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert glob.glob(self.path + '.chunk*') == []
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_cached_bundle_cancel_skips_slot_write(self):
    """A cancel must stop an already-on-disk bundle before it is applied to the slot."""
    def body():
      with open(self.path, 'wb') as f:
        f.write(WHOLE_BODY)
      self.make_artifact()
      self._bundle.ref = "test-ref"
      params, store = self._make_params_with_store()
      store["ModelManager_DownloadRef"] = None  # removed -> cancelled
      self.manager.params = params
      self.manager._download_ref = b"ref"
      with self.assertRaises(DownloadCancelled):
        asyncio.run(self.manager._download_bundle(self._bundle, self.dest, "qcom"))
      assert "ModelManager_ActiveBundle" not in store
      assert os.path.isfile(self.path), "cancel must not delete a cached model"
    self.run_with_server(body)

  def test_download_writes_qcom_slot(self):
    """A download resolved to the qcom source writes the qcom active bundle slot only."""
    def body():
      self.make_artifact()
      self._bundle.ref = "test-ref"
      self._bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
      params, store = self._make_params_with_store()
      self.manager.params = params
      asyncio.run(self.manager._download_bundle(self._bundle, self.dest, "qcom"))

      assert "ModelManager_ActiveBundle" in store, "qcom download must write the qcom slot"
      assert "ModelManager_ActiveBundleChestnut" not in store, "qcom download must not touch the chestnut slot"
      assert self.manager.selected_bundle.status == custom.ModelManagerSP.DownloadStatus.downloaded
      assert self.manager.active_bundle is not None and self.manager.active_bundle.ref == "test-ref"
      assert self.manager.active_bundle.status == custom.ModelManagerSP.DownloadStatus.downloaded
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_download_writes_chestnut_slot(self):
    """A download resolved to the chestnut source writes the chestnut active bundle slot only."""
    def body():
      self.make_artifact()
      self._bundle.ref = "big-ref"
      self._bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
      params, store = self._make_params_with_store()
      self.manager.params = params
      asyncio.run(self.manager._download_bundle(self._bundle, self.dest, "chestnut"))

      assert "ModelManager_ActiveBundleChestnut" in store, "chestnut download must write the chestnut slot"
      assert "ModelManager_ActiveBundle" not in store, "chestnut download must not touch the qcom slot"
      assert self.manager.selected_bundle.status == custom.ModelManagerSP.DownloadStatus.downloaded
    self.run_with_server(body)

  def test_replaced_download_ref_is_kept(self):
    """A selection made during a download must survive that download's cleanup."""
    self.manager.params.get.return_value = b"new-ref"
    self.manager._download_ref = b"old-ref"
    self.manager._release_download_ref()
    self.manager.params.remove.assert_not_called()

  def test_own_download_ref_is_released(self):
    self.manager.params.get.return_value = b"ref"
    self.manager._download_ref = b"ref"
    self.manager._release_download_ref()
    self.manager.params.remove.assert_called_once_with("ModelManager_DownloadRef")

  def test_clear_cache_keeps_only_active_files(self):
    """Interrupted downloads, legacy chunk files and other models all go; the selected slots' files stay."""
    active = custom.ModelManagerSP.ModelBundle.new_message()
    active.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
    active.init('models', 1)
    active.models[0].artifact.fileName = 'active.pkl'
    raw = active.to_dict()
    self.manager.params.get.side_effect = lambda key, *a, **k: raw if key == "ModelManager_ActiveBundle" else None

    for name in ('active.pkl', 'active.pkl.chunkmanifest', 'active.pkl.chunk01of02', 'other.pkl', 'other.pkl.download'):
      with open(os.path.join(self.dest, name), 'wb') as f:
        f.write(b'x')
    with mock.patch.object(hw.Paths, 'model_root', staticmethod(lambda: self.dest)):
      self.manager.clear_model_cache()
    assert os.listdir(self.dest) == ['active.pkl']


class TestTransferRetries(ManagerDownloadTestBase):
  """A transfer whose pieces exhaust their retries is retried from its resume state after a
  cancellable backoff; permanent errors are not retried at all."""

  def process(self):
    artifact = self.make_artifact()
    asyncio.run(self.manager._process_artifact(artifact, self.dest))
    return artifact

  def test_transient_failure_resumes_from_finished_pieces(self):
    """The first transfer gives up on piece 1; the retry fetches only what the sidecar does not record."""
    def body():
      DownloadHandler.fail_times = {piece_range(1): manager_module.PIECE_RETRIES}
      original = self.manager._download_file
      done_before_retry: list[set[int]] = []

      async def spy(url, path, artifact):
        with contextlib.suppress(FileNotFoundError):
          done_before_retry.append(set(self.resume_state()["done"]))
        return await original(url, path, artifact)

      # a slower piece backoff gives the other pieces time to land before the first transfer gives up
      with mock.patch.object(manager_module, 'PIECE_BACKOFF', 0.05), mock.patch.object(self.manager, '_download_file', spy):
        artifact = self.process()
      assert len(done_before_retry) == 1 and done_before_retry[0], "expected exactly one retry, resuming recorded pieces"
      requested = self.piece_requests()
      assert requested.count(piece_range(1)) == manager_module.PIECE_RETRIES + 1
      for i in done_before_retry[0]:
        assert requested.count(piece_range(i)) == 1, f"piece {i} was recorded as done yet fetched again"
      assert self.read_path() == WHOLE_BODY
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.downloaded
      assert not os.path.exists(self.sidecar)
    self.run_with_server(body)

  def test_transient_error_gives_up_after_every_attempt(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 503}
      artifact = self.make_artifact()
      with self.assertRaises(requests.exceptions.HTTPError):
        asyncio.run(self.manager._process_artifact(artifact, self.dest))
      expected = manager_module.PIECE_RETRIES * manager_module.DOWNLOAD_ATTEMPTS
      assert self.piece_requests().count(piece_range(1)) == expected
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed
      assert os.path.isfile(self.sidecar), "the resume state survives for the next request"
    self.run_with_server(body)

  def test_permanent_http_error_is_not_retried(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 404}
      artifact = self.make_artifact()
      with self.assertRaises(requests.exceptions.HTTPError):
        asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert self.piece_requests().count(piece_range(1)) == 1, "a 404 must not be retried"
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed
    self.run_with_server(body)

  def test_cancel_during_backoff_stops_the_retry(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 503}
      original = self.manager._download_file
      gave_up = threading.Event()

      async def wrapped(url, path, artifact):
        try:
          return await original(url, path, artifact)
        except Exception:
          gave_up.set()  # the ref disappears while the backoff is running
          raise

      self.manager.params.get.side_effect = lambda key: (None if gave_up.is_set() else b"ref") if key == "ModelManager_DownloadRef" else b"0"
      self.manager._download_ref = b"ref"
      artifact = self.make_artifact()
      started = time.monotonic()
      with mock.patch.object(manager_module, 'RETRY_BACKOFF', 30.0), mock.patch.object(self.manager, '_download_file', wrapped):
        with self.assertRaises(DownloadCancelled):
          asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert time.monotonic() - started < 5, "the backoff must end at the cancel, not after 30 s"
      assert self.piece_requests().count(piece_range(1)) == manager_module.PIECE_RETRIES, "no second transfer after a cancel"
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed
    self.run_with_server(body)


class TestDownloadRequests(ManagerDownloadTestBase):
  """What the download row shows once _process_download_requests has handled a request: a failure
  stays visible until the next request, a finished or cancelled download clears it."""

  def _request(self, ref: str) -> dict:
    self.make_artifact()
    self._bundle.ref = ref
    self._bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
    self.manager.source_models = {"qcom": [self._bundle], "chestnut": []}
    params, store = self._make_params_with_store()
    store["ModelManager_DownloadRef"] = ref
    params.remove.side_effect = lambda key: store.__setitem__(key, None)
    self.manager.params = params
    return store

  def _process_requests(self):
    with mock.patch.object(manager_module.Paths, 'model_root', return_value=self.dest):
      self.manager._process_download_requests()

  def test_failed_download_stays_on_the_row(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 404}
      store = self._request("test-ref")
      self._process_requests()
      self._process_requests()  # an idle tick must not clear the failure
      assert self.manager.selected_bundle is not None
      assert self.manager.selected_bundle.status == custom.ModelManagerSP.DownloadStatus.failed
      assert store["ModelManager_DownloadRef"] is None, "the failed request is released"
      assert "ModelManager_ActiveBundle" not in store
    self.run_with_server(body)

  def test_finished_download_clears_the_row(self):
    def body():
      store = self._request("test-ref")
      self._process_requests()
      assert self.manager.selected_bundle is None
      assert "ModelManager_ActiveBundle" in store
      assert self.read_path() == WHOLE_BODY
    self.run_with_server(body)

  def test_cancelled_download_clears_the_row(self):
    def body():
      DownloadHandler.stall_ranges = {piece_range(3)}
      DownloadHandler.stall_event = threading.Event()
      store = self._request("test-ref")

      def cancel_soon():
        time.sleep(0.2)
        store["ModelManager_DownloadRef"] = None
        DownloadHandler.stall_event.set()

      threading.Thread(target=cancel_soon).start()
      self._process_requests()
      assert self.manager.selected_bundle is None
      assert "ModelManager_ActiveBundle" not in store
      assert os.path.isfile(self.sidecar), "a cancel keeps the resume state"
    self.run_with_server(body)


class TestManagerImports(OpenpilotTestCase):
  """Catches undeclared dependencies. aiohttp lived only in the AGNOS venv; 19.6 dropped
  it and models_manager died on device while CI stayed green."""

  def test_manager_imports(self):
    assert manager_module.ModelManagerSP is not None

  def test_no_undeclared_http_client(self):
    with open(manager_module.__file__) as f:
      src = f.read()
    assert 'import aiohttp' not in src, "aiohttp is not available on AGNOS 19.6; use requests"

  def test_download_timeout_is_explicit(self):
    connect, read = manager_module.DOWNLOAD_TIMEOUT
    assert connect > 0 and read > 0, "requests defaults to no timeout; downloads would hang forever"

  def test_parallelism_is_bounded(self):
    assert 1 < manager_module.MAX_CONCURRENT_CHUNKS <= 32, "HuggingFace was only verified rate-limit free up to 32 connections"


class TestResolveBundleByRef(OpenpilotTestCase):
  """A ref resolves to (bundle, source) across both hardware manifests. Refs are
  unique per manifest and never overlap across sources, so a ref maps to exactly
  one slot. Shared by the manager's download flow and the settings UI."""

  @staticmethod
  def _bundle(ref: str):
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.ref = ref
    return bundle

  def test_qcom_ref_resolves_to_qcom_slot(self):
    small = self._bundle("small")
    assert resolve_bundle_by_ref("small", {"qcom": [small], "chestnut": []}) == (small, "qcom")

  def test_chestnut_ref_resolves_to_chestnut_slot(self):
    big = self._bundle("big")
    assert resolve_bundle_by_ref("big", {"qcom": [], "chestnut": [big]}) == (big, "chestnut")

  def test_unknown_ref_returns_none(self):
    source_bundles = {"qcom": [self._bundle("small")], "chestnut": []}
    assert resolve_bundle_by_ref("nope", source_bundles) is None


def manifest_bundle(short_name: str, ref: str, index: int = 0, is_big: bool = False) -> dict:
  """Minimal whole-file manifest bundle dict, version-compatible.
  Big (chestnut) bundles carry `is_big: true` in the manifest JSON."""
  return {
    "index": index,
    "short_name": short_name,
    "display_name": short_name.upper(),
    "generation": 1,
    "environment": "release",
    "runner": "tinygrad",
    "is_big": is_big,
    "minimum_selector_version": str(helpers.REQUIRED_JSON_VERSION),
    "ref": ref,
    "models": [{
      "type": "driving",
      "artifact": {
        "file_name": f"{short_name}.pkl",
        "download_uri": {"url": f"https://example.com/{short_name}.pkl", "sha256": "s"},
      },
    }],
  }


def fresh_sync_time() -> int:
  return int(time.monotonic() * 1e9)


class TestModelFetcherSources(OpenpilotTestCase):
  """Both manifests are always maintained: get_bundles_for_source exposes either
  source by name, and active_source picks which one matches the attached hardware."""

  def _make_params(self, qcom_manifest, chestnut_manifest):
    params = mock.MagicMock()

    def get(key):
      if key == "ModelManager_ModelsCache":
        return qcom_manifest
      if key == "ModelManager_ModelsCache_Chestnut":
        return chestnut_manifest
      if key in ("ModelManager_LastSyncTime", "ModelManager_LastSyncTime_Chestnut"):
        return fresh_sync_time()
      return None

    params.get.side_effect = get
    return params

  def test_active_source_follows_chestnut_presence(self):
    assert ModelFetcher.active_source(False) == "qcom"
    assert ModelFetcher.active_source(True) == "chestnut"

  def test_get_bundles_for_source_returns_each_source(self):
    params = self._make_params({"bundles": [manifest_bundle("small", "aaa")]},
                               {"bundles": [manifest_bundle("big", "bbb", is_big=True)]})
    fetcher = ModelFetcher(params)
    assert [bundle.ref for bundle in fetcher.get_bundles_for_source("qcom")] == ["aaa"]
    assert [bundle.ref for bundle in fetcher.get_bundles_for_source("chestnut")] == ["bbb"]

  def test_get_bundles_for_source_unknown(self):
    assert ModelFetcher(mock.MagicMock()).get_bundles_for_source("bogus") == []

  def test_get_cached_bundles_parses_source(self):
    params = self._make_params({"bundles": [manifest_bundle("small", "aaa")]},
                               {"bundles": [manifest_bundle("big", "bbb", is_big=True)]})
    qcom_bundles = get_cached_bundles(params, "qcom")
    chestnut_bundles = get_cached_bundles(params, "chestnut")
    assert [b.ref for b in qcom_bundles] == ["aaa"]
    assert [b.ref for b in chestnut_bundles] == ["bbb"]
    assert qcom_bundles[0].displayName == "SMALL"

  def test_get_cached_bundles_empty_when_missing(self):
    params = mock.MagicMock()
    params.get.return_value = None
    assert get_cached_bundles(params, "qcom") == []
    assert get_cached_bundles(params, "chestnut") == []

  def test_get_cached_bundles_unknown_source(self):
    assert get_cached_bundles(mock.MagicMock(), "bogus") == []

  def test_active_json_has_both_urls(self):
    params = mock.MagicMock()
    ModelFetcher(params)
    active_json_calls = [call for call in params.put.call_args_list if call.args[0] == "ModelManager_ActiveJson"]
    assert active_json_calls, "expected ModelManager_ActiveJson to be written"
    assert active_json_calls[-1].args[1] == {
      "qcom": ModelFetcher.MODEL_URL,
      "chestnut": ModelFetcher.MODEL_URL_CHESTNUT,
    }

  def test_chunked_manifest_entries_are_ignored(self):
    """A stray `chunks` array is not parsed and leaves no chunk manifest on disk."""
    chunked = manifest_bundle("small", "aaa")
    chunked["models"][0]["artifact"]["chunks"] = [{"file_name": "small.pkl.chunk01of01", "sha256": "c"}]
    with tempfile.TemporaryDirectory() as model_dir, mock.patch.object(hw.Paths, 'model_root', staticmethod(lambda: model_dir)):
      bundles = ModelFetcher(mock.MagicMock()).model_parser.parse_models({"bundles": [chunked]})
      assert len(bundles[0].models[0].artifact.chunks) == 0
      assert os.listdir(model_dir) == []

  def test_model_type_driving_and_legacy_chunked_both_parse(self):
    """New manifests type the whole pkl `driving`; `chunked` must keep parsing because an upgrading
    device reads its cached v22 catalog before the first refetch, and an unknown type raises."""
    driving = manifest_bundle("small", "aaa")
    legacy = manifest_bundle("old", "bbb", index=1)
    legacy["models"][0]["type"] = "chunked"
    bundles = ModelFetcher(mock.MagicMock()).model_parser.parse_models({"bundles": [driving, legacy]})
    assert bundles[0].models[0].type == helpers.ModelManager.Model.Type.driving
    assert bundles[1].models[0].type == helpers.ModelManager.Model.Type.chunked


class TestSourceCacheIntegrity(OpenpilotTestCase):
  """Each source's cached manifest must contain only that source's models; the
  `is_big` flag in the JSON marks the big (chestnut) models. A mismatched cache is
  legacy data from before the per-source split (the active manifest was cached
  under the unsuffixed key regardless of hardware) and is refetched. This
  replaces the old one-time bundle migration."""

  def _make_params(self, qcom_manifest, chestnut_manifest):
    params = mock.MagicMock()

    def get(key):
      if key == "ModelManager_ModelsCache":
        return qcom_manifest
      if key == "ModelManager_ModelsCache_Chestnut":
        return chestnut_manifest
      if key in ("ModelManager_LastSyncTime", "ModelManager_LastSyncTime_Chestnut"):
        return fresh_sync_time()
      return None

    params.get.side_effect = get
    return params

  def _fetched(self, *bundles):
    return ModelFetcher(mock.MagicMock()).model_parser.parse_models({"bundles": list(bundles)})

  def test_qcom_cache_with_big_models_is_refetched(self):
    """Legacy: the unsuffixed cache holds the big manifest. is_big confirms it is
    the wrong set for qcom, so a fresh fetch replaces it."""
    params = self._make_params({"bundles": [manifest_bundle("big", "bbb", is_big=True)]},
                               {"bundles": [manifest_bundle("big2", "ccc", is_big=True)]})
    fetcher = ModelFetcher(params)
    fetched = self._fetched(manifest_bundle("small", "aaa"))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched):
      bundles = fetcher.get_bundles_for_source("qcom")
    assert [bundle.ref for bundle in bundles] == ["aaa"]

  def test_chestnut_cache_without_big_models_is_refetched(self):
    params = self._make_params({"bundles": [manifest_bundle("small", "aaa")]},
                               {"bundles": [manifest_bundle("big2", "ccc")]})
    fetcher = ModelFetcher(params)
    fetched = self._fetched(manifest_bundle("big", "bbb", is_big=True))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched):
      bundles = fetcher.get_bundles_for_source("chestnut")
    assert [bundle.ref for bundle in bundles] == ["bbb"]

  def test_matching_caches_are_used_without_fetch(self):
    params = self._make_params({"bundles": [manifest_bundle("small", "aaa")]},
                               {"bundles": [manifest_bundle("big", "bbb", is_big=True)]})
    fetcher = ModelFetcher(params)
    with mock.patch.object(fetcher, "_fetch_and_cache_models", side_effect=AssertionError("cache should be used")):
      assert [bundle.ref for bundle in fetcher.get_bundles_for_source("qcom")] == ["aaa"]
      assert [bundle.ref for bundle in fetcher.get_bundles_for_source("chestnut")] == ["bbb"]

  def test_stale_version_cache_is_refetched(self):
    """A source-matching cache whose bundles are all filtered by the selector version
    check parses to zero valid bundles; it is stale (e.g. an old manifest) and must be
    refetched instead of silently returning an empty list forever."""
    stale = manifest_bundle("small", "aaa")
    stale["minimum_selector_version"] = "16"
    params = self._make_params({"bundles": [stale]},
                               {"bundles": [manifest_bundle("big", "bbb", is_big=True)]})
    fetcher = ModelFetcher(params)
    fetched = self._fetched(manifest_bundle("small2", "ddd"))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched) as fetch:
      bundles = fetcher.get_bundles_for_source("qcom")
    fetch.assert_called_once_with("qcom")
    assert [bundle.ref for bundle in bundles] == ["ddd"]

  def test_mismatched_refetch_happens_once(self):
    """If the fresh manifest still fails the source check, the URL is authoritative:
    trust it instead of refetching at 1 Hz forever."""
    params = self._make_params({"bundles": [manifest_bundle("big", "bbb", is_big=True)]},
                               {"bundles": [manifest_bundle("big2", "ccc", is_big=True)]})
    fetcher = ModelFetcher(params)
    fetched = self._fetched(manifest_bundle("big", "bbb", is_big=True))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched) as fetch:
      first = fetcher.get_bundles_for_source("qcom")
      second = fetcher.get_bundles_for_source("qcom")
    fetch.assert_called_once_with("qcom")
    assert [bundle.ref for bundle in first] == ["bbb"]
    assert [bundle.ref for bundle in second] == ["bbb"]

  def test_corrupt_cache_is_refetched(self):
    """A cache that fails to parse (e.g. truncated/foreign JSON) must trigger a
    refetch instead of raising every loop and never recovering."""
    corrupt = {"bundles": [{"short_name": "broken"}]}  # missing required fields
    params = self._make_params(corrupt, {"bundles": [manifest_bundle("big", "bbb", is_big=True)]})
    fetcher = ModelFetcher(params)
    fetched = self._fetched(manifest_bundle("small", "aaa"))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched) as fetch:
      bundles = fetcher.get_bundles_for_source("qcom")
    fetch.assert_called_once_with("qcom")
    assert [bundle.ref for bundle in bundles] == ["aaa"]


class TestActiveBundleValidation(OpenpilotTestCase):
  """Validation is per-slot: a failed fetch (empty bundle list) must not reset a slot,
  and resetting one slot must not stomp the runner cache derived from the other."""

  def setUp(self):
    super().setUp()
    helpers._LAST_VALIDATED_RAW.clear()

  @staticmethod
  def _raw_bundle(ref: str, runner: int | None = None) -> dict:
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.ref = ref
    bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
    if runner is not None:
      bundle.runner = runner
    return bundle.to_dict()

  def _params(self, qcom=None, chestnut=None):
    params = mock.MagicMock()

    def get(key, *args, **kwargs):
      return {"ModelManager_ActiveBundle": qcom, "ModelManager_ActiveBundleChestnut": chestnut}.get(key)

    params.get.side_effect = get
    return params

  def test_empty_catalog_does_not_reset_slot(self):
    params = self._params(qcom=self._raw_bundle("small"))
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      validate_active_bundles(params, {"qcom": [], "chestnut": []})
    params.remove.assert_not_called()

  def test_reset_recomputes_runner_from_surviving_slot(self):
    tinygrad = int(custom.ModelManagerSP.Runner.tinygrad)
    big_raw = self._raw_bundle("big", runner=tinygrad)
    params = self._params(qcom=self._raw_bundle("gone"), chestnut=big_raw)
    catalog = {"qcom": [custom.ModelManagerSP.ModelBundle(**self._raw_bundle("other"))],
               "chestnut": [custom.ModelManagerSP.ModelBundle(**big_raw)]}
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      validate_active_bundles(params, catalog)
    params.remove.assert_called_once_with("ModelManager_ActiveBundle")
    runner_puts = [call for call in params.put.call_args_list if call.args[0] == "ModelRunnerTypeCache"]
    assert [call.args[1] for call in runner_puts] == [tinygrad]

  def test_previous_version_slot_is_reset(self):
    """A slot saved by a chunked-manifest client (selector 19) is dropped, never downloaded as-is."""
    stale = self._raw_bundle("small")
    stale["minimumSelectorVersion"] = helpers.REQUIRED_JSON_VERSION - 1
    params = self._params(qcom=stale)
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      validate_active_bundles(params, {"qcom": [], "chestnut": []})
    params.remove.assert_called_once_with("ModelManager_ActiveBundle")


class TestActiveBundleSelection(OpenpilotTestCase):
  """The effective active bundle is the active source's slot: chestnut when a GPU is
  present, qcom otherwise. An empty active slot means the hardware default (stock
  runner), never the other slot's pick - modeld_v2 requires a real bundle."""

  @staticmethod
  def _raw_bundle(ref: str) -> dict:
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.ref = ref
    bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
    return bundle.to_dict()

  def _params(self, qcom=None, chestnut=None):
    params = mock.MagicMock()

    def get(key, *args, **kwargs):
      if key == "ModelManager_ActiveBundle":
        return qcom
      if key == "ModelManager_ActiveBundleChestnut":
        return chestnut
      return None

    params.get.side_effect = get
    return params

  def test_selected_bundle_is_per_slot(self):
    params = self._params(qcom=self._raw_bundle("small"), chestnut=self._raw_bundle("big"))
    assert get_selected_bundle(params, "qcom").ref == "small"
    assert get_selected_bundle(params, "chestnut").ref == "big"

  def test_no_gpu_uses_qcom_slot(self):
    params = self._params(qcom=self._raw_bundle("small"), chestnut=self._raw_bundle("big"))
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      assert get_active_bundle(params).ref == "small"

  def test_gpu_uses_chestnut_slot(self):
    params = self._params(qcom=self._raw_bundle("small"), chestnut=self._raw_bundle("big"))
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      assert get_active_bundle(params).ref == "big"

  def test_gpu_without_big_selection_is_hardware_default(self):
    params = self._params(qcom=self._raw_bundle("small"), chestnut=None)
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      assert get_active_bundle(params) is None


class TestEffectiveSource(OpenpilotTestCase):
  """One gate decides the active source. With no flags it is runtime truth (GPU
  attached); display callers (mici) pass the ui_state flags, which additionally
  require the big model to be loading, active, or the device offroad. The active
  bundle is simply the selected bundle of that source."""

  @staticmethod
  def _raw_bundle(ref: str) -> dict:
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.ref = ref
    bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
    return bundle.to_dict()

  def test_runtime_no_gpu(self):
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      assert get_active_source() == "qcom"

  def test_runtime_gpu_present(self):
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      assert get_active_source() == "chestnut"

  def test_display_offroad_gpu_present_shows_big(self):
    assert get_active_source(chestnut=True, chestnut_active=False, chestnut_loading=False, offroad=True) == "chestnut"

  def test_display_onroad_gpu_loading_shows_big(self):
    assert get_active_source(chestnut=True, chestnut_active=False, chestnut_loading=True, offroad=False) == "chestnut"

  def test_display_onroad_gpu_active_shows_big(self):
    assert get_active_source(chestnut=True, chestnut_active=True, chestnut_loading=False, offroad=False) == "chestnut"

  def test_display_onroad_gpu_idle_shows_small(self):
    assert get_active_source(chestnut=True, chestnut_active=False, chestnut_loading=False, offroad=False) == "qcom"

  def test_display_active_none_is_idle(self):
    assert get_active_source(chestnut=True, chestnut_active=None, chestnut_loading=False, offroad=False) == "qcom"

  def test_active_bundle_follows_source(self):
    params = mock.MagicMock()
    params.get.side_effect = lambda key: {"ModelManager_ActiveBundle": self._raw_bundle("small"),
                                          "ModelManager_ActiveBundleChestnut": self._raw_bundle("big")}.get(key)
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      assert get_active_bundle(params).ref == "small"
    assert get_selected_bundle(params, get_active_source(chestnut=True, chestnut_active=False,
                                                         chestnut_loading=False, offroad=True)).ref == "big"


@unittest.skipUnless(os.environ.get('RUN_INTEGRATION_TESTS'), 'requires external network')
class TestLiveModelManifest(OpenpilotTestCase):
  """Every artifact in the published manifests must be a reachable whole file that honors byte
  ranges, which the parallel downloader depends on."""

  def test_all_manifest_urls_available(self):
    session = requests.Session()
    dead = []

    for manifest_url in (ModelFetcher.MODEL_URL, ModelFetcher.MODEL_URL_CHESTNUT):
      manifest = requests.get(manifest_url, timeout=30).json()
      for bundle in manifest.get('bundles', []):
        # a build-all manifest starts as a copy of the previous one: entries still at the old
        # selector version are never loaded by this client, so they are not checked either
        if str(bundle.get('minimum_selector_version', '')).strip() != str(helpers.REQUIRED_JSON_VERSION):
          continue
        for model in bundle.get('models', []):
          artifact = model['artifact']
          if artifact.get('chunks'):
            dead.append(f"{bundle.get('short_name')}: still chunked {artifact['file_name']}")
          url = artifact['download_uri']['url']
          try:
            with session.get(url, headers={'Range': 'bytes=0-0'}, stream=True, timeout=15, allow_redirects=True) as r:
              if r.status_code != 206:
                dead.append(f"{bundle.get('short_name')}: HTTP {r.status_code} (expected 206) {url}")
          except requests.RequestException as e:
            dead.append(f"{bundle.get('short_name')}: {type(e).__name__} {url}")

    assert not dead, "unusable model URLs:\n" + "\n".join(dead)


if __name__ == '__main__':
  unittest.main()
