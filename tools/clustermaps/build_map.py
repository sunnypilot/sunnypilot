#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import http.server
import json
import re
import secrets
import shutil
import socketserver
import threading
from functools import partial
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from openpilot.tools.clustermaps.analyzer import (
  AnalyzerConfig,
  analyze_route,
  merge_segment_routes,
  rebuild_index,
  write_route_cache,
)
from openpilot.tools.lib.route import SegmentRange


TOOL_ROOT = Path(__file__).resolve().parent
DEFAULT_CACHE_DIR = TOOL_ROOT / "web" / "data"
CACHE_ID_PATTERN = re.compile(r"[0-9a-f]{16}")
DEVICE_SEGMENT_PATTERN = re.compile(r"(?P<route>.+)--(?P<segment>[0-9]+)")
IMPORT_JOBS: dict[str, dict] = {}
IMPORT_JOBS_LOCK = threading.Lock()
CACHE_WRITE_LOCK = threading.Lock()


def _public_job(job: dict) -> dict:
  return {key: value for key, value in job.items() if not key.startswith("_")}


def _persist_job(job: dict) -> None:
  manifest_path = Path(job["_manifestPath"])
  manifest_path.parent.mkdir(parents=True, exist_ok=True)
  temporary_path = manifest_path.with_suffix(".tmp")
  temporary_path.write_text(json.dumps(_public_job(job), separators=(",", ":")))
  temporary_path.replace(manifest_path)


def _update_job(job_id: str, **updates) -> None:
  with IMPORT_JOBS_LOCK:
    IMPORT_JOBS[job_id].update(updates)
    _persist_job(IMPORT_JOBS[job_id])


def _run_import_job(job_id: str, route_identifier: str, label: str | None, segments: list[int], cache_dir: Path) -> None:
  try:
    available = SegmentRange(route_identifier).seg_idxs
    cache_key = route_identifier if segments == available else f"{route_identifier}/segments={','.join(map(str, segments))}"
    route_cache_id = hashlib.sha256(cache_key.encode()).hexdigest()[:16]
    segment_dir = cache_dir / "route_analysis" / route_cache_id / "segments"
    segment_dir.mkdir(parents=True, exist_ok=True)
    analyzed_segments: list[dict] = []
    _update_job(job_id, status="running", stage="Locating full rlogs", percent=2)
    for position, segment_index in enumerate(segments, start=1):
      segment_path = segment_dir / f"{segment_index}.json"
      if segment_path.exists():
        try:
          segment_route = json.loads(segment_path.read_text())
        except (json.JSONDecodeError, OSError):
          segment_path.unlink(missing_ok=True)
          segment_route = None
      else:
        segment_route = None
      if segment_route is None:
        _update_job(
          job_id,
          stage=f"Analyzing segment {segment_index} ({position} of {len(segments)})",
          percent=round(80 * (position - 1) / len(segments)),
        )
        segment_route = analyze_route(route_identifier, segment_indexes=[segment_index])
        temporary_path = segment_path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(segment_route, separators=(",", ":")))
        temporary_path.replace(segment_path)
      analyzed_segments.append(segment_route)
      _update_job(
        job_id,
        stage=f"Checkpointed segment {position} of {len(segments)}",
        completedSegments=position,
        percent=round(80 * position / len(segments)),
      )

    _update_job(job_id, stage="Assembling route and map layers", percent=88)
    route = merge_segment_routes(
      route_identifier,
      analyzed_segments,
      label=label,
      cache_key=cache_key,
      segment_indexes=segments,
    )
    with CACHE_WRITE_LOCK:
      route_path, geojson_path = write_route_cache(route, cache_dir)
    _update_job(
      job_id,
      status="complete",
      stage="Ready",
      percent=100,
      cacheId=route["id"],
      routeFile=route_path.name,
      geojsonFile=geojson_path.name,
      summary=route["summary"],
    )
  except Exception as error:
    _update_job(job_id, status="error", stage="Import failed", error=str(error))


def _load_and_resume_jobs(cache_dir: Path) -> None:
  imports_dir = cache_dir / "imports"
  for manifest_path in imports_dir.glob("*/job.json"):
    try:
      job = json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError):
      continue
    job["_manifestPath"] = str(manifest_path)
    with IMPORT_JOBS_LOCK:
      IMPORT_JOBS[job["id"]] = job
    if job["status"] in ("queued", "running"):
      _update_job(job["id"], status="queued", stage="Resuming from segment checkpoints")
      threading.Thread(
        target=_run_import_job,
        args=(job["id"], job["route"], job.get("label"), job["segments"], cache_dir),
        daemon=True,
      ).start()


class RoadQualityRequestHandler(http.server.SimpleHTTPRequestHandler):
  cache_dir = DEFAULT_CACHE_DIR

  def end_headers(self) -> None:
    self.send_header("Cache-Control", "no-store")
    super().end_headers()

  def _json_response(self, payload: dict | list, status: int = 200) -> None:
    encoded = json.dumps(payload).encode()
    self.send_response(status)
    self.send_header("Content-Type", "application/json")
    self.send_header("Content-Length", str(len(encoded)))
    self.end_headers()
    self.wfile.write(encoded)

  def _error_response(self, message: str, status: int = 400) -> None:
    self._json_response({"error": message}, status)

  def _read_json(self) -> dict:
    if self.headers.get("X-Road-Quality-Request") != "1":
      raise ValueError("Missing local request header")
    length = int(self.headers.get("Content-Length", "0"))
    if length <= 0 or length > 65_536:
      raise ValueError("Invalid request size")
    payload = json.loads(self.rfile.read(length))
    if not isinstance(payload, dict):
      raise ValueError("Expected a JSON object")
    return payload

  def do_GET(self) -> None:
    parsed = urlparse(self.path)
    if parsed.path.startswith(("/data/device_rlogs/", "/data/device_analysis/", "/data/route_analysis/", "/data/imports/")):
      self._error_response("Private analysis data is not browser-accessible", 404)
      return
    if parsed.path == "/api/segments":
      try:
        route_identifier = parse_qs(parsed.query).get("route", [""])[0].strip()
        segment_range = SegmentRange(route_identifier)
        base_identifier = f"{segment_range.dongle_id}/{segment_range.log_id}"
        segments = SegmentRange(base_identifier).seg_idxs
        self._json_response({
          "route": base_identifier,
          "segmentCount": len(segments),
          "segments": [{"index": index, "label": f"Segment {index}"} for index in segments],
        })
      except Exception as error:
        self._error_response(str(error))
      return
    if parsed.path.startswith("/api/jobs/"):
      job_id = parsed.path.removeprefix("/api/jobs/")
      with IMPORT_JOBS_LOCK:
        job = IMPORT_JOBS.get(job_id)
        payload = _public_job(job) if job is not None else None
      if payload is None:
        self._error_response("Import job not found", 404)
      else:
        self._json_response(payload)
      return
    super().do_GET()

  def do_POST(self) -> None:
    try:
      payload = self._read_json()
      if self.path == "/api/import":
        route_identifier = str(payload.get("route", "")).strip()
        segment_range = SegmentRange(route_identifier)
        base_identifier = f"{segment_range.dongle_id}/{segment_range.log_id}"
        available = SegmentRange(base_identifier).seg_idxs
        raw_segments = payload.get("segments", available)
        if not isinstance(raw_segments, list) or any(not isinstance(index, int) for index in raw_segments):
          raise ValueError("segments must be a list of integer indexes")
        segments = sorted(set(raw_segments))
        if not segments or any(index not in available for index in segments):
          raise ValueError("Select at least one available segment")
        label_value = payload.get("label")
        label = str(label_value).strip()[:120] if label_value else None
        job_id = secrets.token_hex(8)
        manifest_path = self.cache_dir / "imports" / job_id / "job.json"
        with IMPORT_JOBS_LOCK:
          IMPORT_JOBS[job_id] = {
            "id": job_id,
            "route": base_identifier,
            "label": label,
            "segments": segments,
            "status": "queued",
            "stage": "Queued",
            "percent": 0,
            "completedSegments": 0,
            "totalSegments": len(segments),
            "_manifestPath": str(manifest_path),
          }
          _persist_job(IMPORT_JOBS[job_id])
        threading.Thread(
          target=_run_import_job,
          args=(job_id, base_identifier, label, segments, self.cache_dir),
          daemon=True,
        ).start()
        self._json_response({"jobId": job_id}, 202)
        return
      if self.path == "/api/remove":
        cache_id = str(payload.get("cacheId", ""))
        if CACHE_ID_PATTERN.fullmatch(cache_id) is None:
          raise ValueError("Invalid cache id")
        with CACHE_WRITE_LOCK:
          remove_routes([cache_id], self.cache_dir, AnalyzerConfig())
        self._json_response({"removed": cache_id})
        return
      self._error_response("API endpoint not found", 404)
    except (AssertionError, ValueError, json.JSONDecodeError) as error:
      self._error_response(str(error))


def import_routes(routes: list[str], cache_dir: Path, label: str | None) -> None:
  for identifier in routes:
    print(f"Analyzing {identifier} from full rlogs...")
    route = analyze_route(identifier, label=label if len(routes) == 1 else None)
    route_path, geojson_path = write_route_cache(route, cache_dir)
    counts = route["summary"]["eventCounts"]
    result = f"Cached {route_path.name}: {route['summary']['distanceM']:.0f} m, "
    result += f"{counts['impact']} impacts, {counts['roughRoad']} rough windows"
    print(result)
    print(f"GeoJSON: {geojson_path}")


def import_device_directory(device_dir: Path, cache_dir: Path, device_key: str) -> None:
  grouped: dict[str, list[tuple[int, Path]]] = {}
  for path in sorted(device_dir.glob("*/rlog.*")):
    match = DEVICE_SEGMENT_PATTERN.fullmatch(path.parent.name)
    if match is None:
      continue
    grouped.setdefault(match.group("route"), []).append((int(match.group("segment")), path))
  if not grouped:
    raise ValueError(f"No device rlogs found under {device_dir}")

  checkpoint_root = cache_dir / "device_analysis"
  for route_name, segment_files in grouped.items():
    identifier = f"{device_key}/{route_name}"
    checkpoint_dir = checkpoint_root / hashlib.sha256(identifier.encode()).hexdigest()[:16]
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    analyzed_segments: list[dict] = []
    analyzed_indexes: list[int] = []
    print(f"Analyzing device route {identifier} ({len(segment_files)} segments)...")
    for position, (segment_index, rlog_path) in enumerate(sorted(segment_files), start=1):
      checkpoint_path = checkpoint_dir / f"{segment_index}.json"
      try:
        if checkpoint_path.exists():
          segment_route = json.loads(checkpoint_path.read_text())
        else:
          segment_route = analyze_route(
            identifier,
            segment_indexes=[segment_index],
            log_files=[str(rlog_path)],
          )
          temporary_path = checkpoint_path.with_suffix(".tmp")
          temporary_path.write_text(json.dumps(segment_route, separators=(",", ":")))
          temporary_path.replace(checkpoint_path)
        analyzed_segments.append(segment_route)
        analyzed_indexes.append(segment_index)
        print(f"  [{position}/{len(segment_files)}] segment {segment_index} ready")
      except Exception as error:
        print(f"  [{position}/{len(segment_files)}] segment {segment_index} skipped: {error}")
    if not analyzed_segments:
      print("  No analyzable segments; route skipped.")
      continue
    route = merge_segment_routes(identifier, analyzed_segments, segment_indexes=analyzed_indexes)
    route_path, _ = write_route_cache(route, cache_dir)
    print(f"Cached {route_path.name}: {route['summary']['distanceM'] / 1000:.2f} km")


def remove_routes(cache_ids: list[str], cache_dir: Path, config: AnalyzerConfig) -> None:
  for cache_id in cache_ids:
    if CACHE_ID_PATTERN.fullmatch(cache_id) is None:
      raise ValueError(f"Invalid cache id {cache_id!r}; use the 16-character id printed by --list")
    removed = False
    for path in (cache_dir / "routes" / f"{cache_id}.json", cache_dir / "geojson" / f"{cache_id}.geojson"):
      if path.exists():
        path.unlink()
        removed = True
    shutil.rmtree(cache_dir / "device_analysis" / cache_id, ignore_errors=True)
    shutil.rmtree(cache_dir / "route_analysis" / cache_id, ignore_errors=True)
    for manifest_path in (cache_dir / "imports").glob("*/job.json"):
      try:
        manifest = json.loads(manifest_path.read_text())
      except (json.JSONDecodeError, OSError):
        continue
      if manifest.get("cacheId") == cache_id:
        shutil.rmtree(manifest_path.parent, ignore_errors=True)
    print(f"{'Removed' if removed else 'Not found'}: {cache_id}")
  rebuild_index(cache_dir, config)


def list_routes(cache_dir: Path, config: AnalyzerConfig) -> None:
  index = rebuild_index(cache_dir, config)
  if not index["routes"]:
    print("No routes are cached.")
    return
  print(f"{index['routeCount']} cached route(s), {index['driverCount']} driver(s):")
  for route in index["routes"]:
    summary = route["summary"]
    segments = route["metadata"].get("segmentCount")
    segment_text = f"{segments} segment(s), " if segments is not None else ""
    route_description = (
      f"  {route['id']}  {route['label']}  {segment_text}"
      + f"{summary['durationS'] / 60:.1f} min, {summary['distanceM'] / 1000:.2f} km"
    )
    print(route_description)


def serve(port: int) -> None:
  RoadQualityRequestHandler.cache_dir = DEFAULT_CACHE_DIR
  _load_and_resume_jobs(DEFAULT_CACHE_DIR)
  handler = partial(RoadQualityRequestHandler, directory=str(TOOL_ROOT / "web"))
  with socketserver.ThreadingTCPServer(("127.0.0.1", port), handler) as server:
    print(f"clustermaps: http://127.0.0.1:{port}")
    print("Press Ctrl-C to stop.")
    try:
      server.serve_forever()
    except KeyboardInterrupt:
      pass


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Analyze full rlogs into a multi-route road-quality map cache.",
  )
  parser.add_argument("routes", nargs="*", help="Route or segment identifiers. Full rlogs are required.")
  parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR, help="Generated JSON/GeoJSON cache directory.")
  parser.add_argument("--label", help="Friendly label to use when importing one route.")
  parser.add_argument("--import-device-dir", type=Path, help="Import a previously copied on-device realdata directory.")
  parser.add_argument("--device-key", help="Stable local device/driver key used with --import-device-dir.")
  parser.add_argument("--list", action="store_true", help="List cached routes and their removable cache ids.")
  parser.add_argument("--remove", action="append", default=[], metavar="CACHE_ID", help="Remove one cached route; repeat as needed.")
  parser.add_argument("--serve", action="store_true", help="Serve the local HTML5 map after importing.")
  parser.add_argument("--port", type=int, default=8765, help="Local HTTP port used with --serve.")
  args = parser.parse_args()

  config = AnalyzerConfig()
  if args.import_device_dir:
    device_key = args.device_key or f"device-{args.import_device_dir.name}"
    try:
      import_device_directory(args.import_device_dir, args.cache_dir, device_key)
    except ValueError as error:
      parser.error(str(error))
  if args.remove:
    try:
      remove_routes(args.remove, args.cache_dir, config)
    except ValueError as error:
      parser.error(str(error))
  if args.routes:
    import_routes(args.routes, args.cache_dir, args.label)
  elif not args.remove and not args.import_device_dir:
    rebuild_index(args.cache_dir, config)
  if args.list:
    list_routes(args.cache_dir, config)
  if args.serve:
    if args.cache_dir.resolve() != DEFAULT_CACHE_DIR.resolve():
      parser.error("--serve currently requires the default cache directory")
    serve(args.port)


if __name__ == "__main__":
  main()
