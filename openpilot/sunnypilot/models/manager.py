"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import asyncio
import os
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from openpilot.common.params import Params
from openpilot.common.realtime import Ratekeeper
from openpilot.common.swaglog import cloudlog
from openpilot.common.hardware.hw import Paths

from openpilot.cereal import messaging, custom
from openpilot.sunnypilot.models.fetcher import ModelFetcher
from openpilot.sunnypilot.models.helpers import (ACTIVE_BUNDLE_KEYS, get_active_bundle, get_selected_bundle,
                                                  resolve_bundle_by_ref, validate_active_bundles, verify_file)

# (connect, read) seconds. read is per-request inactivity, not a total cap
DOWNLOAD_TIMEOUT = (30, 30)
# Models live on HuggingFace, whose Xet content-addressed storage throttles each TCP connection to ~1-2 MB/s (erratically)
# but never rate-limited 32 parallel connections. Measured on a comma 3X: 1 connection ~2 MB/s,
# 8 ~12.7 MB/s, 12 ~13.5 MB/s, which is the device link ceiling. 12 saturates it with headroom.
MAX_CONCURRENT_CHUNKS = 12
# Byte-range piece size. Small enough that even a ~50 MB small model splits into enough pieces to
# keep all connections busy, and a throttled connection only ever holds back one small piece.
PIECE_SIZE = 8 * 1024 * 1024
PIECE_RETRIES = 3  # attempts per piece before the download fails
PIECE_BACKOFF = 1.0  # seconds before a piece's second attempt, growing linearly
# HTTP statuses a server sends while overloaded or throttling; any other 4xx/5xx is permanent
TRANSIENT_HTTP_STATUS = frozenset({408, 429, 500, 502, 503, 504})
REPORT_INTERVAL = 0.5  # seconds between progress publications


class DownloadCancelled(Exception):
  pass


def _is_transient(e: BaseException) -> bool:
  """Worth retrying: a transport failure, or an HTTP status the server sends while overloaded."""
  if isinstance(e, requests.HTTPError):
    return e.response is not None and e.response.status_code in TRANSIENT_HTTP_STATUS
  return isinstance(e, (requests.ConnectionError, requests.Timeout, requests.exceptions.ChunkedEncodingError))


class _Progress:
  """Bytes landed on disk, shared between worker threads and the reporter on the event loop."""

  def __init__(self):
    self._bytes = 0
    self._lock = threading.Lock()

  def add_bytes(self, n: int) -> None:
    with self._lock:
      self._bytes += n

  def snapshot(self) -> int:
    with self._lock:
      return self._bytes


def _piece_ranges(total: int, piece_size: int) -> list[tuple[int, int]]:
  """[start, end) byte ranges tiling a file of `total` bytes."""
  return [(start, min(start + piece_size, total)) for start in range(0, total, piece_size)]


def _prepare_target(path: str, total: int) -> None:
  """Starts fresh with a sparse file of the full size; every piece lands at its own offset."""
  with open(path, "wb") as f:
    f.truncate(total)


def _content_range_total(response: requests.Response) -> int | None:
  if response.status_code != 206:
    return None
  match = re.fullmatch(r"bytes \d+-\d+/(\d+)", response.headers.get("Content-Range", ""))
  return int(match.group(1)) if match else None


def _probe_size(url: str) -> tuple[int, bool]:
  """(total bytes, server honors byte ranges). A one-byte Range probe doubles as the size lookup:
  a 206 carries the total in Content-Range, a 200 means the server only serves whole bodies."""
  with requests.get(url, headers={"Range": "bytes=0-0"}, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
    response.raise_for_status()
    total = _content_range_total(response)
    if total is not None:
      return total, True
    return int(response.headers.get("Content-Length", 0)), False


def _fetch_piece(url: str, path: str, index: int, start: int, end: int | None, progress: _Progress,
                 cancel: threading.Event, block_size: int) -> None:
  """Worker thread: streams one byte range straight into `path` at its offset. `end is None` streams
  the whole body (server without range support). Transient errors retry the piece from scratch; a
  permanent HTTP status, a cancel and a server that stops honoring ranges do not."""
  headers = {"Range": f"bytes={start}-{end - 1}"} if end is not None else {}
  label = f"{os.path.basename(path)} piece {index}"
  for attempt in range(PIECE_RETRIES):
    written = 0
    try:
      with requests.get(url, headers=headers, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
        response.raise_for_status()
        if end is not None and response.status_code != 206:
          raise ValueError(f"server ignored byte range for {label}")
        with open(path, "r+b") as f:
          f.seek(start)
          for block in response.iter_content(chunk_size=block_size):
            if cancel.is_set():
              raise DownloadCancelled("Download cancelled")
            f.write(block)
            written += len(block)
            progress.add_bytes(len(block))
          if end is None:
            f.truncate()  # unknown length: the body defines the file size
          if end is not None and written != end - start:
            raise requests.exceptions.ConnectionError(f"short read: {written} of {end - start} bytes")
      return
    except requests.RequestException as e:
      progress.add_bytes(-written)  # the piece restarts from scratch
      if not _is_transient(e) or attempt == PIECE_RETRIES - 1:
        raise
      cloudlog.warning(f"retrying {label} after {type(e).__name__}: {e}")
      if cancel.wait(PIECE_BACKOFF * (1 + attempt)):
        raise DownloadCancelled("Download cancelled") from None


class ModelManagerSP:
  """Manages model downloads and status reporting"""

  def __init__(self):
    self.params = Params()
    self.model_fetcher = ModelFetcher(self.params)
    self.pm = messaging.PubMaster(["modelManagerSP"])
    self.sm = messaging.SubMaster(["deviceState"])
    self.chestnut_present = False
    self.available_models: list[custom.ModelManagerSP.ModelBundle] = []
    self.source_models: dict[str, list[custom.ModelManagerSP.ModelBundle]] = {}
    self.selected_bundle: custom.ModelManagerSP.ModelBundle = None
    self.active_bundle: custom.ModelManagerSP.ModelBundle = get_active_bundle(self.params, chestnut=self.chestnut_present)
    self._block_size = 128 * 1000  # 128 KB network read blocks
    self._download_start_times: dict[str, float] = {}  # Track start time per model
    self._download_ref: bytes | str | None = None

  def _download_interrupted(self) -> bool:
    # only removal cancels: a different ref is a queued selection that
    # _release_download_ref leaves in place for the next tick
    return self.params.get("ModelManager_DownloadRef") is None

  def _release_download_ref(self) -> None:
    if self.params.get("ModelManager_DownloadRef") == self._download_ref:
      self.params.remove("ModelManager_DownloadRef")
    self._download_ref = None

  def _sync_artifact_progress(self, source_artifact) -> None:
    """Mirror download progress to all artifacts sharing the same filename in the selected bundle."""
    if not self.selected_bundle:
      return
    for model in self.selected_bundle.models:
      artifact = model.artifact
      if artifact is not source_artifact and artifact.fileName == source_artifact.fileName:
        artifact.downloadProgress.status = source_artifact.downloadProgress.status
        artifact.downloadProgress.progress = source_artifact.downloadProgress.progress
        artifact.downloadProgress.eta = source_artifact.downloadProgress.eta

  def _calculate_eta(self, filename: str, progress: float) -> int:
    """Calculate ETA based on elapsed time and current progress"""
    if filename not in self._download_start_times or progress <= 0:
      return 60  # Default ETA for new downloads

    elapsed_time = time.monotonic() - self._download_start_times[filename]
    if elapsed_time <= 0:
      return 60

    # If we're at X% after Y seconds, we can estimate total time as (Y / X) * 100
    total_estimated_time = (elapsed_time / progress) * 100
    eta = total_estimated_time - elapsed_time

    return max(1, int(eta))  # Return at least 1 second if download is ongoing

  def _set_progress(self, artifact, status, progress: float, eta: int = 0) -> None:
    artifact.downloadProgress.status = status
    artifact.downloadProgress.progress = progress
    artifact.downloadProgress.eta = eta
    self._sync_artifact_progress(artifact)
    self._report_status()

  def _publish_progress(self, artifact, done_bytes: int, total: int) -> None:
    # 99 until the assembled file passes its hash check
    progress = min(99.0, done_bytes / total * 100) if total > 0 else 0.0
    eta = self._calculate_eta(artifact.fileName, progress)
    self._set_progress(artifact, custom.ModelManagerSP.DownloadStatus.downloading, progress, eta)

  async def _report_until_done(self, tasks: list[asyncio.Future], artifact, progress: _Progress, total: int) -> None:
    """Publishes progress every REPORT_INTERVAL until every piece has landed, surfacing the first
    worker failure and a cancel. Runs on the event loop: workers never touch messaging."""
    pending = set(tasks)
    while pending:
      done, pending = await asyncio.wait(pending, timeout=REPORT_INTERVAL)
      for task in done:
        task.result()  # re-raises a worker failure
      if self._download_interrupted():
        raise DownloadCancelled("Download cancelled")
      self._publish_progress(artifact, progress.snapshot(), total)

  async def _download_file(self, url: str, path: str, artifact) -> None:
    """Downloads `url` to `path` as parallel byte-range pieces written in place at their offsets, so
    the model is never copied and only ever occupies its own size on disk."""
    self._download_start_times[artifact.fileName] = time.monotonic()
    loop = asyncio.get_running_loop()

    total, ranged = await loop.run_in_executor(None, _probe_size, url)
    pieces: list[tuple[int, int | None]] = list(_piece_ranges(total, PIECE_SIZE)) if ranged else [(0, None)]
    await loop.run_in_executor(None, _prepare_target, path, total)
    progress = _Progress()
    cancel = threading.Event()

    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT_CHUNKS) as pool:
      # every worker owns its request: a shared requests.Session is not thread-safe
      tasks = [loop.run_in_executor(pool, _fetch_piece, url, path, i, start, end, progress, cancel, self._block_size)
               for i, (start, end) in enumerate(pieces)]
      try:
        await self._report_until_done(tasks, artifact, progress, total)
      except BaseException:
        cancel.set()
        for task in tasks:
          task.cancel()  # drops queued pieces; running ones see the event at their next block
        await asyncio.gather(*tasks, return_exceptions=True)
        raise

    del self._download_start_times[artifact.fileName]

  async def _download_chunked(self, base_url: str, base_path: str, artifact, skip: frozenset[int] | set[int] = frozenset()) -> None:
    from openpilot.common.file_chunker import get_chunk_name, get_manifest_path

    num_chunks = len(artifact.chunks)
    if num_chunks == 0:
      raise ValueError("No chunks defined in artifact")

    manifest_path = get_manifest_path(base_path)
    self._download_start_times[artifact.fileName] = time.monotonic()

    # Shared connection saves a TCP+TLS handshake per chunk.
    # Keep sequential: the link saturates on one stream and Session is not thread-safe.
    completed = len(skip)
    with requests.Session() as session:
      for i, _ in enumerate(artifact.chunks):
        if i in skip:
          continue
        chunk_url = get_chunk_name(base_url, i, num_chunks)
        chunk_path = get_chunk_name(base_path, i, num_chunks)
        chunk_downloaded = 0
        with session.get(chunk_url, stream=True, timeout=DOWNLOAD_TIMEOUT) as response:
          response.raise_for_status()
          chunk_size = int(response.headers.get("content-length", 0))
          with open(chunk_path, 'wb') as f:  # noqa: ASYNC230
            for data in response.iter_content(chunk_size=self._block_size):
              f.write(data)
              chunk_downloaded += len(data)
              if self._download_interrupted():
                raise DownloadCancelled("Download cancelled")
              intra = chunk_downloaded / max(chunk_size, 1)
              progress = min(99.0, ((completed + intra) / num_chunks) * 100)
              artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
              artifact.downloadProgress.progress = progress
              artifact.downloadProgress.eta = self._calculate_eta(artifact.fileName, progress)
              self._sync_artifact_progress(artifact)
              self._report_status()
        completed += 1

    with open(manifest_path, 'w') as f:  # noqa: ASYNC230
      f.write(str(num_chunks))
    if os.path.isfile(base_path):  # noqa: ASYNC240
      os.remove(base_path)
    del self._download_start_times[artifact.fileName]

  async def _process_artifact(self, artifact, destination_path: str) -> None:
    if not artifact.downloadUri.uri:
      return None
    if self._download_interrupted():
      raise DownloadCancelled("Download cancelled")

    url = artifact.downloadUri.uri
    expected_hash = artifact.downloadUri.sha256
    filename = artifact.fileName
    full_path = os.path.join(destination_path, filename)
    status = custom.ModelManagerSP.DownloadStatus

    try:
      # progress counts only valid chunks so a resumed download continues the
      # bar from where verification left it, instead of falling back to zero
      is_cached = False
      valid_chunks: set[int] = set()
      if len(artifact.chunks) > 0:
        from openpilot.common.file_chunker import get_chunk_name
        num_chunks = len(artifact.chunks)
        for i, chunk in enumerate(artifact.chunks):
          if self._download_interrupted():
            raise DownloadCancelled("Download cancelled")
          if await verify_file(get_chunk_name(full_path, i, num_chunks), chunk.sha256):
            valid_chunks.add(i)
          artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.verifying
          artifact.downloadProgress.progress = (len(valid_chunks) / num_chunks) * 100
          self._sync_artifact_progress(artifact)
          self._report_status()
        is_cached = len(valid_chunks) == num_chunks
      else:
        self._set_progress(artifact, status.verifying, 0)
        if await verify_file(full_path, expected_hash):
          is_cached = True

      if is_cached:
        self._set_progress(artifact, status.cached, 100)
        return

      if len(artifact.chunks) > 0:
        await self._download_chunked(url, full_path, artifact, skip=valid_chunks)
        from openpilot.common.file_chunker import get_chunk_name
        for i, chunk in enumerate(artifact.chunks):
          chunk_path = get_chunk_name(full_path, i, len(artifact.chunks))
          if not await verify_file(chunk_path, chunk.sha256):
            raise ValueError(f"Hash validation failed for chunk {i+1} of {filename}")
      else:
        await self._download_file(url, full_path, artifact)
        self._set_progress(artifact, status.verifying, 99)
        if not await verify_file(full_path, expected_hash):
          raise ValueError(f"Hash validation failed for {filename}")

      self._set_progress(artifact, status.downloaded, 100)

    except DownloadCancelled:
      # a cancel keeps whatever is on disk: complete chunks resume the next attempt
      self._download_start_times.pop(artifact.fileName, None)
      artifact.downloadProgress.status = status.failed
      artifact.downloadProgress.eta = 0
      self._sync_artifact_progress(artifact)
      if self.selected_bundle:
        self.selected_bundle.status = status.failed
      self._report_status()
      raise

    except Exception as e:
      cloudlog.error(f"Error downloading {filename}: {str(e)}")
      for f in [full_path] + [p for p in (os.path.join(destination_path, f) for f in os.listdir(destination_path)) if filename in p]:
        if os.path.isfile(f):  # noqa: ASYNC240
          os.remove(f)
      artifact.downloadProgress.status = status.failed
      artifact.downloadProgress.eta = 0
      self._sync_artifact_progress(artifact)
      if self.selected_bundle:
        self.selected_bundle.status = status.failed
      self._report_status()
      self._download_start_times.pop(artifact.fileName, None)
      raise

  async def _process_model(self, model, destination_path: str) -> None:
    """Processes a single model download including verification"""
    await self._process_artifact(model.artifact, destination_path)

  def _report_status(self) -> None:
    """Reports current status through messaging system"""
    msg = messaging.new_message('modelManagerSP', valid=True)
    model_manager_state = msg.modelManagerSP
    if self.selected_bundle:
      model_manager_state.selectedBundle = self.selected_bundle

    if self.active_bundle:
      model_manager_state.activeBundle = self.active_bundle

    model_manager_state.availableBundles = self.available_models
    self.pm.send('modelManagerSP', msg)

  async def _download_bundle(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str, source: str) -> None:
    self.selected_bundle = model_bundle
    self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloading
    for model in self.selected_bundle.models:
      model.artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.downloading
    self._report_status()
    os.makedirs(destination_path, exist_ok=True)

    try:
      seen_artifacts: set[str] = set()
      for model in self.selected_bundle.models:
        artifact = model.artifact
        if not artifact.fileName:
          continue
        if artifact.fileName in seen_artifacts:
          artifact.downloadProgress.status = custom.ModelManagerSP.DownloadStatus.cached
          artifact.downloadProgress.progress = 100
          artifact.downloadProgress.eta = 0
        else:
          seen_artifacts.add(artifact.fileName)
          await self._process_artifact(artifact, destination_path)

      if self._download_interrupted():
        raise DownloadCancelled("Download cancelled")
      self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.downloaded
      self.params.put(ACTIVE_BUNDLE_KEYS[source], model_bundle.to_dict(), block=True)
      self.active_bundle = get_active_bundle(self.params, chestnut=self.chestnut_present)

    except Exception:
      if self.selected_bundle is not None:
        self.selected_bundle.status = custom.ModelManagerSP.DownloadStatus.failed
      raise

    finally:
      self._report_status()

  def download(self, model_bundle: custom.ModelManagerSP.ModelBundle, destination_path: str, source: str) -> None:
    """Main entry point for downloading a model bundle"""
    asyncio.run(self._download_bundle(model_bundle, destination_path, source))

  def _process_download_requests(self) -> None:
    # loops so a ref queued during a download starts in the same tick, without
    # the bar dropping to idle for a tick between the two transfers
    last_ref = None
    while (ref_to_download := self.params.get("ModelManager_DownloadRef")) is not None:
      if ref_to_download == last_ref:  # a repeating ref falls back to the next tick instead of spinning
        return
      last_ref = ref_to_download
      resolved = resolve_bundle_by_ref(ref_to_download, self.source_models)
      if not resolved:
        return
      model_to_download, source = resolved
      self._download_ref = ref_to_download
      try:
        self.download(model_to_download, Paths.model_root(), source)
      except Exception as e:
        cloudlog.exception(e)
      finally:
        self._release_download_ref()
        self.selected_bundle = None

  def main_thread(self) -> None:
    """Main thread for model management"""
    rk = Ratekeeper(1, print_delay_threshold=None)

    while True:
      try:
        self.sm.update(0)
        self.chestnut_present = self.sm['deviceState'].chestnutPresent
        self.source_models = {source: self.model_fetcher.get_bundles_for_source(source) for source in ModelFetcher.MODEL_SOURCES}
        self.available_models = self.source_models[ModelFetcher.active_source(self.chestnut_present)]
        validate_active_bundles(self.params, self.source_models)
        self.active_bundle = get_active_bundle(self.params, chestnut=self.chestnut_present)

        if get_selected_bundle(self.params, "chestnut") is not None and get_selected_bundle(self.params, "qcom") is None:
          if self.params.get("ModelManager_DownloadRef") is None:
            from openpilot.sunnypilot.models.model_name import DEFAULT_MODEL_REF
            if DEFAULT_MODEL_REF:
              self.params.put("ModelManager_DownloadRef", DEFAULT_MODEL_REF)

        self._process_download_requests()

        if self.params.get("ModelManager_ClearCache"):
          self.clear_model_cache()
          self.params.remove("ModelManager_ClearCache")

        self._report_status()
        rk.keep_time()

      except Exception as e:
        cloudlog.exception(f"Error in main thread: {str(e)}")
        rk.keep_time()

  def clear_model_cache(self) -> None:
    """
    Clears the model cache directory of all files except those in the active model bundle.
    """

    # Get list of files used by both slots' selected bundles (either may become
    # the truly active bundle depending on hardware availability)
    active_files = []
    for source in ACTIVE_BUNDLE_KEYS:
      if selected_bundle := get_selected_bundle(self.params, source):
        for model in selected_bundle.models:
          if model.artifact.fileName:
            active_files.append(model.artifact.fileName)

    # Remove all files except active ones (including their chunk files)
    model_dir = Paths.model_root()
    try:
      for filename in os.listdir(model_dir):
        base = filename.split('.chunk')[0] if '.chunk' in filename else filename
        if base not in active_files and filename not in active_files:
          file_path = os.path.join(model_dir, filename)
          if os.path.isfile(file_path):
            os.remove(file_path)
      cloudlog.info("Model cache cleared, keeping active model files")
    except Exception as e:
      cloudlog.exception(f"Error clearing model cache: {str(e)}")

def main():
  ModelManagerSP().main_thread()


if __name__ == "__main__":
  main()
