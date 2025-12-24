import numpy as np


def apply_camera_offset(model_transform, intrinsics, height, offset_param):
  camera_offset: float = offset_param
  cy = intrinsics[1, 2]
  shear = np.eye(3, dtype=np.float32)
  shear[0, 1] = camera_offset / height
  shear[0, 2] = -camera_offset / height * cy
  model_transform = (shear @ model_transform).astype(np.float32)

  return model_transform
