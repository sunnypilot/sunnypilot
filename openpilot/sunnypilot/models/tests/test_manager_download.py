"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import hashlib
import http.server
import os
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
from openpilot.selfdrive.test.helpers import http_server_context
from openpilot.sunnypilot.models import manager as manager_module
from openpilot.sunnypilot.models.fetcher import ModelFetcher, get_cached_bundles
from openpilot.sunnypilot.models import helpers
from openpilot.sunnypilot.models.helpers import (get_active_bundle, get_active_source, get_selected_bundle,
                                                  resolve_bundle_by_ref, validate_active_bundles)
from openpilot.sunnypilot.models.manager import ModelManagerSP

CHUNK_BODIES = [b'A' * 5000, b'B' * 5000, b'C' * 3000]
WHOLE_BODY = b'Z' * 9000


def sha256(data: bytes) -> str:
  return hashlib.sha256(data).hexdigest()


class DownloadHandler(http.server.BaseHTTPRequestHandler):
  """Serves the fixture bodies. Class attributes are reset per test."""
  request_paths: list[str] = []
  fail_paths: dict[str, int] = {}
  stall_paths: set[str] = set()
  stall_event: threading.Event | None = None

  def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
    pass

  def _body_for(self, path):
    if path.endswith('.whole'):
      return WHOLE_BODY
    for i in range(len(CHUNK_BODIES)):
      if path.endswith(get_chunk_name('', i, len(CHUNK_BODIES))):
        return CHUNK_BODIES[i]
    return None

  def do_GET(self):
    type(self).request_paths.append(self.path)

    status = type(self).fail_paths.get(self.path)
    if status:
      self.send_response(status)
      self.end_headers()
      return

    body = self._body_for(self.path)
    if body is None:
      self.send_response(404)
      self.end_headers()
      return

    self.send_response(200)
    self.send_header('Content-Length', str(len(body)))
    self.end_headers()

    if self.path in type(self).stall_paths:
      # write a little, then wait so the test can cancel mid-transfer
      self.wfile.write(body[:100])
      self.wfile.flush()
      if type(self).stall_event is not None:
        type(self).stall_event.wait(timeout=5)
      self.wfile.write(body[100:])
    else:
      self.wfile.write(body)


class ManagerDownloadTestBase(OpenpilotTestCase):
  def setUp(self):
    super().setUp()
    DownloadHandler.request_paths = []
    DownloadHandler.fail_paths = {}
    DownloadHandler.stall_paths = set()
    DownloadHandler.stall_event = None

    self._tmp = tempfile.TemporaryDirectory()
    self.addCleanup(self._tmp.cleanup)
    self.dest = self._tmp.name

    self.reported: list[float] = []

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
    self.manager._chunk_size = 1024
    self.manager._download_start_times = {}

  def _record_progress(self, *args) -> None:
    """Runs on every real _report_status send."""
    artifact = getattr(self, 'artifact', None)
    if artifact is not None:
      self.reported.append(float(artifact.downloadProgress.progress))

  def make_artifact(self, chunked: bool):
    bundle = custom.ModelManagerSP.ModelBundle.new_message()
    bundle.init('models', 1)
    artifact = bundle.models[0].artifact
    artifact.fileName = 'driving_test_tinygrad.pkl'
    if chunked:
      artifact.downloadUri.uri = self.base_url + '/driving_test_tinygrad.pkl'
      artifact.downloadUri.sha256 = sha256(b''.join(CHUNK_BODIES))
      artifact.init('chunks', len(CHUNK_BODIES))
      for i, body in enumerate(CHUNK_BODIES):
        artifact.chunks[i].sha256 = sha256(body)
    else:
      artifact.downloadUri.uri = self.base_url + '/driving_test_tinygrad.pkl.whole'
      artifact.downloadUri.sha256 = sha256(WHOLE_BODY)
    self._bundle = bundle
    self.artifact = artifact
    return artifact

  def chunk_paths(self, base_path):
    return [get_chunk_name(base_path, i, len(CHUNK_BODIES)) for i in range(len(CHUNK_BODIES))]

  def assert_no_partials(self, base_path):
    leftovers = [p for p in [base_path, get_manifest_path(base_path)] + self.chunk_paths(base_path)
                 if os.path.isfile(p)]
    assert leftovers == [], f"partial files left behind: {leftovers}"


class TestManagerDownload(ManagerDownloadTestBase):
  """Exercises the real _download_file / _download_chunked against a local server."""

  def run_with_server(self, fn):
    with http_server_context(handler=DownloadHandler) as (host, port):
      self.base_url = f'http://{host}:{port}'
      return fn()

  def test_download_file_writes_exact_bytes(self):
    def body():
      artifact = self.make_artifact(chunked=False)
      path = os.path.join(self.dest, artifact.fileName)
      asyncio.run(self.manager._download_file(artifact.downloadUri.uri, path, artifact))
      with open(path, 'rb') as f:
        written = f.read()
      assert written == WHOLE_BODY
      assert sha256(written) == artifact.downloadUri.sha256
      assert artifact.fileName not in self.manager._download_start_times
    self.run_with_server(body)

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

  def test_cached_bundle_cancel_skips_slot_write(self):
    """A cancel must stop an already-on-disk bundle before it is applied to the slot."""
    def body():
      artifact = self.make_artifact(chunked=True)
      base_path = os.path.join(self.dest, artifact.fileName)
      for i, data in enumerate(CHUNK_BODIES):
        with open(get_chunk_name(base_path, i, len(CHUNK_BODIES)), 'wb') as f:
          f.write(data)
      self._bundle.ref = "test-ref"
      params, store = self._make_params_with_store()
      store["ModelManager_DownloadRef"] = None  # removed -> cancelled
      self.manager.params = params
      self.manager._download_ref = b"ref"
      with self.assertRaises(Exception) as ctx:
        asyncio.run(self.manager._download_bundle(self._bundle, self.dest, "qcom"))
      assert 'cancelled' in str(ctx.exception).lower()
      assert "ModelManager_ActiveBundle" not in store
      assert all(os.path.isfile(p) for p in self.chunk_paths(base_path)), "cancel must not delete cached chunks"
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

  def test_download_writes_qcom_slot(self):
    """A download resolved to the qcom source writes the qcom active bundle slot only."""
    def body():
      artifact = self.make_artifact(chunked=True)
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
      chunk_names = [get_chunk_name(artifact.fileName, i, len(artifact.chunks)) for i in range(len(artifact.chunks))]
      missing = [c for c in chunk_names if not os.path.isfile(os.path.join(self.dest, c))]
      assert missing == [], f"chunks missing from the cache: {missing}"
    self.run_with_server(body)

  def test_download_writes_chestnut_slot(self):
    """A download resolved to the chestnut source writes the chestnut active bundle slot only."""
    def body():
      self.make_artifact(chunked=True)
      self._bundle.ref = "big-ref"
      self._bundle.minimumSelectorVersion = helpers.REQUIRED_JSON_VERSION
      params, store = self._make_params_with_store()
      self.manager.params = params
      asyncio.run(self.manager._download_bundle(self._bundle, self.dest, "chestnut"))

      assert "ModelManager_ActiveBundleChestnut" in store, "chestnut download must write the chestnut slot"
      assert "ModelManager_ActiveBundle" not in store, "chestnut download must not touch the qcom slot"
      assert self.manager.selected_bundle.status == custom.ModelManagerSP.DownloadStatus.downloaded
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
