"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from tinygrad import Tensor, TinyJit


def prepare_reset(model):
  """Capture reset before driving, keeping the small JIT's buffer identities.

  Its history is stale after the Jetson ran, so fallback starts from the same
  zero history as modeld startup. Nothing is allocated or compiled on the
  failure frame.
  """
  queues = tuple(model.input_queues[k] for k in ('img_q', 'big_img_q', 'feat_q', 'desire_q'))

  @TinyJit
  def clear():
    Tensor.realize(*(q.assign(0) for q in queues))

  for _ in range(3):
    clear()

  def reset():
    clear()
    model.prev_desire.fill(0)
    model.npy['prev_feat'].fill(0)
    model.npy['desire'].fill(0)

  return reset
