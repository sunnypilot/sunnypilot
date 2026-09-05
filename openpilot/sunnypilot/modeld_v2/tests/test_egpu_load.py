from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.modeld_v2.egpu_load import EGPU_LOAD_ATTEMPTS, is_lock_contention, load_with_retry


def _lock_error() -> ExceptionGroup:
  # shape of the error tinygrad raises when the am_usb flock is held by another process
  return ExceptionGroup('No interface for AMD:0 is available',
                        [FileNotFoundError(2, 'No such file or directory'),
                         RuntimeError('no pcie'),
                         RuntimeError('Failed to acquire lock file am_usb:4-2.lock')])


class TestEgpuLoad(OpenpilotTestCase):
  def test_lock_contention_detected(self):
    assert is_lock_contention(_lock_error())
    assert is_lock_contention(RuntimeError('Failed to acquire lock file am_usb:2-1.lock'))
    assert not is_lock_contention(RuntimeError('no pcie'))
    assert not is_lock_contention(RuntimeError("args mismatch in JIT: captured=(..., 'QCOM') expected=(..., 'AMD')"))

  def test_retries_on_lock_contention(self):
    calls = []

    def make_model():
      calls.append(1)
      raise _lock_error()

    model, err = load_with_retry(make_model, wait=0)
    assert model is None
    assert len(calls) == EGPU_LOAD_ATTEMPTS
    assert is_lock_contention(err)

  def test_no_retry_on_other_errors(self):
    calls = []

    def make_model():
      calls.append(1)
      raise RuntimeError('args mismatch in JIT')

    model, err = load_with_retry(make_model, wait=0)
    assert model is None
    assert len(calls) == 1
    assert isinstance(err, RuntimeError)

  def test_success_after_contention(self):
    calls = []

    def make_model():
      calls.append(1)
      if len(calls) < 3:
        raise _lock_error()
      return 'model'

    model, err = load_with_retry(make_model, wait=0)
    assert model == 'model'
    assert err is None
    assert len(calls) == 3

  def test_success_first_try(self):
    calls = []

    def make_model():
      calls.append(1)
      return 'model'

    model, err = load_with_retry(make_model, wait=0)
    assert model == 'model'
    assert err is None
    assert len(calls) == 1
