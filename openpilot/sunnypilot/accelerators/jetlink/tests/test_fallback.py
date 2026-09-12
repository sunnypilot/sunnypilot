"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from types import SimpleNamespace

import numpy as np
from tinygrad import Tensor

from openpilot.sunnypilot.accelerators.jetlink.fallback import prepare_reset


def test_reset_clears_history_in_place_on_repeated_fallbacks():
  model = SimpleNamespace(
    input_queues={k: Tensor.zeros(4, 8, device='CPU').contiguous().realize()
                  for k in ('img_q', 'big_img_q', 'feat_q', 'desire_q')},
    prev_desire=np.ones(8), npy={'prev_feat': np.ones(32), 'desire': np.ones(8)})
  identities = {k: id(v) for k, v in model.input_queues.items()}
  reset = prepare_reset(model)
  for _ in range(3):
    for q in model.input_queues.values():
      q.assign(7).realize()
    model.prev_desire.fill(1)
    for v in model.npy.values():
      v.fill(1)
    reset()
    assert {k: id(v) for k, v in model.input_queues.items()} == identities
    for q in model.input_queues.values():
      np.testing.assert_array_equal(q.numpy(), 0)
    np.testing.assert_array_equal(model.prev_desire, 0)
    for v in model.npy.values():
      np.testing.assert_array_equal(v, 0)
