#!/usr/bin/env python3
"""
Adds "Plan-Aligned Braking (Alpha)" to sunnypilot, mirroring how Blendful (#2073 + #2081) is wired.

Run from the sunnypilot repo root (the directory that contains `openpilot/`):

    python3 add_plan_align_braking.py            # apply
    python3 add_plan_align_braking.py --check    # only report whether everything is applied

What it does (idempotent: safe to re-run):
  1. openpilot/common/params_keys.h                                  new param  PlanAlignBraking (bool, default OFF, BACKUP)
  2. openpilot/sunnypilot/selfdrive/controls/lib/plan_align.py        NEW  the logic + default-model gate
  3. openpilot/sunnypilot/selfdrive/controls/lib/tests/test_plan_align.py   NEW  unit tests
  4. openpilot/selfdrive/controls/lib/longitudinal_planner.py         3 tiny hooks (import / init / one call)
  5. openpilot/selfdrive/ui/sunnypilot/layouts/settings/models.py     TICI/C3X toggle, "(Alpha)", locked on Default model
  6. openpilot/selfdrive/ui/sunnypilot/mici/layouts/models.py         mici toggle, locked on Default model
  7. openpilot/sunnypilot/sunnylink/settings_ui_src/pages/models.yaml sunnylink toggle (gated by existing `custom_model` macro)
  8. openpilot/sunnypilot/sunnylink/settings_ui.json                  regenerated with the repo's own compile_settings_ui.py

After running: rebuild (params_keys.h changed -> `scons` / rebuild libparams), then run
    pytest openpilot/sunnypilot/selfdrive/controls/lib/tests/test_plan_align.py
    pytest openpilot/sunnypilot/sunnylink/tests/test_compile_settings_ui.py
"""
import os
import subprocess
import sys
import py_compile

CHECK_ONLY = "--check" in sys.argv
ROOT = os.getcwd()
OP = os.path.join(ROOT, "openpilot")
if not os.path.isfile(os.path.join(OP, "common", "params_keys.h")):
  sys.exit("Run this from the sunnypilot repo root (the folder containing `openpilot/`).")

PARAM = "PlanAlignBraking"
TITLE = "Plan-Aligned Braking (Alpha)"
DESC_A = "Brakes harder toward the model's own planned stop when there is no lead car, "
DESC_B = "such as approaching a red light, especially at higher speeds. Never reduces braking. "
DESC_C = "Not available with the Default model."
DESC = DESC_A + DESC_B + DESC_C

status: list[str] = []


def p(*parts):
  return os.path.join(OP, *parts)


def read(path):
  with open(path, encoding="utf-8") as f:
    return f.read()


def write(path, text):
  with open(path, "w", encoding="utf-8") as f:
    f.write(text)


def patch(path, edits, marker):
  """edits: list of (anchor, replacement). Every anchor must occur exactly once."""
  rel = os.path.relpath(path, ROOT)
  src = read(path)
  if marker in src:
    status.append(f"[already applied] {rel}")
    return
  if CHECK_ONLY:
    status.append(f"[NOT applied]     {rel}")
    return
  for anchor, repl in edits:
    n = src.count(anchor)
    if n != 1:
      sys.exit(f"ERROR in {rel}: expected anchor exactly once, found {n}x:\n{anchor!r}\n"
               "The file differs from the sunnypilot master this script was written against. Nothing further was changed.")
    src = src.replace(anchor, repl)
  write(path, src)
  status.append(f"[patched]         {rel}")


def create(path, text):
  rel = os.path.relpath(path, ROOT)
  if os.path.exists(path):
    status.append(f"[exists, kept]    {rel}")
    return
  if CHECK_ONLY:
    status.append(f"[NOT created]     {rel}")
    return
  os.makedirs(os.path.dirname(path), exist_ok=True)
  write(path, text)
  status.append(f"[created]         {rel}")


# pre-flight: refuse (changing nothing) if the earlier standalone planner patch is present
_planner = p("selfdrive", "controls", "lib", "longitudinal_planner.py")
_ps = read(_planner)
if "class PlanAlign:" in _ps or "plan_aligned_accel" in _ps:
  sys.exit("The stock longitudinal_planner.py already contains the earlier standalone plan-align patch (apply_plan_align_fix*.py).\n"
           "Revert it first:  git checkout openpilot/selfdrive/controls/lib/longitudinal_planner.py   then re-run this script.")

# ----------------------------------------------------------------------------------------------------------------------
# 1. params_keys.h
# ----------------------------------------------------------------------------------------------------------------------
patch(p("common", "params_keys.h"), [
  ('    {"Blendful", {PERSISTENT | BACKUP, BOOL, "0"}},\n',
   '    {"Blendful", {PERSISTENT | BACKUP, BOOL, "0"}},\n'
   f'    {{"{PARAM}", {{PERSISTENT | BACKUP, BOOL, "0"}}}},\n'),
], f'"{PARAM}"')

# ----------------------------------------------------------------------------------------------------------------------
# 2. logic module
# ----------------------------------------------------------------------------------------------------------------------
PLAN_ALIGN_PY = '''"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.

Plan-Aligned Braking (alpha).

Models that output both a plan (modelV2.velocity / position) and a learned action head (modelV2.action.desiredAcceleration)
can disagree: when decelerating hard, the action head commands less braking than the plan implies. With no lead car the e2e
candidate is the only braking source in the planner's min(mpc, cruise, e2e), so the shortfall reaches the car as creeping
toward stops and overshooting red lights, worse at higher speed (decel needed for a fixed stopping distance scales with v^2).

This pulls the e2e accel toward the stronger of
  a_plan : accel implied by the plan's speed change over HORIZON seconds
  a_stop : constant decel needed to stop at the stop point the plan itself predicts (-v^2 / 2d)
Only ever toward HARDER braking, only while the action accel is already braking, never with a lead, and floored.

Gate: Custom (non-Default) models only, same condition as Blendful / sunnylink `custom_model_active`.
"""
import numpy as np

from openpilot.cereal import custom
from openpilot.common.filter_simple import FirstOrderFilter
from openpilot.common.params import Params
from openpilot.common.realtime import DT_MDL
from openpilot.selfdrive.modeld.constants import ModelConstants

PARAM = "PlanAlignBraking"

BETA = 0.7          # 0 = off, 1 = follow the plan fully
HORIZON = 1.0       # s, plan lookahead for a_plan
FLOOR = -3.0        # m/s^2, never push the aligned command below this (stock ACCEL_MIN is -3.5)
STOP_V = 0.3        # m/s, plan speed below this counts as "stopped"
MIN_V = 2.0         # m/s, ignore the stop-point term below this speed
MIN_DIST = 3.0      # m, avoid blow-up when the predicted stop point is very close
TAU = 0.5           # s, smoothing of the stop-point term
RAMP = 0.3          # m/s^2, correction fades in as the action accel goes from 0 to -RAMP (no effect while cruising/accelerating)
PARAM_CHECK_FRAMES = int(1.0 / DT_MDL)


class PlanAlignBraking:
  def __init__(self):
    self.params = Params()
    self.enabled = False
    self._frame = 0
    self.a_stop_f = FirstOrderFilter(0.0, TAU, DT_MDL)
    self._read_params()

  def _read_params(self) -> None:
    # runner the manager launches; Default (stock) model is excluded
    custom_model = self.params.get("ModelRunnerTypeCache") == custom.ModelManagerSP.Runner.tinygrad
    self.enabled = bool(custom_model and self.params.get_bool(PARAM))

  def update_params(self) -> None:
    if self._frame % PARAM_CHECK_FRAMES == 0:
      self._read_params()
    self._frame += 1

  def update(self, model_msg, a_action: float, has_lead: bool) -> float:
    self.update_params()
    if not self.enabled:
      self.a_stop_f.x = 0.0
      return a_action

    t = ModelConstants.T_IDXS
    v = np.array(model_msg.velocity.x)
    x = np.array(model_msg.position.x)
    if len(v) != len(t) or len(x) != len(t):
      self.a_stop_f.x = 0.0
      return a_action

    a_plan = (np.interp(HORIZON, t, v) - v[0]) / HORIZON
    a_stop = 0.0
    if v[0] > MIN_V:
      idx = np.flatnonzero(v < STOP_V)
      if idx.size:
        a_stop = -v[0] ** 2 / (2.0 * max(x[idx[0]], MIN_DIST))
    a_stop = self.a_stop_f.update(a_stop)

    if has_lead:
      return a_action

    a_tgt = min(a_plan, a_stop)
    w = float(np.clip(-a_action / RAMP, 0.0, 1.0))
    a_out = a_action + BETA * w * min(a_tgt - a_action, 0.0)
    return float(max(a_out, min(a_action, FLOOR)))
'''
create(p("sunnypilot", "selfdrive", "controls", "lib", "plan_align.py"), PLAN_ALIGN_PY)

# ----------------------------------------------------------------------------------------------------------------------
# 3. tests
# ----------------------------------------------------------------------------------------------------------------------
TEST_PY = '''"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import types

import numpy as np

from openpilot.cereal import custom
from openpilot.common.test import OpenpilotTestCase
from openpilot.selfdrive.modeld.constants import ModelConstants
from openpilot.sunnypilot.selfdrive.controls.lib import plan_align
from openpilot.sunnypilot.selfdrive.controls.lib.plan_align import PlanAlignBraking

Runner = custom.ModelManagerSP.Runner
T = np.array(ModelConstants.T_IDXS)


class FakeParams:
  def __init__(self, runner, toggle):
    self.runner, self.toggle = runner, toggle

  def get(self, key):
    return int(self.runner) if key == "ModelRunnerTypeCache" else None

  def get_bool(self, key):
    return self.toggle if key == plan_align.PARAM else False


def make(runner=Runner.tinygrad, toggle=True) -> PlanAlignBraking:
  pa = PlanAlignBraking()
  pa.params = FakeParams(runner, toggle)
  pa._read_params()
  return pa


def stop_plan(v0, d_stop):
  """constant-decel plan that stops exactly at d_stop"""
  a = v0 ** 2 / (2 * d_stop)
  ts = v0 / a
  v = np.clip(v0 - a * T, 0, None)
  x = np.where(T < ts, v0 * T - 0.5 * a * T ** 2, d_stop)
  return types.SimpleNamespace(velocity=types.SimpleNamespace(x=list(v)), position=types.SimpleNamespace(x=list(x)))


def cruise_plan(v0=20.0):
  return types.SimpleNamespace(velocity=types.SimpleNamespace(x=[v0] * len(T)), position=types.SimpleNamespace(x=list(v0 * T)))


def run(pa, msg, a_action, has_lead=False, n=30):
  out = a_action
  for _ in range(n):
    out = pa.update(msg, a_action, has_lead)
  return out


class TestPlanAlignBraking(OpenpilotTestCase):
  def test_default_model_is_excluded(self):
    assert not make(runner=Runner.stock, toggle=True).enabled

  def test_custom_model_needs_toggle(self):
    assert make(runner=Runner.tinygrad, toggle=True).enabled
    assert not make(runner=Runner.tinygrad, toggle=False).enabled

  def test_disabled_is_passthrough(self):
    assert run(make(Runner.stock, True), stop_plan(80 / 3.6, 120), -1.3) == -1.3

  def test_high_speed_stop_brakes_harder(self):
    out = run(make(), stop_plan(80 / 3.6, 120), -1.3)
    assert -2.1 < out < -1.5  # needed ~ -2.06, beta 0.7 closes most of the gap

  def test_never_weaker_and_respects_floor(self):
    out = run(make(), stop_plan(80 / 3.6, 60), -1.3)  # would need ~ -4.1
    assert plan_align.FLOOR - 1e-6 <= out <= -1.3
    assert run(make(), stop_plan(15.0, 60), -2.5) == -2.5  # action already harder than plan

  def test_lead_is_untouched(self):
    assert run(make(), stop_plan(80 / 3.6, 120), -1.3, has_lead=True) == -1.3

  def test_cruise_and_acceleration_untouched(self):
    assert run(make(), cruise_plan(), 0.1) == 0.1
    assert run(make(), stop_plan(15.0, 60), 0.8) == 0.8

  def test_bad_plan_length_is_passthrough(self):
    bad = types.SimpleNamespace(velocity=types.SimpleNamespace(x=[1.0, 2.0]), position=types.SimpleNamespace(x=[1.0, 2.0]))
    assert run(make(), bad, -1.0) == -1.0
'''
create(p("sunnypilot", "selfdrive", "controls", "lib", "tests", "test_plan_align.py"), TEST_PY)

# ----------------------------------------------------------------------------------------------------------------------
# 4. stock planner hooks
# ----------------------------------------------------------------------------------------------------------------------
patch(p("selfdrive", "controls", "lib", "longitudinal_planner.py"), [
  ("from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP\n",
   "from openpilot.sunnypilot.selfdrive.controls.lib.longitudinal_planner import LongitudinalPlannerSP\n"
   "from openpilot.sunnypilot.selfdrive.controls.lib.plan_align import PlanAlignBraking\n"),
  ("    self.output_should_stop = False\n",
   "    self.output_should_stop = False\n    self.plan_align = PlanAlignBraking()\n"),
  ("    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration\n",
   "    output_a_target_e2e = sm['modelV2'].action.desiredAcceleration\n"
   "    output_a_target_e2e = self.plan_align.update(sm['modelV2'], output_a_target_e2e, sm['radarState'].leadOne.present)\n"),
], "PlanAlignBraking")

# ----------------------------------------------------------------------------------------------------------------------
# 5. TICI / C3X settings UI  (same pattern as Blendful #2073 + #2081)
# ----------------------------------------------------------------------------------------------------------------------
patch(p("selfdrive", "ui", "sunnypilot", "layouts", "settings", "models.py"), [
  ('    self.blendful_toggle = toggle_item_sp(tr("Blendful (Alpha)"), self._blendful_desc, param="Blendful")\n',
   '    self.blendful_toggle = toggle_item_sp(tr("Blendful (Alpha)"), self._blendful_desc, param="Blendful")\n'
   '\n'
   f'    self._plan_align_desc = tr("{DESC_A}" +\n'
   f'                               "{DESC_B}" +\n'
   f'                               "{DESC_C}")\n'
   f'    self.plan_align_toggle = toggle_item_sp(tr("{TITLE}"), self._plan_align_desc, param="{PARAM}")\n'),
  ("                  self.blendful_toggle, self.lane_turn_desire_toggle, self.lane_turn_value_control, self.lagd_toggle, self.delay_control,\n"
   "                  self.camera_offset]\n",
   "                  self.blendful_toggle, self.plan_align_toggle, self.lane_turn_desire_toggle, self.lane_turn_value_control,\n"
   "                  self.lagd_toggle, self.delay_control, self.camera_offset]\n"),
  ("      self.blendful_toggle.show_description(not blendful_allowed)\n",
   "      self.blendful_toggle.show_description(not blendful_allowed)\n"
   "\n"
   "    plan_align_allowed = ui_state.active_runner_tinygrad\n"
   "    if plan_align_allowed:\n"
   f'      self.plan_align_toggle.action_item.set_state(ui_state.params.get_bool("{PARAM}"))\n'
   "      self.plan_align_toggle.action_item.set_enabled(True)\n"
   "    else:\n"
   "      self.plan_align_toggle.action_item.set_state(False)\n"
   "      self.plan_align_toggle.action_item.set_enabled(False)\n"
   "\n"
   "    plan_align_desc = self._plan_align_desc if plan_align_allowed else \\\n"
   "      f\"<b>{tr('Select a non-Default model to use Plan-Aligned Braking.')}</b><br><br>{self._plan_align_desc}\"\n"
   "    if self.plan_align_toggle.description != plan_align_desc:\n"
   "      self.plan_align_toggle.set_description(plan_align_desc)\n"
   "      self.plan_align_toggle.show_description(not plan_align_allowed)\n"),
], "plan_align_toggle")

# ----------------------------------------------------------------------------------------------------------------------
# 6. mici settings UI
# ----------------------------------------------------------------------------------------------------------------------
patch(p("selfdrive", "ui", "sunnypilot", "mici", "layouts", "models.py"), [
  ("    self.main_items = [self.current_model_info, self.select_model_btn, self.cancel_download_btn, self.refresh_btn, self.clear_cache_btn,\n"
   "                       self.blendful_toggle]\n",
   f'    self.plan_align_toggle = BigParamControl(tr("plan-aligned braking (alpha)"), "{PARAM}",\n'
   f'                                             description=tr("{DESC_A}" +\n'
   f'                                                            "{DESC_B}" +\n'
   f'                                                            "{DESC_C}"))\n'
   "\n"
   "    self.main_items = [self.current_model_info, self.select_model_btn, self.cancel_download_btn, self.refresh_btn, self.clear_cache_btn,\n"
   "                       self.blendful_toggle, self.plan_align_toggle]\n"),
  ("    self.blendful_toggle.refresh()\n",
   "    self.blendful_toggle.refresh()\n    self.plan_align_toggle.refresh()\n"),
  ("    if self.blendful_toggle.value != blendful_value:\n"
   "      self.blendful_toggle.set_value(blendful_value)\n",
   "    if self.blendful_toggle.value != blendful_value:\n"
   "      self.blendful_toggle.set_value(blendful_value)\n"
   "\n"
   "    plan_align_allowed = ui_state.active_runner_tinygrad\n"
   "    if plan_align_allowed:\n"
   f'      self.plan_align_toggle.set_checked(ui_state.params.get_bool("{PARAM}"))\n'
   "      self.plan_align_toggle.set_enabled(True)\n"
   "    else:\n"
   "      self.plan_align_toggle.set_checked(False)\n"
   "      self.plan_align_toggle.set_enabled(False)\n"
   '    plan_align_value = "" if plan_align_allowed else tr("custom model only")\n'
   "    if self.plan_align_toggle.value != plan_align_value:\n"
   "      self.plan_align_toggle.set_value(plan_align_value)\n"),
], "plan_align_toggle")

# ----------------------------------------------------------------------------------------------------------------------
# 7. sunnylink settings source (YAML) -> 8. regenerate settings_ui.json with the repo's compiler
# ----------------------------------------------------------------------------------------------------------------------
patch(p("sunnypilot", "sunnylink", "settings_ui_src", "pages", "models.yaml"), [
  ("  description: Lane desire, Blendful lane centering, and lead-vehicle awareness tuning\n",
   "  description: Lane desire, Blendful lane centering, plan-aligned braking, and lead-vehicle awareness tuning\n"),
  ("      - $ref: '#/macros/custom_model'\n  - key: LaneTurnDesire\n",
   "      - $ref: '#/macros/custom_model'\n"
   f"  - key: {PARAM}\n"
   "    widget: toggle\n"
   f"    title: {TITLE}\n"
   f"    description: {DESC}\n"
   "    enablement:\n"
   "      - $ref: '#/macros/custom_model'\n"
   "  - key: LaneTurnDesire\n"),
], f"key: {PARAM}")

compiler = p("sunnypilot", "sunnylink", "tools", "compile_settings_ui.py")
if CHECK_ONLY:
  r = subprocess.run([sys.executable, compiler, "--check"], capture_output=True, text=True)
  status.append(f"[json {'in sync' if r.returncode == 0 else 'OUT OF SYNC'}]   openpilot/sunnypilot/sunnylink/settings_ui.json")
else:
  r = subprocess.run([sys.executable, compiler], capture_output=True, text=True)
  if r.returncode != 0:
    sys.exit(f"settings_ui compile failed (is PyYAML installed?):\n{r.stdout}\n{r.stderr}")
  r = subprocess.run([sys.executable, compiler, "--check"], capture_output=True, text=True)
  if r.returncode != 0:
    sys.exit(f"settings_ui.json still differs from YAML after compile:\n{r.stdout}\n{r.stderr}")
  status.append("[regenerated]     openpilot/sunnypilot/sunnylink/settings_ui.json (verified in sync with YAML)")

# ----------------------------------------------------------------------------------------------------------------------
# syntax check every python file touched
# ----------------------------------------------------------------------------------------------------------------------
if not CHECK_ONLY:
  for f in [("selfdrive", "controls", "lib", "longitudinal_planner.py"),
            ("selfdrive", "ui", "sunnypilot", "layouts", "settings", "models.py"),
            ("selfdrive", "ui", "sunnypilot", "mici", "layouts", "models.py"),
            ("sunnypilot", "selfdrive", "controls", "lib", "plan_align.py"),
            ("sunnypilot", "selfdrive", "controls", "lib", "tests", "test_plan_align.py")]:
    py_compile.compile(p(*f), doraise=True)

print("\n".join(status))
if not CHECK_ONLY:
  print("\nDone. Next: rebuild (params_keys.h changed), then run the two pytest commands listed at the top of this script.")
