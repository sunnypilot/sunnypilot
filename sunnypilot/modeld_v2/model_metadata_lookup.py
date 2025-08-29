"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import argparse
import os
import pickle
import sys
from typing import Any


def parse_metadata_file(metadata_path: str, type_key: str = None) -> dict:
  if not os.path.exists(metadata_path):
    print(f"Error: File not found: {metadata_path}")
    sys.exit(1)
  with open(metadata_path, 'rb') as f:
    metadata = pickle.load(f)
  result = {
    "metadata_path": metadata_path,
    "model_checkpoint": metadata.get("model_checkpoint"),
    **{k: metadata[k] for k in ("input_shapes", "output_shapes", "output_slices") if k in metadata}
  }
  if type_key:
    result[type_key] = True
  return result

def add_to_model_metadata(new_data: dict, key: str) -> None:
  file_path = os.path.abspath(__file__)
  with open(file_path) as f:
    lines = f.readlines()
  # Find insertion point for new entry
  for i in range(len(lines)-1, -1, -1):
    if lines[i].strip() == '}' and any('MODEL_METADATA' in l for l in lines[:i]):
      insert_idx = i
      break
  else:
    print("Could not find where to insert new entry in MODEL_METADATA.")
    sys.exit(1)

  def format_val(val: Any, indent: int = 2) -> str:
    if isinstance(val, dict):
      items = [f'"{k}": {format_val(v, indent+2)}' for k, v in val.items()]
      return '{\n' + ',\n'.join(' '*(indent+2) + item for item in items) + '\n' + ' '*indent + '}'
    if isinstance(val, str):
      return f'"{val}"'
    if isinstance(val, slice):
      if val.step is None:
        return f'slice({val.start}, {val.stop})'
      return f'slice({val.start}, {val.stop}, {val.step})'
    if isinstance(val, (tuple, list)):
      open_s, close_s = ('(', ')') if isinstance(val, tuple) else ('[', ']')
      return open_s + ', '.join(format_val(x, 0) for x in val) + close_s
    return repr(val)

  entry_str = f'  "{key}": {format_val(new_data, 2)},\n'
  lines.insert(insert_idx, entry_str)

  with open(file_path, 'w') as f:
    f.writelines(lines)
  print(f"Added entry to MODEL_METADATA with key: {key}")


MODEL_METADATA = {
  "supercombo_wd40": {
    "metadata_path": "/Users/james/Downloads/model-WD40 (April 09, 2024)-558/supercombo_wd40_metadata.pkl",
    "model_checkpoint": None,
    "non20hz": True,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 100, 8),
      "traffic_convention": (1, 2),
      "lateral_control_params": (1, 2),
      "prev_desired_curv": (1, 100, 1),
      "features_buffer": (1, 99, 512),
    },
    "output_shapes": {"outputs": (1, 6504)},
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5916),
      "desire_pred": slice(5916, 5948),
      "pose": slice(5948, 5960),
      "wide_from_device_euler": slice(5960, 5966),
      "sim_pose": slice(5966, 5978),
      "road_transform": slice(5978, 5990),
      "desired_curvature": slice(5990, 5992),
      "hidden_state": slice(5992, None),
    },
  },
  "supercombo_farmville": {
    "metadata_path": "/Users/james/Downloads/model-Farmville (November 07, 2023)-557/supercombo_farmville_metadata.pkl",
    "model_checkpoint": None,
    "non20hz": True,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 100, 8),
      "traffic_convention": (1, 2),
      "lat_planner_state": (1, 4),
      "nav_features": (1, 256),
      "nav_instructions": (1, 150),
      "features_buffer": (1, 99, 512),
    },
    "output_shapes": {"outputs": (1, 6768)},
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5916),
      "desire_pred": slice(5916, 5948),
      "pose": slice(5948, 5960),
      "wide_from_device_euler": slice(5960, 5966),
      "sim_pose": slice(5966, 5978),
      "road_transform": slice(5978, 5990),
      "lat_planner_solution": slice(5990, 6254),
      "hidden_state": slice(6254, -2),
      "pad": slice(-2, None),
    },
  },
  "driving_policy_steam_powered": {
    "metadata_path": "selfdrive/modeld/models/driving_policy_metadata.pkl",
    "model_checkpoint": "a8f96b93-bde2-4e28-a732-4df21ebba968/400",
    "split": True,
    "input_shapes": {
      "desire": (1, 25, 8),
      "traffic_convention": (1, 2),
      "features_buffer": (1, 25, 512),
    },
    "output_shapes": {"outputs": (1, 1000)},
    "output_slices": {
      "plan": slice(0, 990),
      "desire_state": slice(990, 998),
      "pad": slice(-2, None),
    },
  },
  "supercombo_op": {
    "metadata_path": "/Users/james/Downloads/model-Optimus Prime (September 21, 2023)-559/supercombo_op_metadata.pkl",
    "model_checkpoint": None,
    "non20hz": True,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 100, 8),
      "traffic_convention": (1, 2),
      "nav_features": (1, 256),
      "nav_instructions": (1, 150),
      "features_buffer": (1, 99, 512),
    },
    "output_shapes": {"outputs": (1, 6504)},
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5916),
      "desire_pred": slice(5916, 5948),
      "pose": slice(5948, 5960),
      "wide_from_device_euler": slice(5960, 5966),
      "sim_pose": slice(5966, 5978),
      "road_transform": slice(5978, 5990),
      "hidden_state": slice(5990, -2),
      "pad": slice(-2, None),
    },
  },
  "supercombo_nd": {
    "metadata_path": "/Users/james/Downloads/model-Notre Dame (July 01, 2024)-568/supercombo_nd_metadata.pkl",
    "model_checkpoint": None,
    "non20hz": True,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 100, 8),
      "traffic_convention": (1, 2),
      "lateral_control_params": (1, 2),
      "prev_desired_curv": (1, 100, 1),
      "features_buffer": (1, 99, 512),
    },
    "output_shapes": {"outputs": (1, 6512)},
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5921),
      "desire_pred": slice(5921, 5953),
      "pose": slice(5953, 5965),
      "wide_from_device_euler": slice(5965, 5971),
      "sim_pose": slice(5971, 5983),
      "road_transform": slice(5983, 5995),
      "desired_curvature": slice(5995, 5997),
      "hidden_state": slice(5997, -3),
      "pad": slice(-3, None),
    },
  },
  "supercombo_npr": {
    "metadata_path": "/Users/james/Downloads/supercombo_npr_metadata.pkl",
    "model_checkpoint": None,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 25, 8),
      "traffic_convention": (1, 2),
      "features_buffer": (1, 24, 512)
    },
    "output_shapes": {
      "outputs": (1, 6500)
    },
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5923),
      "desire_pred": slice(5923, 5955),
      "pose": slice(5955, 5967),
      "wide_from_device_euler": slice(5967, 5973),
      "road_transform": slice(5973, 5985),
      "hidden_state": slice(5985, -3),
      "pad": slice(-3, None)
    },
    "20hz": True
  },
  "driving_policy_renamed_desire": {
    "metadata_path": "/Users/james/Downloads/model-ugh (August 27, 2025)-575/driving_policy_ugh_metadata.pkl",
    "model_checkpoint": "a8f96b93-bde2-4e28-a732-4df21ebba968/400",
    "split": True,
    "input_shapes": {
      "desire_pulse": (1, 25, 8),
      "traffic_convention": (1, 2),
      "features_buffer": (1, 25, 512)
    },
    "output_shapes": {
      "outputs": (1, 1000)
    },
    "output_slices": {
      "plan": slice(0, 990),
      "desire_state": slice(990, 998),
      "pad": slice(-2, None)
    }
  },
  "supercombo_nts": {   # released in January of this year, so its not 20hz, but it is modern logic..
    "metadata_path": "/Users/james/Downloads/supercombo_nts_metadata.pkl",
    "model_checkpoint": None,
    "non20hz": True,
    "input_shapes": {
      "input_imgs": (1, 12, 128, 256),
      "big_input_imgs": (1, 12, 128, 256),
      "desire": (1, 100, 8),
      "traffic_convention": (1, 2),
      "lateral_control_params": (1, 2),
      "prev_desired_curv": (1, 100, 1),
      "features_buffer": (1, 99, 512)
    },
    "output_shapes": {
      "outputs": (1, 6512)
    },
    "output_slices": {
      "plan": slice(0, 4955),
      "lane_lines": slice(4955, 5483),
      "lane_lines_prob": slice(5483, 5491),
      "road_edges": slice(5491, 5755),
      "lead": slice(5755, 5857),
      "lead_prob": slice(5857, 5860),
      "desire_state": slice(5860, 5868),
      "meta": slice(5868, 5923),
      "desire_pred": slice(5923, 5955),
      "pose": slice(5955, 5967),
      "wide_from_device_euler": slice(5967, 5973),
      "sim_pose": slice(5973, 5985),
      "road_transform": slice(5985, 5997),
      "desired_curvature": slice(5997, 5999),
      "hidden_state": slice(5999, -1),
      "pad": slice(-1, None)
    }
  },
}


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Add model metadata from .pkl file to lookup dictionary")
  parser.add_argument("metadata_file", help="Path to *_metadata.pkl file to parse")
  parser.add_argument("--type", dest="type_key", default=None,
                      help="Type key to set (e.g., non20hz, split, 20hz)")
  args = parser.parse_args()
  basename = os.path.basename(args.metadata_file)
  dict_key = basename.replace("_metadata.pkl", "")

  metadata = parse_metadata_file(args.metadata_file, args.type_key)
  add_to_model_metadata(metadata, dict_key)
