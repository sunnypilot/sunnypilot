#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import requests
from openpilot.tools.lib.route import Route


def get_segments(source, route_id, camera, seg_range):
  if "@" in source or "comma-" in source or "sunny-" in source:  # SSH
    if not route_id:
      raise ValueError("route_id required for SSH")
    cmd = ["ssh", source, f"ls -d /data/media/0/realdata/{route_id.split('--')[0]}--*"]
    output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip()
    return [{
      "type": "ssh",
      "host": source,
      "src": os.path.join(path, camera),
      "num": int(path.split("--")[-1])
    } for path in sorted(output.split("\n"), key=lambda x: int(x.split("--")[-1])) if path]
  else:  # URL
    route = Route(route_id)
    cameras = [camera]
    if camera == "fcamera.hevc":
      cameras.extend([c for c in ["ecamera.hevc", "qcamera.ts"] if c != camera])

    for cam in cameras:
      attr_name = "camera_paths" if cam == "fcamera.hevc" else f"{cam.split('.')[0]}_paths"
      paths = getattr(route, attr_name)()
      if any(paths):
        return [{"type": "url", "src": url, "num": idx, "cam": cam} for idx, url in enumerate(paths) if url]

    raise ValueError(f"No footage found for {route_id}")


def download(job, out_dir):
  destination = os.path.join(out_dir, f"{job['num']}_{os.path.basename(job.get('cam', job.get('src')))}")
  if os.path.exists(destination) and os.path.getsize(destination) > 0:
    return destination

  print(f"Downloading segment {job['num']}")
  if job["type"] == "ssh":
    subprocess.check_call(["scp", f"{job['host']}:{job['src']}", destination])
  else:
    with requests.get(job["src"], stream=True) as r:
      r.raise_for_status()
      with open(destination, 'wb') as f:
        shutil.copyfileobj(r.raw, f)
  return destination


def mux(files, output_file, codec):
  list_filename = f"{output_file}.list.txt"
  with open(list_filename, 'w') as f:
    f.write('\n'.join([f"file '{os.path.abspath(name)}'" for name in files]))

  try:
    cmd = [
      "ffmpeg", "-y", "-probesize", "100M", "-analyzeduration", "100M", "-f", "concat",
      "-safe", "0", "-r", "20", "-i", list_filename, "-c", "copy", "-tag:v", codec, output_file
    ]
    subprocess.check_call(cmd)
    print(f"Saved: {output_file} ({os.path.getsize(output_file) / 1048576:.2f} MB)")
    if sys.platform == "darwin":
      subprocess.run(["open", "-R", output_file])
  finally:
    if os.path.exists(list_filename):
      os.remove(list_filename)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("source")
  parser.add_argument("route_id", nargs='?')
  parser.add_argument("--output", "-o", default="output.mp4")
  parser.add_argument("--camera", "-c", default="fcamera.hevc")
  parser.add_argument("--keep-segments", action="store_true")
  args = parser.parse_args()

  try:
    route_id_str = args.route_id or args.source
    segment_range = None
    if "/" in route_id_str:
      route_id_str, range_str = route_id_str.rsplit("/", 1)
      if ":" in range_str or range_str.isdigit():
        segment_range = range_str

    is_ssh = "@" in args.source or "comma-" in args.source or "sunny-" in args.source
    if not is_ssh and len(route_id_str.split("--")) > 2:
      route_id_str = "--".join(route_id_str.split("--")[:2])

    segments = get_segments(args.source, route_id_str, args.camera, segment_range)
    if segment_range:
      if ":" in segment_range:
        parts = segment_range.split(":")
        start_idx = int(parts[0]) if parts[0] else None
        end_idx = int(parts[1]) if parts[1] else None
      else:
        start_idx = int(segment_range)
        end_idx = start_idx + 1

      segments = [
        segment for segment in segments
        if (start_idx is None or segment['num'] >= start_idx) and (end_idx is None or segment['num'] < end_idx)
      ]

    download_dir = f"{route_id_str}_segments"
    os.makedirs(download_dir, exist_ok=True)

    downloaded_files = sorted(
      [download(segment, download_dir) for segment in segments],
      key=lambda x: int(os.path.basename(x).split("_")[0])
    )

    camera_name = segments[0].get('cam', args.camera)
    codec = "hvc1" if camera_name.endswith("hevc") else "avc1"
    mux(downloaded_files, f"{route_id_str}--{args.output}", codec)

    if not args.keep_segments:
      shutil.rmtree(download_dir)

  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)


if __name__ == "__main__":
  main()
