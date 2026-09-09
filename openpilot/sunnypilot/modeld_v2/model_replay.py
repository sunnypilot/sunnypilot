import argparse
import os
import sys
import time
import matplotlib.pyplot as plt
import numpy as np
from tinygrad.device import Device

from openpilot.common.file_chunker import open_file_chunked
from openpilot.selfdrive.modeld.compile_modeld import MODELD_INPUTS, make_input_queues
from openpilot.selfdrive.modeld.helpers import load_oob
from openpilot.selfdrive.test.process_replay.model_replay import SEGMENT, TEST_ROUTE
from openpilot.system.camerad.cameras.nv12_info import get_nv12_info
from openpilot.tools.lib.framereader import FrameReader
from openpilot.tools.lib.openpilotci import get_url
from openpilot.sunnypilot.modeld_v2.compile_modeld import derive_frame_skip, nv12_copy_size
from openpilot.sunnypilot.modeld_v2.parse_model_outputs import Parser


def get_replay_video_source(route_or_path=None, segment_index=SEGMENT, camera_type="fcamera.hevc"):
  if route_or_path and os.path.exists(route_or_path):
    return route_or_path
  selected_route = route_or_path or TEST_ROUTE
  return get_url(selected_route, segment_index, camera_type)


def initialize_replay_queues(model_dictionary, device="CPU"):
  metadata = model_dictionary.get("metadata", {})
  model_meta = metadata.get("model", metadata)
  input_shapes = model_meta.get("input_shapes", {})
  cam_resolutions = list(model_dictionary.get("run_model", {}).keys())
  cam_width, cam_height = cam_resolutions[0] if cam_resolutions else (1928, 1208)
  nv12_info = get_nv12_info(cam_width, cam_height)
  frame_copy_size = nv12_copy_size(nv12_info[0], nv12_info[1], nv12_info[2])
  frame_skip = model_meta.get("frame_skip") or derive_frame_skip({}, input_shapes)
  queues, npy_views, frame_views = make_input_queues(input_shapes, frame_skip, device, frame_copy_size)
  if "tfm" in npy_views:
    npy_views["tfm"][:] = np.eye(3, dtype=np.float32)
  if "big_tfm" in npy_views:
    npy_views["big_tfm"][:] = np.eye(3, dtype=np.float32)
  if "traffic_convention" in npy_views:
    npy_views["traffic_convention"][:] = np.array([1.0, 0.0], dtype=np.float32)
  return queues, npy_views, frame_views, model_meta


def replay_model_on_frames(model_path, frame_reader, number_of_frames=20):
  with open_file_chunked(model_path) as file_handle:
    model_data = load_oob(file_handle)
  run_model_dict = model_data.get("run_model", {})
  runner = next(iter(run_model_dict.values()), None)
  if runner is None:
    raise ValueError("Failed to resolve runner from model dictionary")

  queues, npy_views, frame_views, model_meta = initialize_replay_queues(model_data)
  output_slices = model_meta.get("output_slices", {})
  hidden_state_slice = output_slices.get("hidden_state")
  parser = Parser(ignore_missing=True)
  recorded_outputs = []
  max_frames = min(number_of_frames, getattr(frame_reader, "frame_count", number_of_frames))

  for frame_index in range(max_frames):
    frame_raw = frame_reader.get(frame_index)
    if frame_raw is not None:
      for view in frame_views.values():
        copy_length = min(view.size, frame_raw.size)
        view.flat[:copy_length] = frame_raw.flat[:copy_length]

    execution_arguments = {key: queues[key] for key in MODELD_INPUTS if key in queues}
    execution_start = time.perf_counter()
    step_output = runner(**execution_arguments)
    Device.default.synchronize()
    step_duration = time.perf_counter() - execution_start

    output_array = (step_output[0].numpy() if hasattr(step_output[0], "numpy") else np.array(step_output[0]))
    flat_output = output_array.flatten()

    if hidden_state_slice and "prev_feat" in npy_views:
      features_flat = flat_output[hidden_state_slice]
      target_slice = min(features_flat.size, npy_views["prev_feat"].size)
      npy_views["prev_feat"].flat[:target_slice] = features_flat[:target_slice]

    sliced_outputs = {slice_name: flat_output[np.newaxis, slice_range] for slice_name, slice_range in output_slices.items()}
    parser.parse_outputs(sliced_outputs)

    recorded_outputs.append({
      "frame_index": frame_index,
      "raw_output": output_array,
      "parsed_outputs": sliced_outputs,
      "execution_time": step_duration,
    })
  return recorded_outputs


def plot_comparison(series_a, series_b, title, output_directory, label_a="modeld_v2 model", label_b="stock"):
  os.makedirs(output_directory, exist_ok=True)
  figure, axis = plt.subplots()
  axis.plot(series_b, label=label_b)
  axis.plot(series_a, label=label_a, linestyle="--")
  axis.set_title(title)
  axis.legend(loc="best")
  plot_path = os.path.join(output_directory, f"{title}.png")
  figure.savefig(plot_path)
  plt.close(figure)
  return plot_path


def compare_models_on_route(new_model_path, old_model_path, route_or_path=None, segment_index=SEGMENT,
                            number_of_frames=20, tolerance=1e-4, label_a="modeld_v2 model", label_b="stock",
                            plot_directory=None, enforce_timings=False):
  video_url_or_path = get_replay_video_source(route_or_path, segment_index)
  frame_reader = FrameReader(video_url_or_path, pix_fmt="nv12")
  old_results = replay_model_on_frames(old_model_path, frame_reader, number_of_frames)
  new_results = replay_model_on_frames(new_model_path, frame_reader, number_of_frames)

  for step_index, (new_step, old_step) in enumerate(zip(new_results, old_results, strict=True)):
    new_array = new_step["raw_output"]
    old_array = old_step["raw_output"]
    if not np.allclose(new_array, old_array, atol=tolerance, rtol=tolerance):
      max_absolute_error = np.max(np.abs(new_array - old_array))
      sys.stderr.write(
        f"Replay mismatch at frame {step_index}: max absolute error {max_absolute_error:.6f} exceeds tolerance {tolerance}\n"
      )
      return False

  if len(new_results) > 1 and len(old_results) > 1:
    new_timings = [step["execution_time"] * 1000.0 for step in new_results[1:] if "execution_time" in step]
    old_timings = [step["execution_time"] * 1000.0 for step in old_results[1:] if "execution_time" in step]
    if new_timings and old_timings:
      print("------------------------------------------------")
      print("----------------- Model Timing -----------------")
      print("------------------------------------------------")
      print(f"{label_a}: avg {np.mean(new_timings):6.2f} ms | max {np.max(new_timings):6.2f} ms")
      print(f"{label_b}: avg {np.mean(old_timings):6.2f} ms | max {np.max(old_timings):6.2f} ms")

      if plot_directory:
        first_step_outputs = new_results[0].get("parsed_outputs", {})
        if "action" in first_step_outputs:
          series_a_curv = [step["parsed_outputs"]["action"].flatten()[0] for step in new_results]
          series_b_curv = [step["parsed_outputs"]["action"].flatten()[0] for step in old_results]
          plot_comparison(series_a_curv, series_b_curv, "desiredCurvature", plot_directory, label_a, label_b)

          series_a_accel = [step["parsed_outputs"]["action"].flatten()[1] for step in new_results]
          series_b_accel = [step["parsed_outputs"]["action"].flatten()[1] for step in old_results]
          plot_comparison(series_a_accel, series_b_accel, "desiredAcceleration", plot_directory, label_a, label_b)

        if "plan" in first_step_outputs:
          series_a_vel = [step["parsed_outputs"]["plan"].flatten()[0] for step in new_results]
          series_b_vel = [step["parsed_outputs"]["plan"].flatten()[0] for step in old_results]
          plot_comparison(series_a_vel, series_b_vel, "velocity.x", plot_directory, label_a, label_b)

        if "lead" in first_step_outputs:
          series_a_lead = [step["parsed_outputs"]["lead"].flatten()[0] for step in new_results]
          series_b_lead = [step["parsed_outputs"]["lead"].flatten()[0] for step in old_results]
          plot_comparison(series_a_lead, series_b_lead, "leadsV3.x", plot_directory, label_a, label_b)

        plot_comparison(new_timings, old_timings, "execution_timings", plot_directory, label_a, label_b)

        for slice_name in first_step_outputs:
          series_a = [np.mean(step["parsed_outputs"][slice_name]) for step in new_results if slice_name in step["parsed_outputs"]]
          series_b = [np.mean(step["parsed_outputs"][slice_name]) for step in old_results if slice_name in step["parsed_outputs"]]
          if series_a and series_b:
            plot_comparison(series_a, series_b, f"output_{slice_name}", plot_directory, label_a, label_b)
  print(f"Replay comparison result on route ({label_a} vs {label_b}): True")
  return True


if __name__ == "__main__":
  argument_parser = argparse.ArgumentParser(description="Model Replay on Real Driving Video")
  argument_parser.add_argument("--sunnypilot-model", dest="model_a", default=None)
  argument_parser.add_argument("--stock-model", dest="model_b", default=None)
  argument_parser.add_argument("--route", default=TEST_ROUTE)
  argument_parser.add_argument("--segment", type=int, default=SEGMENT)
  argument_parser.add_argument("--frames", type=int, default=20)
  argument_parser.add_argument("--plot-dir", default=None)
  parsed_arguments = argument_parser.parse_args()

  if not parsed_arguments.model_a:
    argument_parser.error("Must provide either --sunnypilot-model, --new-model, or --model-path-a")

  if parsed_arguments.model_b:
    matches = compare_models_on_route(parsed_arguments.model_a, parsed_arguments.model_b, route_or_path=parsed_arguments.route,
                                      segment_index=parsed_arguments.segment, number_of_frames=parsed_arguments.frames,
                                      tolerance=1e-4, label_a="modeld_v2 model",
                                      label_b="stock", plot_directory=parsed_arguments.plot_dir)
    if not matches:
      sys.exit(1)
  else:
    source_url = get_replay_video_source(parsed_arguments.route, parsed_arguments.segment)
    reader = FrameReader(source_url, pix_fmt="nv12")
    results = replay_model_on_frames(parsed_arguments.model_a, reader, parsed_arguments.frames)
