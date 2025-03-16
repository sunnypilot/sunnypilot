"""
The MIT License

Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Last updated: July 29, 2024
"""
import os
from difflib import SequenceMatcher

from opendbc.car import structs
from openpilot.common.basedir import BASEDIR

# dict used to rename activation functions whose names aren't valid python identifiers
ACTIVATION_FUNCTION_NAMES = {'σ': 'sigmoid'}

TORQUE_NN_MODEL_PATH = os.path.join(BASEDIR, "sunnypilot", "neural_network_data", "neural_network_lateral_control")


def similarity(s1: str, s2: str) -> float:
  return SequenceMatcher(None, s1, s2).ratio()


def get_nn_model_path(CP: structs.CarParams) -> tuple[str | None, str, bool]:
  _car = CP.carFingerprint
  _eps_fw = str(next((fw.fwVersion for fw in CP.carFw if fw.ecu == "eps"), ""))
  _model_name = ""

  def check_nn_path(_check_model):
    _model_path = None
    _max_similarity = -1.0
    for f in os.listdir(TORQUE_NN_MODEL_PATH):
      if f.endswith(".json"):
        model = f.replace(".json", "").replace(f"{TORQUE_NN_MODEL_PATH}/", "")
        similarity_score = similarity(model, _check_model)
        if similarity_score > _max_similarity:
          _max_similarity = similarity_score
          _model_path = os.path.join(TORQUE_NN_MODEL_PATH, f)
    return _model_path, _max_similarity

  if len(_eps_fw) > 3:
    _eps_fw = _eps_fw.replace("\\", "")
    check_model = f"{_car} {_eps_fw}"
  else:
    check_model = _car
  model_path, max_similarity = check_nn_path(check_model)
  if 0.0 <= max_similarity < 0.9:
    check_model = _car
    model_path, max_similarity = check_nn_path(check_model)
    if 0.0 <= max_similarity < 0.9:
      model_path = None

  _model_name = os.path.splitext(os.path.basename(model_path))[0] if model_path else "MOCK"

  fuzzy_fingerprint = max_similarity < 0.99
  return model_path, _model_name, fuzzy_fingerprint
