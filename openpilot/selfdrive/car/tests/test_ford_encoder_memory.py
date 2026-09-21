"""Native encoder calls must release their arguments with card's GC disabled."""
import ctypes
import gc
import weakref

import numpy as np
import pytest

from openpilot.selfdrive.controls.lib.ford_joint.encoder import DoubleArray, PairedRelease
from openpilot.selfdrive.controls.lib.ford_joint.model import MainRequest


@pytest.mark.parametrize('preview', [0., .1])
def test_native_arguments_do_not_accumulate_without_gc(preview):
  encoder = PairedRelease(MainRequest(native_lookup=True))
  kwargs = {'curvature_rate': .01, 'preview': preview, 'curvature_bound': .04}
  encoder.choose(20., .01, **kwargs)
  enabled = gc.isenabled()
  gc.collect()
  gc.disable()
  try:
    before = sum(isinstance(obj, ctypes.c_void_p) for obj in gc.get_objects())
    for _ in range(500):
      encoder.choose(20., .01, **kwargs)
    after = sum(isinstance(obj, ctypes.c_void_p) for obj in gc.get_objects())
    assert after <= before, f'{after - before} native pointer objects retained in 500 control updates'
  finally:
    gc.collect()
    if enabled:
      gc.enable()


@pytest.mark.parametrize('value', [[1., 2.], np.ones(3, dtype=np.float32), np.ones(6)[::2]])
def test_native_array_validation_is_retained(value):
  with pytest.raises(TypeError):
    DoubleArray.from_param(value)


def test_native_argument_owns_array_only_until_call_finishes():
  value = np.array([1., 2.])
  ref = weakref.ref(value)
  pointer = DoubleArray.from_param(value)
  assert pointer.value == value.ctypes.data
  del value
  assert ref() is not None
  del pointer
  assert ref() is None
