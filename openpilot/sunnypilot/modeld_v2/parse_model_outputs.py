import numpy as np
from openpilot.sunnypilot.modeld_v2.constants import ModelConstants


def safe_exp(x, out=None):
  # -11 is around 10**14, more causes float16 overflow
  return np.exp(np.clip(x, -np.inf, 11), out=out)


def sigmoid(x):
  return 1. / (1. + safe_exp(-x))


def softmax(x, axis=-1):
  x -= np.max(x, axis=axis, keepdims=True)
  if x.dtype == np.float32 or x.dtype == np.float64:
    safe_exp(x, out=x)
  else:
    x = safe_exp(x)
  x /= np.sum(x, axis=axis, keepdims=True)
  return x


def _infer_mhp(slice_size: int, prod_out_shape: int, max_in_n: int = 16, max_out_n: int = 6) -> tuple[int, int]:
  for out_n in range(max_out_n + 1):
    per = 2 * prod_out_shape + out_n
    if per <= 0:
      continue
    if slice_size % per == 0:
      in_n = slice_size // per
      if 1 <= in_n <= max_in_n:
        return in_n, out_n
  return 1, 0  # single hypothesis, no weights — matches a non-MDN output


class Parser:
  def __init__(self, ignore_missing=False):
    self.ignore_missing = ignore_missing

  def check_missing(self, outs, name):
    if name not in outs and not self.ignore_missing:
      raise ValueError(f"Missing output {name}")
    return name not in outs

  def parse_categorical_crossentropy(self, name, outs, out_shape=None):
    if self.check_missing(outs, name):
      return
    raw = outs[name]
    if out_shape is not None:
      raw = raw.reshape((raw.shape[0],) + out_shape)
    outs[name] = softmax(raw, axis=-1)

  def parse_binary_crossentropy(self, name, outs):
    if self.check_missing(outs, name):
      return
    raw = outs[name]
    outs[name] = sigmoid(raw)

  def parse_mdn(self, name, outs, out_shape, in_N=0, out_N=0):
    if self.check_missing(outs, name):
      return
    raw = outs[name]

    if in_N == 0 and out_N == 0:
      prod = int(np.prod(out_shape))
      in_N, out_N = _infer_mhp(raw.shape[1], prod)

    raw = raw.reshape((raw.shape[0], in_N, -1))

    n_values = (raw.shape[2] - out_N)//2
    pred_mu = raw[:,:,:n_values]
    pred_std = safe_exp(raw[:,:,n_values: 2*n_values])

    if in_N > 1 and out_N > 0:
      weights = np.zeros((raw.shape[0], in_N, out_N), dtype=raw.dtype)
      for i in range(out_N):
        weights[:,:,i - out_N] = softmax(raw[:,:,i - out_N], axis=-1)

      if out_N == 1:
        for fidx in range(weights.shape[0]):
          idxs = np.argsort(weights[fidx][:,0])[::-1]
          weights[fidx] = weights[fidx][idxs]
          pred_mu[fidx] = pred_mu[fidx][idxs]
          pred_std[fidx] = pred_std[fidx][idxs]
      full_shape = tuple([raw.shape[0], in_N] + list(out_shape))
      outs[name + '_weights'] = weights
      outs[name + '_hypotheses'] = pred_mu.reshape(full_shape)
      outs[name + '_stds_hypotheses'] = pred_std.reshape(full_shape)

      pred_mu_final = np.zeros((raw.shape[0], out_N, n_values), dtype=raw.dtype)
      pred_std_final = np.zeros((raw.shape[0], out_N, n_values), dtype=raw.dtype)
      for fidx in range(weights.shape[0]):
        for hidx in range(out_N):
          idxs = np.argsort(weights[fidx,:,hidx])[::-1]
          pred_mu_final[fidx, hidx] = pred_mu[fidx, idxs[0]]
          pred_std_final[fidx, hidx] = pred_std[fidx, idxs[0]]
    elif in_N > 1 and out_N == 0:
      # MHP without weights: keep every hypothesis intact, surface them as
      # ``*_hypotheses`` and propagate the full multi-hypothesis tensor.
      full_shape = tuple([raw.shape[0], in_N] + list(out_shape))
      outs[name + '_hypotheses'] = pred_mu.reshape(full_shape)
      outs[name + '_stds_hypotheses'] = pred_std.reshape(full_shape)
      pred_mu_final = pred_mu
      pred_std_final = pred_std
    else:
      pred_mu_final = pred_mu
      pred_std_final = pred_std

    if out_N > 1 or (in_N > 1 and out_N == 0):
      n_selections = out_N if out_N > 1 else in_N
      final_shape = tuple([raw.shape[0], n_selections] + list(out_shape))
    else:
      final_shape = tuple([raw.shape[0],] + list(out_shape))
    outs[name] = pred_mu_final.reshape(final_shape)
    outs[name + '_stds'] = pred_std_final.reshape(final_shape)

  def parse_outputs(self, outs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    # supercombo (4955 / 102) and newer variants (e.g. 990 / 144).
    self.parse_mdn('plan',   outs, out_shape=(ModelConstants.IDX_N, ModelConstants.PLAN_WIDTH))
    self.parse_mdn('lane_lines', outs, out_shape=(ModelConstants.NUM_LANE_LINES, ModelConstants.IDX_N, ModelConstants.LANE_LINES_WIDTH))
    self.parse_mdn('road_edges', outs, out_shape=(ModelConstants.NUM_ROAD_EDGES, ModelConstants.IDX_N, ModelConstants.LANE_LINES_WIDTH))
    self.parse_mdn('pose',         outs, out_shape=(ModelConstants.POSE_WIDTH,))
    self.parse_mdn('road_transform', outs, out_shape=(ModelConstants.POSE_WIDTH,))
    if 'sim_pose' in outs:
      self.parse_mdn('sim_pose', outs, out_shape=(ModelConstants.POSE_WIDTH,))
    self.parse_mdn('wide_from_device_euler', outs, out_shape=(ModelConstants.WIDE_FROM_DEVICE_WIDTH,))
    self.parse_mdn('lead', outs, out_shape=(ModelConstants.LEAD_TRAJ_LEN, ModelConstants.LEAD_WIDTH))
    if 'lat_planner_solution' in outs:
      self.parse_mdn('lat_planner_solution', outs, out_shape=(ModelConstants.IDX_N, ModelConstants.LAT_PLANNER_SOLUTION_WIDTH))
    if 'desired_curvature' in outs:
      self.parse_mdn('desired_curvature', outs, out_shape=(ModelConstants.DESIRED_CURV_WIDTH,))
    for k in ['lead_prob', 'lane_lines_prob', 'meta']:
      self.parse_binary_crossentropy(k, outs)
    self.parse_categorical_crossentropy('desire_state', outs, out_shape=(ModelConstants.DESIRE_PRED_WIDTH,))
    self.parse_categorical_crossentropy('desire_pred',  outs, out_shape=(ModelConstants.DESIRE_PRED_LEN, ModelConstants.DESIRE_PRED_WIDTH))
    return outs
