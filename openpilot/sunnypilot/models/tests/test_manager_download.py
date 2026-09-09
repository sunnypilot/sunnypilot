"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import contextlib
import hashlib
import http.server
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
from urllib3.connectionpool import HTTPConnectionPool

from openpilot.cereal import custom
from openpilot.common.test import OpenpilotTestCase
from openpilot.common.file_chunker import get_chunk_name, get_manifest_path
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
# a legacy chunked entry, served by path; goes with the chunked download path
CHUNK_BODIES = [b'A' * 5000, b'B' * 5000, b'C' * 3000]


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def piece_range(index: int) -> tuple[int, int]:
  """Inclusive byte range the client is expected to request for piece `index`."""
  start = index * PIECE
  return start, min(start + PIECE, len(WHOLE_BODY)) - 1


class DownloadHandler(http.server.BaseHTTPRequestHandler):
  """Serves WHOLE_BODY with byte-range support. Class attributes are reset per test."""
  request_ranges: list[tuple[int, int] | None] = []  # None: no (honoured) Range header
  fail_ranges: dict[tuple[int, int], int] = {}  # range -> HTTP status, every time
  fail_once: set[tuple[int, int]] = set()  # ranges that 503 on their first request only
  fail_times: dict[tuple[int, int], int] = {}  # range -> how many more requests 503 before it succeeds
  stall_ranges: set[tuple[int, int]] = set()
  stall_event: threading.Event | None = None
  stall_released_by_event: bool | None = None
  support_ranges = True
  corrupt = False
  request_paths: list[str] = []  # every path requested, chunk or whole
  fail_paths: dict[str, int] = {}  # chunk path -> HTTP status

  def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
    pass

  def do_GET(self):
    cls = type(self)
    cls.request_paths.append(self.path)
    if self.path in cls.fail_paths:
      self.send_response(cls.fail_paths[self.path])
      self.end_headers()
      return
    for i, chunk in enumerate(CHUNK_BODIES):
      if self.path.endswith(get_chunk_name('', i, len(CHUNK_BODIES))):
        self.send_response(200)
        self.send_header('Content-Length', str(len(chunk)))
        self.end_headers()
        self.wfile.write(chunk)
        return
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
    if cls.fail_times.get(rng, 0) > 0:
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
    DownloadHandler.request_paths = []
    DownloadHandler.fail_paths = {}

    self._tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self._tmp.cleanup)
    self.dest = self._tmp.name

    for name, value in (('PIECE_SIZE', PIECE), ('REPORT_INTERVAL', 0.05), ('PIECE_BACKOFF', 0.01)):
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

  def make_artifact(self, chunked: bool = False):
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.init('models', 1)
    artifact = bundle.models[0].artifact
    artifact.fileName = FILE_NAME
    artifact.downloadUri.uri = self.base_url + '/' + FILE_NAME
    if chunked:  # a legacy manifest entry: the whole file's hash plus one per chunk
      artifact.downloadUri.sha256 = sha256(b''.join(CHUNK_BODIES))
      artifact.init('chunks', len(CHUNK_BODIES))
      for i, body in enumerate(CHUNK_BODIES):
        artifact.chunks[i].sha256 = sha256(body)
    else:
      artifact.downloadUri.sha256 = sha256(WHOLE_BODY)
    self._bundle = bundle
    self.artifact = artifact
    return artifact

  @property
  def path(self) -> str:
    return os.path.join(self.dest, FILE_NAME)

  @staticmethod
  def piece_requests() -> list[tuple[int, int]]:
    """Honoured ranges minus the one-byte size probe."""
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
    self.run_with_server(body)

  def test_http_error_propagates(self):
    def body():
      DownloadHandler.fail_ranges = {piece_range(1): 404}
      with self.assertRaises(requests.exceptions.HTTPError):
        self.download_file()
    self.run_with_server(body)

  def test_transient_error_is_retried(self):
    def body():
      DownloadHandler.fail_once = {piece_range(2)}
      self.download_file()
      assert self.read_path() == WHOLE_BODY
      assert self.piece_requests().count(piece_range(2)) == 2
    self.run_with_server(body)

  def test_cancellation_via_download_ref(self):
    """Removing DownloadRef mid-transfer cancels the download. One piece is held back so the transfer
    spans several reporter ticks; the ref vanishes on the second."""
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
      assert DownloadHandler.stall_released_by_event is True, "the cancel must have caught the piece mid-transfer"
    self.run_with_server(body)

  def test_replaced_download_ref_queues_instead_of_cancelling(self):
    """Selecting another model mid-transfer lets the running download finish."""
    def body():
      self.manager.params.get.side_effect = lambda key: b"other-ref" if key == "ModelManager_DownloadRef" else None
      self.manager._download_ref = b"ref"
      self.download_file()
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


class TestChunkedDownload(ManagerDownloadTestBase):
  """The chunked download path, still used by the manifests before selector version 20."""

  def test_download_chunked_writes_all_chunks_and_manifest(self):
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))

      for i, expected in enumerate(CHUNK_BODIES):
        with open(get_chunk_name(base_path, i, len(CHUNK_BODIES)), 'rb') as f:
          assert f.read() == expected, f"chunk {i} body mismatch"

      with open(get_manifest_path(base_path)) as f:
        assert f.read() == str(len(CHUNK_BODIES))

      assert not os.path.isfile(base_path), "base file should be removed after chunking"
      assert artifact.fileName not in self.manager._download_start_times
    self.run_with_server(body)

  def test_progress_is_monotonic_and_bounded(self):
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))

      assert self.reported, "expected progress reports"
      for a, b in zip(self.reported, self.reported[1:], strict=False):
        assert b >= a, f"progress went backwards: {a} -> {b}"
      assert max(self.reported) <= 99.0, f"chunked progress must stay <=99 until verify, got {max(self.reported)}"
    self.run_with_server(body)

  def test_session_is_reused_across_chunks(self):
    """One connection pool shared across every chunk."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)

      pools = []
      original = HTTPConnectionPool.urlopen

      def tracked(pool_self, *args, **kwargs):
        pools.append(id(pool_self))
        return original(pool_self, *args, **kwargs)

      with mock.patch.object(HTTPConnectionPool, 'urlopen', tracked):
        asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))

      assert len(pools) == len(CHUNK_BODIES), f"expected one request per chunk, got {len(pools)}"
      assert len(set(pools)) == 1, f"connection pool not reused across chunks: {len(set(pools))} pools"
    self.run_with_server(body)

  def test_http_error_propagates(self):
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      failing = '/' + os.path.basename(get_chunk_name(artifact.downloadUri.uri, 1, len(CHUNK_BODIES)))
      DownloadHandler.fail_paths = {failing: 404}

      with self.assertRaises(requests.exceptions.HTTPError):
        asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))

      # chunk 1 failed, so its file and the manifest must not exist
      assert not os.path.isfile(get_chunk_name(base_path, 1, len(CHUNK_BODIES)))
      assert not os.path.isfile(get_manifest_path(base_path))
    self.run_with_server(body)

  def test_cancellation_mid_transfer(self):
    """Cancellation is checked inside the byte loop; it must still fire after the port."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      self.manager.params.get.return_value = None  # cancelled

      with self.assertRaises(Exception) as ctx:
        asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))
      assert 'cancelled' in str(ctx.exception).lower()
      assert not os.path.isfile(get_manifest_path(base_path))
    self.run_with_server(body)

  def test_repeat_downloads_are_stable(self):
    """Back-to-back runs must produce identical bytes and leak no start-time state."""
    def body():
      for _ in range(2):
        artifact = self.make_artifact(chunked=True)
        base_path = os.path.join(self.dest, artifact.fileName)
        asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))
        for i, expected in enumerate(CHUNK_BODIES):
          with open(get_chunk_name(base_path, i, len(CHUNK_BODIES)), 'rb') as f:
            assert f.read() == expected
        assert self.manager._download_start_times == {}
    self.run_with_server(body)

  def test_download_ref_present_keeps_download_alive(self):
    """A pending download request (DownloadRef set) must not be cancelled mid-transfer."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      self.manager.params.get.side_effect = lambda key: b"ref" if key == "ModelManager_DownloadRef" else None
      self.manager._download_ref = b"ref"
      asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))
      assert os.path.isfile(get_manifest_path(base_path))
    self.run_with_server(body)

  def test_cancellation_via_download_ref(self):
    """Removing DownloadRef mid-transfer cancels the download."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      checks = {"n": 0}

      def get(key):
        if key == "ModelManager_DownloadRef":
          checks["n"] += 1
          return b"ref" if checks["n"] <= 2 else None
        return b"0"

      self.manager.params.get.side_effect = get
      self.manager._download_ref = b"ref"
      with self.assertRaises(Exception) as ctx:
        asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))
      assert 'cancelled' in str(ctx.exception).lower()
      assert not os.path.isfile(get_manifest_path(base_path))
    self.run_with_server(body)

  def test_replaced_download_ref_queues_instead_of_cancelling(self):
    """Selecting another model mid-transfer lets the running download finish."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      self.manager.params.get.side_effect = lambda key: b"other-ref" if key == "ModelManager_DownloadRef" else None
      self.manager._download_ref = b"ref"
      asyncio.run(self.manager._download_chunked(artifact.downloadUri.uri, base_path, artifact))
      assert os.path.isfile(get_manifest_path(base_path))
    self.run_with_server(body)

  def test_resume_skips_valid_chunks(self):
    """A chunk already on disk is kept and not re-downloaded; progress starts above its share."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      with open(get_chunk_name(base_path, 0, len(CHUNK_BODIES)), 'wb') as f:
        f.write(CHUNK_BODIES[0])

      asyncio.run(self.manager._process_artifact(artifact, self.dest))

      chunk0_suffix = get_chunk_name('', 0, len(CHUNK_BODIES))
      assert not any(p.endswith(chunk0_suffix) for p in DownloadHandler.request_paths), "valid chunk was re-downloaded"
      for i, expected in enumerate(CHUNK_BODIES):
        with open(get_chunk_name(base_path, i, len(CHUNK_BODIES)), 'rb') as f:
          assert f.read() == expected
      assert os.path.isfile(get_manifest_path(base_path))
      assert min(self.reported) >= (1 / len(CHUNK_BODIES)) * 100 - 1, "progress must not restart below the resumed share"
    self.run_with_server(body)

  def test_verify_reports_valid_fraction_then_cached(self):
    """A fully cached bundle publishes climbing verify progress and ends cached."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      for i, data in enumerate(CHUNK_BODIES):
        with open(get_chunk_name(base_path, i, len(CHUNK_BODIES)), 'wb') as f:
          f.write(data)

      asyncio.run(self.manager._process_artifact(artifact, self.dest))

      assert DownloadHandler.request_paths == [], "cached bundle must not hit the network"
      assert [round(p) for p in self.reported[:3]] == [33, 67, 100]
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.cached
    self.run_with_server(body)


class TestProcessArtifact(ManagerDownloadTestBase):
  """Verification and cleanup around the download."""

  def test_downloaded_file_verifies_and_ends_idle(self):
    def body():
      artifact = self.make_artifact()
      asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert self.read_path() == WHOLE_BODY
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.downloaded
      assert artifact.downloadProgress.progress == 100
      assert artifact.downloadProgress.eta == 0
    self.run_with_server(body)

  def test_hash_mismatch_discards_file_and_parts(self):
    def body():
      DownloadHandler.corrupt = True
      artifact = self.make_artifact()
      with self.assertRaises(ValueError):
        asyncio.run(self.manager._process_artifact(artifact, self.dest))
      assert not os.path.isfile(self.path)
      assert artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed
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
  """Minimal manifest bundle dict, version-compatible (no chunks to avoid disk side effects).
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
      "type": "supercombo",
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
  """Every artifact and chunk URL in the published manifest must resolve."""

  def test_all_manifest_urls_available(self):
    from openpilot.sunnypilot.models.fetcher import ModelFetcher

    manifest = requests.get(ModelFetcher.MODEL_URL, timeout=30).json()
    session = requests.Session()
    dead = []

    for bundle in manifest.get('bundles', []):
      for model in bundle.get('models', []):
        artifact = model['artifact']
        url = artifact['download_uri']['url']
        chunks = artifact.get('chunks', [])
        urls = ([url] if not chunks
                else [get_chunk_name(url, i, len(chunks)) for i in range(len(chunks))])
        for u in urls:
          try:
            r = session.head(u, timeout=15, allow_redirects=True)
            if r.status_code != 200:
              dead.append(f"{bundle.get('short_name')}: HTTP {r.status_code} {u}")
          except requests.RequestException as e:
            dead.append(f"{bundle.get('short_name')}: {type(e).__name__} {u}")

    assert not dead, "unreachable model URLs:\n" + "\n".join(dead)


if __name__ == '__main__':
  unittest.main()
