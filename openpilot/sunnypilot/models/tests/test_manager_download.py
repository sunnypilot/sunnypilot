"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import concurrent.futures
import contextlib
import dataclasses
import hashlib
import http.server
import json
import math
import os
import random
import re
import requests
import stat
import tempfile
import threading
import time
import unittest
from typing import Any
from unittest import mock

from openpilot.cereal import custom
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.models import manager as manager_module
from openpilot.sunnypilot.models.fetcher import ModelFetcher, get_cached_bundles
from openpilot.sunnypilot.models import helpers
from openpilot.sunnypilot.models.helpers import (ACTIVE_BUNDLE_KEYS, get_active_bundle, get_active_source, get_selected_bundle,
                                                  resolve_bundle_by_ref, validate_active_bundles)
from openpilot.sunnypilot.models.manager import DownloadCancelled, ModelManagerSP

FILE_NAME = 'driving_test_tinygrad.pkl'
# fixed-seed random bytes: every piece differs, so a misplaced piece changes the file
WHOLE_BODY = random.Random(0).randbytes(10_240)
PIECE_SIZE = 1000  # bytes per test piece -> 11 pieces, the last one short
NUM_PIECES = math.ceil(len(WHOLE_BODY) / PIECE_SIZE)


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


def piece_range(index: int) -> tuple[int, int]:
  start = index * PIECE_SIZE
  return start, min(start + PIECE_SIZE, len(WHOLE_BODY)) - 1


@dataclasses.dataclass
class ServerState:
  request_ranges: list[tuple[int, int] | None] = dataclasses.field(default_factory=list)  # None: no (honored) Range header
  request_encodings: list[str | None] = dataclasses.field(default_factory=list)  # Accept-Encoding of every request
  fail_ranges: dict[tuple[int, int], int] = dataclasses.field(default_factory=dict)  # range -> HTTP status, every time
  fail_times: dict[tuple[int, int], int] = dataclasses.field(default_factory=dict)  # range -> how many more requests 503
  short_once: set[tuple[int, int]] = dataclasses.field(default_factory=set)  # ranges whose first answer is cut short
  stall_ranges: set[tuple[int, int]] = dataclasses.field(default_factory=set)
  stall_event: threading.Event | None = None
  stall_released_by_event: bool | None = None
  support_ranges: bool = True
  corrupt: bool = False


class DownloadHandler(http.server.BaseHTTPRequestHandler):
  state = ServerState()

  def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
    pass

  def do_GET(self):
    state = self.state
    body = WHOLE_BODY
    if state.corrupt:
      # flip every bit of one mid-file byte: same size, so only the hash check can catch it
      body = body[:5000] + bytes([body[5000] ^ 0xFF]) + body[5001:]

    rng = None
    match = re.fullmatch(r'bytes=(\d+)-(\d+)', self.headers.get('Range', ''))
    if match and state.support_ranges:
      rng = (int(match.group(1)), int(match.group(2)))
    state.request_ranges.append(rng)
    state.request_encodings.append(self.headers.get('Accept-Encoding'))

    if rng is not None:
      status = state.fail_ranges.get(rng)
      if status is None and state.fail_times.get(rng, 0) > 0:
        state.fail_times[rng] -= 1
        status = 503
      if status is not None:
        self.send_response(status)
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
      if rng in state.short_once:
        state.short_once.discard(rng)
        payload = payload[:100]
    self.send_header('Content-Length', str(len(payload)))
    self.end_headers()

    if rng in state.stall_ranges:
      # write a little, then hold the connection until the test releases it
      self.wfile.write(payload[:100])
      self.wfile.flush()
      if state.stall_event is not None:
        state.stall_released_by_event = state.stall_event.wait(timeout=5)
      self.wfile.write(payload[100:])
    else:
      self.wfile.write(payload)


@contextlib.contextmanager
def threaded_server(handler):
  server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
  thread = threading.Thread(target=server.serve_forever)
  thread.start()
  try:
    yield f'http://127.0.0.1:{server.server_port}'
  finally:
    server.shutdown()
    server.server_close()
    thread.join()


class InlineExecutor(concurrent.futures.Executor):
  def submit(self, fn, /, *args, **kwargs):
    future: concurrent.futures.Future = concurrent.futures.Future()
    future.set_result(fn(*args, **kwargs))  # the piece lands before the reporter starts
    return future


class ManagerDownloadTestBase(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    self.server = DownloadHandler.state = ServerState()
    self.base_url = self.enterContext(threaded_server(DownloadHandler))

    self._tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self._tmp.cleanup)
    self.dest = self._tmp.name

    for name, value in (('PIECE_SIZE', PIECE_SIZE), ('REPORT_INTERVAL', 0.05), ('PIECE_BACKOFF', 0.01), ('SPEED_FLOOR', 100)):
      self.enterContext(mock.patch.object(manager_module, name, value))

    self.reported: list[float] = []
    self.reported_statuses: list[int] = []
    self.reported_resuming: list[bool] = []

    self.manager = ModelManagerSP.__new__(ModelManagerSP)
    self.params = self.manager.params = mock.MagicMock()
    self.params.get.return_value = b'0'  # not cancelled
    self.manager._download_ref = b'0'
    self.pm = self.manager.pm = mock.MagicMock()
    self.pm.send.side_effect = self._record_progress
    self.manager.selected_bundle = None
    self.manager.active_bundle = None
    self.manager.available_models = []
    self.manager.chestnut_present = False
    self.manager._block_size = 256
    self.manager._download_start_times = {}

  def _record_progress(self, *args) -> None:
    artifact = getattr(self, 'artifact', None)
    if artifact is not None:
      self.reported.append(float(artifact.downloadProgress.progress))
      status = artifact.downloadProgress.status
      self.reported_statuses.append(getattr(status, 'raw', status))  # .raw: _DynamicEnum equals its int but does not hash like it
      self.reported_resuming.append(bool(artifact.downloadProgress.resuming))

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
    with open(self.path, 'wb') as f:
      f.truncate(len(WHOLE_BODY) if file_size is None else file_size)
      for i in done:
        f.seek(i * PIECE_SIZE)
        f.write(WHOLE_BODY[i * PIECE_SIZE:(i + 1) * PIECE_SIZE])
    with open(self.sidecar, 'w') as f:
      json.dump({"total": total, "piece_size": PIECE_SIZE, "ranged": True, "sha256": file_sha256, "done": done}, f)

  def piece_requests(self) -> list[tuple[int, int]]:
    return [r for r in self.server.request_ranges if r is not None and r != (0, 0)]

  def stall(self, index: int) -> threading.Event:
    self.server.stall_ranges = {piece_range(index)}
    self.server.stall_event = threading.Event()
    return self.server.stall_event

  def download_file(self):
    artifact = self.make_artifact()
    asyncio.run(self.manager._download_file(artifact.downloadUri.uri, self.path, artifact))
    return artifact

  def process_artifact(self):
    artifact = self.make_artifact()
    asyncio.run(self.manager._process_artifact(artifact, self.dest))
    return artifact

  def download_bundle(self, source: str):
    asyncio.run(self.manager._download_bundle(self._bundle, self.dest, source))

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
  def test_download(self):
    artifact = self.download_file()
    assert self.read_path() == WHOLE_BODY
    assert sorted(self.piece_requests()) == [piece_range(i) for i in range(NUM_PIECES)], "pieces must tile the file once"
    assert self.server.request_encodings == ['identity'] * (NUM_PIECES + 1), "ranges count encoded bytes, so ask for none"
    assert self.reported and self.reported == sorted(self.reported), "progress only rises"
    assert max(self.reported) <= 99.0, "progress holds below 100 until the hash check"
    assert artifact.fileName not in self.manager._download_start_times
    assert artifact.downloadProgress.speed > 0, "a running download shows its speed"
    assert not os.path.exists(self.sidecar), "the resume state goes once every piece has landed"

  def test_speed_counts_bytes_landed_before_the_first_report(self):
    self.enterContext(mock.patch.object(manager_module, 'ThreadPoolExecutor', lambda max_workers: InlineExecutor()))
    artifact = self.download_file()
    assert artifact.downloadProgress.speed > 0

  def test_eta_comes_from_speed(self):
    artifact = self.make_artifact()
    self.manager._publish_progress(artifact, done_bytes=400, total=1000, speed=100)
    assert artifact.downloadProgress.eta == 6

  def test_stalled_speed_drops_to_zero(self):
    stall_event = self.stall(0)
    seen_speed = threading.Event()

    def release_once_zero(*args):
      if self.artifact.downloadProgress.speed > 0:
        seen_speed.set()
      elif seen_speed.is_set():
        stall_event.set()
    self.pm.send.side_effect = release_once_zero
    self.download_file()
    assert self.server.stall_released_by_event is True, "the stalled speed never reached exactly 0"
    assert self.artifact.downloadProgress.speed > 0, "the speed must recover once data flows again"

  def test_pieces_download_in_parallel(self):
    stall_event = self.stall(0)
    others = {piece_range(i) for i in range(1, NUM_PIECES)}

    def release_when_others_requested():
      deadline = time.monotonic() + 5
      while time.monotonic() < deadline:
        if others <= set(self.piece_requests()):
          stall_event.set()
          return
        time.sleep(0.01)

    threading.Thread(target=release_when_others_requested).start()
    self.download_file()
    assert self.server.stall_released_by_event is True, "other pieces did not download while one was stalled"

  def test_fallback_when_server_ignores_ranges(self):
    self.server.support_ranges = False
    self.download_file()
    assert self.read_path() == WHOLE_BODY
    assert self.server.request_ranges == [None, None], "expected the probe plus one whole-body request"
    assert self.server.request_encodings == ['identity', 'identity']

  def test_transient_failures_are_retried(self):
    self.server.fail_times = {piece_range(2): 1}
    self.server.short_once = {piece_range(4)}
    self.download_file()
    assert self.read_path() == WHOLE_BODY
    assert self.piece_requests().count(piece_range(2)) == 2
    assert self.piece_requests().count(piece_range(4)) == 2

  def test_permanent_failure_is_not_retried(self):
    self.server.fail_ranges = {piece_range(1): 404}
    with self.assertRaises(requests.exceptions.HTTPError):
      self.process_artifact()
    assert self.piece_requests().count(piece_range(1)) == 1
    done = self.resume_state()["done"]
    assert os.path.isfile(self.path) and done and 1 not in done

  def test_removing_download_ref_cancels(self):
    stall_event = self.stall(3)
    refs = iter([b"ref"])
    self.params.get.side_effect = lambda key: next(refs, None)  # removed after the first poll
    self.manager._download_ref = b"ref"

    def release_once_canceling(*args):
      # the "canceling" report comes after the cancel event is set, so the piece can't finish first
      if self.artifact.downloadProgress.canceling:
        stall_event.set()
    self.pm.send.side_effect = release_once_canceling
    with self.assertRaises(DownloadCancelled):
      self.download_file()
    assert self.server.stall_released_by_event is True, "the cancel must have caught the piece mid-transfer"
    end = piece_range(3)[1] + 1
    assert self.read_path()[end - 100:end] == bytes(100), "the cancelled piece must stop before its last bytes land"
    done = self.resume_state()["done"]
    assert done and 3 not in done, "a cancel records the finished pieces, and only those, for resume"

  def test_resume_skips_complete_pieces(self):
    self.write_resume_state(done=[0, 4])
    self.download_file()
    assert piece_range(0) not in self.piece_requests() and piece_range(4) not in self.piece_requests()
    assert self.read_path() == WHOLE_BODY
    assert min(self.reported) >= 2 * PIECE_SIZE / len(WHOLE_BODY) * 100 - 1, "progress must not restart below the resumed share"

  def test_unusable_resume_state_starts_over(self):
    def malformed(content: bytes):
      self.write_resume_state(done=[0])
      with open(self.sidecar, 'wb') as f:
        f.write(content)

    layout = {"total": len(WHOLE_BODY), "piece_size": PIECE_SIZE, "ranged": True, "sha256": sha256(WHOLE_BODY)}
    cases = {
      "other size": lambda: self.write_resume_state(done=[0], total=len(WHOLE_BODY) + 1),
      "other bytes": lambda: self.write_resume_state(done=[0], file_sha256="0" * 64),
      "truncated file": lambda: self.write_resume_state(done=[0], file_size=PIECE_SIZE),
      "not an object": lambda: malformed(b'[]'),
      "cut-off json": lambda: malformed(b'{"total": '),
      "done not a list": lambda: malformed(json.dumps({**layout, "done": 3}).encode()),
      "done not ints": lambda: malformed(json.dumps({**layout, "done": ["0", None]}).encode()),
    }
    for name, write_state in cases.items():
      with self.subTest(name):
        self.server.request_ranges = []
        write_state()
        self.download_file()
        assert sorted(self.piece_requests()) == [piece_range(i) for i in range(NUM_PIECES)], "every piece is fetched again"
        assert self.read_path() == WHOLE_BODY

  def test_pieces_and_resume_state_are_synced_to_disk(self):
    real_fsync, synced = os.fsync, []

    def record_sync(fd):
      st = os.fstat(fd)
      synced.append("dir" if stat.S_ISDIR(st.st_mode) else "model" if st.st_ino == os.stat(self.path).st_ino else "sidecar")
      real_fsync(fd)
    with mock.patch.object(manager_module.os, 'fsync', side_effect=record_sync):
      self.download_file()
    assert synced.count("model") == NUM_PIECES, f"expected one fsync per piece, got {synced.count('model')}"
    assert "sidecar" in synced and "dir" in synced, "sidecar file and directory must be fsync'd"

  def test_replaced_download_ref_queues_instead_of_canceling(self):
    self.params.get.return_value = b"other-ref"
    self.manager._download_ref = b"ref"
    self.download_file()
    assert self.read_path() == WHOLE_BODY


class TestProcessArtifact(ManagerDownloadTestBase):
  def test_download_writes_only_its_slot(self):
    ds = custom.ModelManagerSP.DownloadStatus
    for source, other in (("qcom", "chestnut"), ("chestnut", "qcom")): # bernoulli
      with self.subTest(source=source):
        self.make_artifact()
        self._bundle.ref = f"{source}-ref"
        self._bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
        self.manager.params, store = self._make_params_with_store()
        self.download_bundle(source)
        assert ACTIVE_BUNDLE_KEYS[source] in store and ACTIVE_BUNDLE_KEYS[other] not in store
        assert self.manager.selected_bundle.status == ds.downloaded
        assert self.artifact.downloadProgress.progress == 100
        assert self.artifact.downloadProgress.eta == 0 and self.artifact.downloadProgress.speed == 0
        assert self.read_path() == WHOLE_BODY
        os.remove(self.path)

  def test_hash_mismatch_discards_file(self):
    self.server.corrupt = True
    with self.assertRaises(ValueError):
      self.process_artifact()
    assert not os.path.isfile(self.path) and not os.path.exists(self.sidecar), "a corrupt file must not be resumed from"
    assert self.artifact.downloadProgress.status == custom.ModelManagerSP.DownloadStatus.failed

  def test_interrupted_download_resumes_without_reverifying(self):
    self.write_resume_state(done=[0, 1, 2])
    artifact = self.process_artifact()
    ds = custom.ModelManagerSP.DownloadStatus
    assert self.reported_statuses[0] == ds.downloading, "an in-progress download is not verified first"
    assert piece_range(0) not in self.piece_requests()
    assert artifact.downloadProgress.status == ds.downloaded
    assert any(self.reported_resuming), "a resumed download is flagged resuming until its first progress report"
    assert not artifact.downloadProgress.resuming

  def test_probe_failure_moves_past_verifying(self):
    self.server.fail_ranges = {(0, 0): 404}  # the size probe
    with self.assertRaises(requests.exceptions.HTTPError):
      self.process_artifact()
    ds = custom.ModelManagerSP.DownloadStatus
    assert self.reported_statuses == [ds.verifying, ds.downloading, ds.failed]

  def test_cached_file_skips_network(self):
    with open(self.path, 'wb') as f:
      f.write(WHOLE_BODY)
    self.process_artifact()
    assert self.server.request_ranges == [], "cached file must not hit the network"
    ds = custom.ModelManagerSP.DownloadStatus
    assert self.reported_statuses == [ds.verifying, ds.cached]

  def test_cached_bundle_cancel_skips_slot_write(self):
    with open(self.path, 'wb') as f:
      f.write(WHOLE_BODY)
    self.make_artifact()
    self.manager.params, store = self._make_params_with_store()
    store["ModelManager_DownloadRef"] = None  # removed -> cancelled
    self.manager._download_ref = b"ref"
    with self.assertRaises(DownloadCancelled):
      self.download_bundle("qcom")
    assert ACTIVE_BUNDLE_KEYS["qcom"] not in store
    assert os.path.isfile(self.path), "cancel must not delete a cached model"

  def test_download_ref_is_released_only_if_unchanged(self):
    for current, removed in ((b"new-ref", False), (b"ref", True)):
      self.params = self.manager.params = mock.MagicMock()
      self.params.get.return_value = current
      self.manager._download_ref = b"ref"
      self.manager._release_download_ref()
      assert self.params.remove.called == removed


def raw_bundle(ref: str, runner: int | None = None) -> dict:
  bundle = custom.ModelManagerSP.ModelBundle.new_message()
  bundle.ref = ref
  bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
  if runner is not None:
    bundle.runner = runner
  return bundle.to_dict()


class TestResolveBundleByRef(OpenpilotTestCase):
  def test_ref_resolves_to_its_slot(self):
    small, big = (custom.ModelManagerSP.ModelBundle(**raw_bundle(ref)) for ref in ("small", "big"))
    catalog = {"qcom": [small], "chestnut": [big]}
    assert resolve_bundle_by_ref("small", catalog) == (small, "qcom")
    assert resolve_bundle_by_ref("big", catalog) == (big, "chestnut")
    assert resolve_bundle_by_ref("nope", catalog) is None


def manifest_bundle(short_name: str, ref: str, index: int = 0, is_big: bool = False) -> dict:
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


def manifest_params(qcom_manifest, chestnut_manifest=None):
  values = {
    "ModelManager_ModelsCache": qcom_manifest,
    "ModelManager_ModelsCache_Chestnut": chestnut_manifest or {"bundles": [manifest_bundle("big", "bbb", is_big=True)]},
    "ModelManager_LastSyncTime": int(time.monotonic() * 1e9),
    "ModelManager_LastSyncTime_Chestnut": int(time.monotonic() * 1e9),
  }
  params = mock.MagicMock()
  params.get.side_effect = values.get
  return params


class TestModelFetcher(OpenpilotTestCase):
  def refetch(self, fetcher, *bundles):
    fetched = fetcher.model_parser.parse_models({"bundles": list(bundles)})
    return mock.patch.object(fetcher, "_fetch_and_cache_models", return_value=fetched)

  def test_active_source_follows_chestnut_presence(self):
    assert ModelFetcher.active_source(False) == "qcom"
    assert ModelFetcher.active_source(True) == "chestnut"

  def test_unknown_source_has_no_bundles(self):
    assert ModelFetcher(mock.MagicMock()).get_bundles_for_source("bogus") == []
    assert get_cached_bundles(mock.MagicMock(), "bogus") == []

  def test_get_cached_bundles_reads_its_source(self):
    params = manifest_params({"bundles": [manifest_bundle("small", "aaa")]})
    assert [b.ref for b in get_cached_bundles(params, "qcom")] == ["aaa"]
    assert [b.ref for b in get_cached_bundles(params, "chestnut")] == ["bbb"]

  def test_active_json_has_both_urls(self):
    params = mock.MagicMock()
    ModelFetcher(params)
    params.put.assert_any_call("ModelManager_ActiveJson", {"qcom": ModelFetcher.MODEL_URL, "chestnut": ModelFetcher.MODEL_URL_CHESTNUT}, block=True)

  def test_matching_caches_are_used_without_fetch(self):
    fetcher = ModelFetcher(manifest_params({"bundles": [manifest_bundle("small", "aaa")]}))
    with mock.patch.object(fetcher, "_fetch_and_cache_models", side_effect=AssertionError("cache should be used")):
      assert [bundle.ref for bundle in fetcher.get_bundles_for_source("qcom")] == ["aaa"]
      assert [bundle.ref for bundle in fetcher.get_bundles_for_source("chestnut")] == ["bbb"]

  def test_unusable_cache_is_refetched(self):
    stale = {**manifest_bundle("small", "aaa"), "minimum_selector_version": "16"}  # parses to zero valid bundles
    corrupt = {"short_name": "broken"}  # missing required fields
    for cached in (stale, corrupt):
      with self.subTest(cached=cached):
        fetcher = ModelFetcher(manifest_params({"bundles": [cached]}))
        with self.refetch(fetcher, manifest_bundle("small2", "ddd")) as fetch:
          assert [bundle.ref for bundle in fetcher.get_bundles_for_source("qcom")] == ["ddd"]
        fetch.assert_called_once_with("qcom")

  def test_mismatched_cache_is_refetched_once(self):
    fetcher = ModelFetcher(manifest_params({"bundles": [manifest_bundle("big", "bbb", is_big=True)]}))
    with self.refetch(fetcher, manifest_bundle("big", "bbb", is_big=True)) as fetch:
      first = fetcher.get_bundles_for_source("qcom")
      second = fetcher.get_bundles_for_source("qcom")
    fetch.assert_called_once_with("qcom")
    assert [bundle.ref for bundle in first] == [bundle.ref for bundle in second] == ["bbb"]


def ref_of(bundle) -> str | None:
  return None if bundle is None else bundle.ref


def slot_params(qcom=None, chestnut=None):
  params = mock.MagicMock()
  params.get.side_effect = {"ModelManager_ActiveBundle": qcom, "ModelManager_ActiveBundleChestnut": chestnut}.get
  return params


class TestActiveBundle(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    helpers._LAST_VALIDATED_RAW.clear()

  def test_active_source(self):
    for gpu, source in ((False, "qcom"), (True, "chestnut")):
      with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=gpu):
        assert get_active_source() == source
    for state, source in (
      ((True, False, False, True), "chestnut"),  # offroad
      ((True, False, True, False), "chestnut"),  # onroad, big model loading
      ((True, True, False, False), "chestnut"),  # onroad, big model running
      ((True, False, False, False), "qcom"),  # onroad, big model idle
      ((True, None, False, False), "qcom"),  # onroad, big model state not known yet
      ((False, False, False, True), "qcom"),  # offroad, no GPU
    ):
      chestnut, active, loading, offroad = state
      assert get_active_source(chestnut=chestnut, chestnut_active=active, chestnut_loading=loading, offroad=offroad) == source, state

  def test_active_bundle_is_the_active_slot(self):
    params = slot_params(qcom=raw_bundle("small"), chestnut=raw_bundle("big"))
    assert ref_of(get_selected_bundle(params, "qcom")) == "small"
    assert ref_of(get_selected_bundle(params, "chestnut")) == "big"
    for gpu, ref in ((False, "small"), (True, "big")):
      with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=gpu):
        assert ref_of(get_active_bundle(params)) == ref
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      assert get_active_bundle(slot_params(qcom=raw_bundle("small"))) is None, \
        "an empty chestnut slot must not fall back to the qcom pick"

  def test_empty_catalog_does_not_reset_slot(self):
    params = slot_params(qcom=raw_bundle("small"))
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=False):
      validate_active_bundles(params, {"qcom": [], "chestnut": []})
    params.remove.assert_not_called()

  def test_reset_recomputes_runner_from_surviving_slot(self):
    tinygrad = int(custom.ModelManagerSP.Runner.tinygrad)
    big_raw = raw_bundle("big", runner=tinygrad)
    params = slot_params(qcom=raw_bundle("gone"), chestnut=big_raw)
    catalog = {"qcom": [custom.ModelManagerSP.ModelBundle(**raw_bundle("other"))],
               "chestnut": [custom.ModelManagerSP.ModelBundle(**big_raw)]}
    with mock.patch("openpilot.sunnypilot.models.helpers.chestnut_present", return_value=True):
      validate_active_bundles(params, catalog)
    params.remove.assert_called_once_with("ModelManager_ActiveBundle")
    params.put.assert_called_once_with("ModelRunnerTypeCache", tinygrad, block=True)


@unittest.skipUnless(os.environ.get('RUN_INTEGRATION_TESTS'), 'requires external network')
class TestLiveModelManifest(OpenpilotTestCase):
  def test_all_manifest_urls_available(self):
    from openpilot.sunnypilot.models.fetcher import ModelFetcher

    manifest = requests.get(ModelFetcher.MODEL_URL, timeout=30).json()
    session = requests.Session()
    dead = []

    for bundle in manifest.get('bundles', []):
      for model in bundle.get('models', []):
        artifact = model['artifact']
        url = artifact['download_uri']['url']
        try:
          r = session.head(url, timeout=15, allow_redirects=True)
          if r.status_code != 200:
            dead.append(f"{bundle.get('short_name')}: HTTP {r.status_code} {url}")
        except requests.RequestException as e:
          dead.append(f"{bundle.get('short_name')}: {type(e).__name__} {url}")
    assert not dead, "unreachable model URLs:\n" + "\n".join(dead)


if __name__ == '__main__':
  unittest.main()
