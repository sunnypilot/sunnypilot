from typing import Any
import codecs
import pickle
from tinygrad.nn.onnx import OnnxPBParser

class MetadataOnnxPBParser(OnnxPBParser):
  def _parse_ModelProto(self) -> dict:
    obj: dict[str, Any] = {"graph": {"input": [], "output": []}, "metadata_props": []}
    for fid, wire_type in self._parse_message(self.reader.len):
      match fid:
        case 7:
          obj["graph"] = self._parse_GraphProto()
        case 14:
          obj["metadata_props"].append(self._parse_StringStringEntryProto())
        case _:
          self.reader.skip_field(wire_type)
    return obj

def _get_name_and_shape(value_info: dict[str, Any]) -> tuple[str, tuple[int, ...]]:
  shape = tuple(int(dim) if isinstance(dim, int) else 1 for dim in value_info["parsed_type"].shape)
  return value_info["name"], shape

def _get_metadata_value_by_name(model: dict[str, Any], name: str) -> str | None:
  for prop in model["metadata_props"]:
    if prop["key"] == name:
      return prop["value"]
  return None

def make_metadata_dict(onnx_path):
  model = MetadataOnnxPBParser(onnx_path).parse()
  output_slices_raw = _get_metadata_value_by_name(model, 'output_slices')

  if output_slices_raw:
    output_slices = pickle.loads(codecs.decode(output_slices_raw.encode(), "base64"))
  else:
    output_slices = {}

  input_shapes = dict(_get_name_and_shape(x) for x in model["graph"]["input"])
  metadata = {prop["key"]: prop["value"] for prop in model["metadata_props"]}

  if 'hidden_state' not in output_slices:
    output_slices['hidden_state'] = slice(0, 512)

  return {
    'input_shapes': input_shapes,
    'output_slices': output_slices,
    'metadata_props': metadata
  }
