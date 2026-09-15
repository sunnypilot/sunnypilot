"""Exercise manual input and the manager entrypoint against real IPC sockets."""
import multiprocessing
import shutil
import threading
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest

from openpilot.cereal import messaging
from openpilot.common.hardware.hw import Paths
from openpilot.tools.joystick import joystick_control as frontend


def run_frontend(role, pipe):
  class Input:
    axes_values = {'gb': 0., 'steer': .05 if role == 'manual' else 0.}
    axes_order = ['gb', 'steer']
    ford_channel = 'c0' if role == 'manual' else 'standard'

    def update(self):
      command = pipe.recv()
      if command == 'stop':
        raise SystemExit
      self.axes_values['steer'] = command

  frontend.Params = lambda: SimpleNamespace(put_bool=lambda *a, **kw: pipe.send('enabled'))
  frontend.Joystick = Input
  threading.excepthook = lambda args: pipe.send(type(args.exc_value).__name__)
  pipe.send('ready')
  if role == 'manager':
    frontend.main()
  else:
    frontend.joystick_control_thread(Input())


@contextmanager
def publisher(role):
  context = multiprocessing.get_context('spawn')
  parent, child = context.Pipe()
  process = context.Process(target=run_frontend, args=(role, child))
  process.start()
  child.close()
  try:
    assert parent.poll(10), 'frontend failed to start'
    assert parent.recv() == 'ready'
    yield process, parent
  finally:
    if process.is_alive():
      process.terminate()
    process.join(5)
    if process.is_alive():
      process.kill()
      process.join(5)
    parent.close()
    process.close()


@pytest.fixture
def joystick_socket(monkeypatch):
  prefix = 'joystick_test_' + uuid.uuid4().hex
  monkeypatch.setenv('OPENPILOT_PREFIX', prefix)
  monkeypatch.delenv('ZMQ', raising=False)
  directory = Path(Paths.shm_path()) / ('msgq_' + prefix)
  directory.mkdir()
  messaging.reset_context()
  socket = messaging.sub_sock('testJoystick', conflate=True, timeout=1000)
  try:
    yield socket
  finally:
    del socket
    shutil.rmtree(directory)
    (Path(Paths.shm_path()) / ('joystick_control' + prefix + '.lock')).unlink(missing_ok=True)
    messaging.reset_context()


def assert_stream(socket, channel, steer, duration=.3):
  deadline = time.monotonic() + duration
  while time.monotonic() < deadline:
    message = messaging.recv_one(socket)
    assert message is not None, 'joystick publisher stopped transmitting'
    assert message.testJoystick.fordChannel == channel, 'another input source stole testJoystick'
    assert list(message.testJoystick.axes) == pytest.approx([0., steer])


def test_onroad_manager_does_not_replace_keyboard_publisher(joystick_socket):
  with publisher('manual') as (_, manual):
    assert manual.poll(5) and manual.recv() == 'enabled'
    assert_stream(joystick_socket, 'c0', .05)
    with publisher('manager'):
      assert_stream(joystick_socket, 'c0', .05)
      assert not manual.poll(), 'keyboard sender raised an exception'


@pytest.mark.parametrize('abrupt', [False, True])
def test_manager_can_publish_after_keyboard_exits(joystick_socket, abrupt):
  with publisher('manual') as (manual_process, manual):
    assert manual.poll(5) and manual.recv() == 'enabled'
    assert_stream(joystick_socket, 'c0', .05)
    with publisher('manager') as (_, manager):
      assert_stream(joystick_socket, 'c0', .05)
      assert not manager.poll(), 'manager enabled a competing publisher'
      if abrupt:
        manual_process.kill()
      else:
        manual.send('stop')
      manual_process.join(5)
      assert not manual_process.is_alive()
      if not abrupt:
        assert manual_process.exitcode == 0
      assert manager.poll(5) and manager.recv() == 'enabled'
      messaging.drain_sock(joystick_socket)
      assert_stream(joystick_socket, 'standard', 0.)


def test_second_manual_session_exits_without_replacing_first(joystick_socket):
  with publisher('manual') as (_, manual):
    assert manual.poll(5) and manual.recv() == 'enabled'
    assert_stream(joystick_socket, 'c0', .05)
    with publisher('manual') as (duplicate_process, duplicate):
      duplicate_process.join(5)
      assert duplicate_process.exitcode == 0, 'duplicate frontend did not exit'
      with pytest.raises(EOFError):
        duplicate.recv()  # A rejected instance must not enable the mode or start a sender.
      assert_stream(joystick_socket, 'c0', .05)
      assert not manual.poll(), 'original keyboard sender raised an exception'


def test_automatic_gamepad_publishes_normally_without_manual_session(joystick_socket):
  with publisher('manager') as (_, manager):
    assert manager.poll(5) and manager.recv() == 'enabled'
    assert_stream(joystick_socket, 'standard', 0.)
