"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

A device with comma's board fitted must behave exactly as it does on develop.

The upstreaming plan rests on one claim: chestnut is native, at its own lines,
and jetlink is five sites beside it a chestnut device never reaches. This reads
modeld.py rather than importing it (that costs tinygrad, usb1 and a vision
stream) and runs the decide, load and status-publisher statements verbatim
under fakes.

Two calls that must not happen: a fitted board with PCIe trained asks
accelerators nothing, because `not CHESTNUT` is the first term; no board and
the link off stops at ready(), so prepare() never opens a link. The rest pins
the footprint: chestnut statements are develop's byte for byte, and the module
is reachable from four call sites in five hunks.
"""
import ast
import subprocess
import textwrap
import threading
import time
import unittest
from pathlib import Path
from types import SimpleNamespace

from openpilot.common.params import Params
from openpilot.sunnypilot import accelerators
from openpilot.sunnypilot.accelerators.jetlink import helpers

MODELD = Path(__file__).resolve().parents[3] / 'selfdrive' / 'modeld' / 'modeld.py'

# the zoompilot parent carries comma's chestnut unmodified, so it is the
# baseline rather than any older upstream tag
BASELINE = 'develop'

# everything core openpilot may call on the module; a name added here without
# a plan entry is a widened seam
ACCELERATOR_CALLS = {'ready', 'prepare', 'make_model_state', 'make_status_publisher'}


def _parse(src: str) -> list[ast.stmt]:
  tree = ast.parse(src)
  main = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'main')
  return main.body


def _assigns(stmt: ast.stmt, name: str) -> bool:
  return isinstance(stmt, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in stmt.targets)


def _index(body: list[ast.stmt], pred, what: str) -> int:
  for i, stmt in enumerate(body):
    if pred(stmt):
      return i
  raise AssertionError(f"modeld.py main() no longer has {what}; this test is describing a file that moved on")


def _tests_name(stmt: ast.stmt, name: str) -> bool:
  return isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Name) and stmt.test.id == name


def _run(src: str, stmts: list[ast.stmt]) -> str:
  """The verbatim source of a run of statements, dedented so it can be exec'd."""
  lines = src.splitlines()
  return textwrap.dedent('\n'.join(lines[stmts[0].lineno - 1:stmts[-1].end_lineno]))


def _git_show(ref: str, path: str) -> str | None:
  """The file at a ref, or None off a checkout that has it. Never raises."""
  try:
    out = subprocess.run(['git', 'show', f'{ref}:{path}'], cwd=MODELD.parents[3],
                         capture_output=True, text=True, timeout=30, check=False)
  except (OSError, subprocess.SubprocessError):
    return None
  return out.stdout if out.returncode == 0 else None


class FakeAccelerators:
  """The accelerators module as modeld sees it, recording every call.

  prepare() answers the most permissive thing it can, so a call that should
  never have happened fails twice over: on the recording, and on JETLINK being
  true where the plan says a chestnut owns the drive.
  """

  def __init__(self, ready=None):
    self.calls: list[str] = []
    self._ready = ready if ready is not None else (lambda: True)

  def ready(self) -> bool:
    self.calls.append('ready')
    return self._ready()

  def prepare(self) -> bool:
    self.calls.append('prepare')
    return True

  def make_model_state(self, cam_w, cam_h, small=None):
    self.calls.append('make_model_state')
    return SimpleNamespace(chestnut=True, big_model_available=True, big_model_state='joining')

  def make_status_publisher(self, pm, model):
    self.calls.append('make_status_publisher')
    return SimpleNamespace(send=lambda *a: None, big=False)


class FakeParams:
  """Params for the block under test only. The real ones belong to a car."""

  def __init__(self):
    self.store: dict[str, bool] = {}

  def put_bool(self, key, value):
    self.store[key] = bool(value)

  def get_bool(self, key):
    return bool(self.store.get(key))

  def remove(self, key):
    self.store.pop(key, None)


class FakeMessaging:
  """One chestnutState and then silence, which is the poller wait's fast path."""

  def __init__(self):
    self.polled = 0

  # Capitalised because messaging's is.
  def Poller(self):
    return self

  def poll(self, timeout_ms):
    self.polled += 1
    return [object()] if self.polled == 1 else []

  def sub_sock(self, name, poller=None, conflate=False):
    return object()

  def recv_one_or_none(self, sock):
    return SimpleNamespace(valid=True, chestnutState=object())


class FakeModelState:
  def __init__(self, cam_w, cam_h, chestnut):
    self.chestnut = chestnut

  def warmup(self):
    pass


class ModeldSeam:
  """modeld's own statements, lifted out of main() and runnable with no hardware."""

  def __init__(self):
    self.src = MODELD.read_text()
    self.body = _parse(self.src)

    decide_start = _index(self.body, lambda s: _assigns(s, 'chestnut_available'), 'the chestnut_available assignment')
    self.decide_end = _index(self.body, lambda s: _assigns(s, 'JETLINK'), 'the JETLINK assignment')
    self.decide = _run(self.src, self.body[decide_start:self.decide_end + 1])

    load_start = _index(self.body, lambda s: _assigns(s, 'model') and isinstance(s.value, ast.Constant) and s.value.value is None,
                        'the `model = None` that opens the load')
    load_end = _index(self.body, lambda s: isinstance(s, ast.Assert) and s.lineno > self.body[load_start].lineno,
                      'the `assert model is not None` that closes the load')
    self.load = _run(self.src, self.body[load_start:load_end + 1])

    pub_start = _index(self.body, lambda s: _assigns(s, 'chestnut_state'), 'the chestnut_state assignment')
    self.publish = _run(self.src, self.body[pub_start:pub_start + 2])

    self.realtime = _index(self.body, lambda s: isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                           and isinstance(s.value.func, ast.Name) and s.value.func.id == 'config_realtime_process',
                           'the config_realtime_process call')

  def decide_and_load(self, accel, present: bool, compiled: bool, trained: bool) -> dict:
    """Run the three blocks in order, exactly as main() does, and hand back its locals."""
    env: dict[str, str] = {}
    scope = {
      'chestnut_present': lambda: present,
      'chestnut_compiled': lambda: compiled,
      'chestnut_ready': lambda state: trained,
      'messaging': FakeMessaging(),
      # A short deadline: a board that never trains would otherwise wait out
      # deviceState's real period for a message the fake stops sending.
      'SERVICE_LIST': {'deviceState': SimpleNamespace(frequency=20)},
      'time': time,
      'threading': threading,
      'os': SimpleNamespace(environ=env),
      'Params': FakeParams,
      'accelerators': accel,
      'cloudlog': SimpleNamespace(warning=lambda *a, **k: None, exception=lambda *a, **k: None),
      'ModelState': FakeModelState,
      'ChestnutState': lambda pm, chestnut: SimpleNamespace(send=lambda *a: None, big=chestnut),
      'BIG_MODEL_TIMEOUT': 5,
      'vipc_client_main': SimpleNamespace(width=1928, height=1208),
      'pm': object(),
    }
    for block in (self.decide, self.load, self.publish):
      # in a function: the chestnut load declares `nonlocal big_model`. What
      # each block binds becomes a global for the next, which is how JETLINK
      # reaches the load
      wrapped = 'def _block():\n' + textwrap.indent(block, '  ') + '\n  return locals()\n'
      # exec of modeld's own source is the point of this file.
      exec(compile(wrapped, str(MODELD), 'exec'), scope)
      scope.update(scope.pop('_block')())
    scope['environ'] = env
    return scope


class NativeEquivalence(unittest.TestCase):
  """What a device gets asked, for the two configurations that must ask nothing."""

  @classmethod
  def setUpClass(cls):
    cls.seam = ModeldSeam()

  def test_a_trained_chestnut_never_asks_the_accelerator_module(self):
    accel = FakeAccelerators()
    scope = self.seam.decide_and_load(accel, present=True, compiled=True, trained=True)

    self.assertTrue(scope['CHESTNUT'])
    self.assertFalse(scope['JETLINK'])
    # not "prepare was not called": nothing was, because `not CHESTNUT` is
    # the first term
    self.assertEqual(accel.calls, [], "a fitted chestnut asked the accelerator module something")
    self.assertEqual(scope['environ'].get('HCQDEV_WAIT_TIMEOUT_MS'), '3000')
    self.assertTrue(scope['model'].chestnut)
    self.assertIsNotNone(scope['chestnut_state'])

  def test_no_board_and_the_link_off_stops_at_ready(self):
    # the real module with the link off: ready() reads one param and nothing
    # opens a gadget
    Params().remove(helpers.P_ENABLED)
    self.assertFalse(accelerators.ready())

    accel = FakeAccelerators(ready=accelerators.ready)
    scope = self.seam.decide_and_load(accel, present=False, compiled=False, trained=False)

    self.assertFalse(scope['CHESTNUT'])
    self.assertFalse(scope['JETLINK'])
    self.assertEqual(accel.calls, ['ready'], "the disabled link was asked more than whether it is ready")
    self.assertNotIn('prepare', accel.calls)
    self.assertNotIn('make_model_state', accel.calls)
    self.assertNotIn('make_status_publisher', accel.calls)
    # The small model drives, and nothing publishes accelerator status.
    self.assertFalse(scope['model'].chestnut)
    self.assertIsNone(scope['chestnut_state'])

  def test_a_board_that_never_trains_falls_through_to_the_question(self):
    # a chestnut device does ask, once, when the board is fitted but PCIe never
    # trains inside the poller wait: CHESTNUT is false, same as a bare device
    accel = FakeAccelerators(ready=lambda: False)
    scope = self.seam.decide_and_load(accel, present=True, compiled=True, trained=False)

    self.assertFalse(scope['CHESTNUT'])
    self.assertFalse(scope['JETLINK'])
    self.assertEqual(accel.calls, ['ready'])

  def test_the_link_is_decided_before_the_process_goes_realtime(self):
    # prepare() starts tinygrad's device thread; after config_realtime_process
    # it would inherit SCHED_FIFO 54 on core 7 and preempt the frame loop
    self.assertLess(self.seam.decide_end, self.seam.realtime,
                    "the JETLINK decision moved after config_realtime_process")


class UpstreamFootprint(unittest.TestCase):
  """modeld.py stays five hunks wide, and chestnut's lines stay develop's."""

  @classmethod
  def setUpClass(cls):
    cls.src = MODELD.read_text()
    cls.tree = ast.parse(cls.src)
    cls.body = _parse(cls.src)

  def _baseline_body(self) -> list[ast.stmt] | None:
    src = _git_show(BASELINE, 'openpilot/selfdrive/modeld/modeld.py')
    if src is None:
      return None
    self.baseline_src = src
    return _parse(src)

  def _skip_without_baseline(self, body):
    if body is None:
      self.skipTest(f"no {BASELINE} here: not a checkout of this fork, or the branch is gone")

  def test_the_module_is_reachable_from_four_calls_in_five_hunks(self):
    lines = self.src.splitlines()
    calls = [(n.lineno, n.attr) for n in ast.walk(self.tree)
             if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == 'accelerators']
    sites = [f"  modeld.py:{lineno} {lines[lineno - 1].strip()}" for lineno, _ in calls]

    # the five hunks: decision, load, status publisher, fallback re-raise and
    # the modelDataV2SP fields. Lines closer than a hunk's context are one
    # hunk, so `if not JETLINK:` is part of the load
    jetlink = sorted({n.lineno for n in ast.walk(self.tree) if isinstance(n, ast.Name) and n.id == 'JETLINK'}
                     | {lineno for lineno, _ in calls})
    hunk_starts = [line for i, line in enumerate(jetlink) if i == 0 or line - jetlink[i - 1] > 8]
    detail = '\n'.join(sites + [f"  hunks start at lines {hunk_starts}"])

    self.assertEqual({attr for _, attr in calls}, ACCELERATOR_CALLS, f"the seam widened:\n{detail}")
    self.assertEqual(len(calls), 4, f"expected ready/prepare/make_model_state/make_status_publisher and nothing else:\n{detail}")
    self.assertEqual(len(hunk_starts), 5, f"modeld.py's jetlink path is no longer five hunks:\n{detail}")

  def test_the_chestnut_block_never_mentions_the_accelerator_module(self):
    for stmt in ast.walk(self.tree):
      if not _tests_name(stmt, 'CHESTNUT'):
        continue
      # body only: the orelse of the load is the `elif JETLINK` hunk.
      names = {n.id for stmt_ in stmt.body for n in ast.walk(stmt_) if isinstance(n, ast.Name)}
      self.assertNotIn('accelerators', names, f"an `if CHESTNUT:` block at line {stmt.lineno} reaches the accelerator module")
      self.assertNotIn('JETLINK', names, f"an `if CHESTNUT:` block at line {stmt.lineno} reads JETLINK")

  def test_chestnut_state_is_the_baselines(self):
    body = self._baseline_body()
    self._skip_without_baseline(body)
    ours = next((n for n in self.tree.body if isinstance(n, ast.ClassDef) and n.name == 'ChestnutState'), None)
    theirs = next((n for n in ast.parse(self.baseline_src).body if isinstance(n, ast.ClassDef) and n.name == 'ChestnutState'), None)
    self.assertIsNotNone(ours, "ChestnutState left modeld.py again")
    self.assertIsNotNone(theirs)
    self.assertEqual(ast.get_source_segment(self.src, ours), ast.get_source_segment(self.baseline_src, theirs),
                     f"class ChestnutState differs from {BASELINE}")

  def test_the_poller_wait_and_the_chestnut_load_are_the_baselines(self):
    body = self._baseline_body()
    self._skip_without_baseline(body)

    def wait(b):
      return next(s for s in b if _tests_name(s, 'chestnut_available'))

    def load(b):
      return next(s for s in b if _tests_name(s, 'CHESTNUT') and len(s.body) > 2)

    self.assertEqual(_run(self.src, [wait(self.body)]), _run(self.baseline_src, [wait(body)]),
                     f"the chestnutState poller wait differs from {BASELINE}")
    # The body only. Our orelse is the `elif JETLINK:` hunk, which is the point.
    self.assertEqual(_run(self.src, load(self.body).body), _run(self.baseline_src, load(body).body),
                     f"the `if CHESTNUT:` load differs from {BASELINE}")

  def test_the_fallback_is_the_baseline_behind_one_guard(self):
    body = self._baseline_body()
    self._skip_without_baseline(body)

    def handler(b):
      return next(h for n in b for x in ast.walk(n) if isinstance(x, ast.Try)
                  for h in x.handlers if any('ChestnutActive' in ast.dump(s) for s in ast.walk(h)))

    ours = handler(self.body)
    theirs = handler(body)
    guard = ours.body[0]
    self.assertTrue(_tests_name(guard, 'JETLINK') and isinstance(guard.body[0], ast.Raise),
                    "the fallback no longer opens with `if JETLINK: raise`")
    # everything after the guard is develop's handler: a small-model fault is
    # still fatal and a chestnut still demotes itself
    self.assertEqual(_run(self.src, ours.body[1:]), _run(self.baseline_src, theirs.body),
                     f"the big-model fallback differs from {BASELINE}")


if __name__ == '__main__':
  unittest.main()
