import numpy as np
from openpilot.sunnypilot.models.split_model_constants import SplitModelConstants


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

  def parse_mdn(self, name, outs, in_N=0, out_N=1, out_shape=None):
    if self.check_missing(outs, name):
      return
    raw = outs[name]
    raw = raw.reshape((raw.shape[0], max(in_N, 1), -1))

    n_values = (raw.shape[2] - out_N)//2
    pred_mu = raw[:,:,:n_values]
    pred_std = safe_exp(raw[:,:,n_values: 2*n_values])

    if in_N > 1:
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
    else:
      pred_mu_final = pred_mu
      pred_std_final = pred_std

    if out_N > 1:
      final_shape = tuple([raw.shape[0], out_N] + list(out_shape))
    else:
      final_shape = tuple([raw.shape[0],] + list(out_shape))
    outs[name] = pred_mu_final.reshape(final_shape)
    outs[name + '_stds'] = pred_std_final.reshape(final_shape)

  def split_outputs(self, outs: dict[str, np.ndarray]) -> None:
    if 'lane_lines' in outs:
      self.parse_mdn('lane_lines', outs, in_N=0, out_N=0,
                     out_shape=(SplitModelConstants.NUM_LANE_LINES,SplitModelConstants.IDX_N,SplitModelConstants.LANE_LINES_WIDTH))
      self.parse_mdn('road_edges', outs, in_N=0, out_N=0,
                     out_shape=(SplitModelConstants.NUM_ROAD_EDGES,SplitModelConstants.IDX_N,SplitModelConstants.LANE_LINES_WIDTH))
      self.parse_mdn('lead', outs, in_N=SplitModelConstants.LEAD_MHP_N, out_N=SplitModelConstants.LEAD_MHP_SELECTION,
                     out_shape=(SplitModelConstants.LEAD_TRAJ_LEN,SplitModelConstants.LEAD_WIDTH))
      if 'sim_pose' in outs:
        self.parse_mdn('sim_pose', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.POSE_WIDTH,))
      for k in ['lead_prob', 'lane_lines_prob']:
        self.parse_binary_crossentropy(k, outs)

  def parse_vision_outputs(self, outs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    self.parse_mdn('pose', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.POSE_WIDTH,))
    self.parse_mdn('wide_from_device_euler', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.WIDE_FROM_DEVICE_WIDTH,))
    self.parse_mdn('road_transform', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.POSE_WIDTH,))
    self.split_outputs(outs)
    self.parse_categorical_crossentropy('desire_pred', outs, out_shape=(SplitModelConstants.DESIRE_PRED_LEN,SplitModelConstants.DESIRE_PRED_WIDTH))
    self.parse_binary_crossentropy('meta', outs)
    return outs

  def parse_policy_outputs(self, outs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    self.parse_mdn('plan', outs, in_N=SplitModelConstants.PLAN_MHP_N, out_N=SplitModelConstants.PLAN_MHP_SELECTION,
                   out_shape=(SplitModelConstants.IDX_N,SplitModelConstants.PLAN_WIDTH))
    self.split_outputs(outs)
    if 'lat_planner_solution' in outs:
      self.parse_mdn('lat_planner_solution', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.IDX_N,SplitModelConstants.LAT_PLANNER_SOLUTION_WIDTH))
    if 'desired_curvature' in outs:
      self.parse_mdn('desired_curvature', outs, in_N=0, out_N=0, out_shape=(SplitModelConstants.DESIRED_CURV_WIDTH,))
    self.parse_categorical_crossentropy('desire_state', outs, out_shape=(SplitModelConstants.DESIRE_PRED_WIDTH,))
    return outs

  def parse_outputs(self, outs: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    outs = self.parse_vision_outputs(outs)
    outs = self.parse_policy_outputs(outs)
    return outs
