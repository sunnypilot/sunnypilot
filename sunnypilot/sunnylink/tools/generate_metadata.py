#!/usr/bin/env python3
"""
generate_metadata.py - Static AST analysis of sunnypilot UI code.

Extracts the complete panel/widget/rule hierarchy from the Python Raylib UI
and outputs an enhanced params_metadata.json (schema v2.0).

Usage:
    python sunnypilot/sunnylink/tools/generate_metadata.py

The script runs at build/CI time and never on-device.
It does NOT import any sunnypilot code - pure static analysis via ast module.
"""

import ast
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Configuration ────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[3]

# Panel layout files
SP_SETTINGS = REPO_ROOT / "selfdrive" / "ui" / "sunnypilot" / "layouts" / "settings" / "settings.py"

# Upstream (openpilot) panel files
OP_TOGGLES = REPO_ROOT / "selfdrive" / "ui" / "layouts" / "settings" / "toggles.py"
OP_DEVELOPER = REPO_ROOT / "selfdrive" / "ui" / "layouts" / "settings" / "developer.py"
OP_DEVICE = REPO_ROOT / "selfdrive" / "ui" / "layouts" / "settings" / "device.py"

# Sunnypilot panel files
SP_DIR = REPO_ROOT / "selfdrive" / "ui" / "sunnypilot" / "layouts" / "settings"

EXISTING_METADATA = REPO_ROOT / "sunnypilot" / "sunnylink" / "params_metadata.json"
OUTPUT_PATH = EXISTING_METADATA

# Widget factory function names
TOGGLE_FACTORIES = frozenset({"toggle_item_sp", "toggle_item"})
OPTION_FACTORIES = frozenset({"option_item_sp"})
MULTI_BTN_FACTORIES = frozenset({"multiple_button_item_sp", "multiple_button_item"})
NAV_BTN_FACTORIES = frozenset({"simple_button_item_sp"})
BUTTON_FACTORIES = frozenset({"button_item_sp", "button_item"})
DUAL_BTN_FACTORIES = frozenset({"dual_button_item_sp", "dual_button_item"})
TEXT_FACTORIES = frozenset({"text_item"})

ALL_FACTORIES = (
    TOGGLE_FACTORIES | OPTION_FACTORIES | MULTI_BTN_FACTORIES |
    NAV_BTN_FACTORIES | BUTTON_FACTORIES | DUAL_BTN_FACTORIES | TEXT_FACTORIES
)

# Known panel -> source file mappings
PANEL_FILES: dict[str, Path] = {
    "TogglesLayout": OP_TOGGLES,
    "FirehoseLayout": REPO_ROOT / "selfdrive" / "ui" / "layouts" / "settings" / "firehose.py",
    "DeviceLayoutSP": SP_DIR / "device.py",
    "SoftwareLayoutSP": SP_DIR / "software.py",
    "DeveloperLayoutSP": SP_DIR / "developer.py",
    "SteeringLayout": SP_DIR / "steering.py",
    "CruiseLayout": SP_DIR / "cruise.py",
    "VisualsLayout": SP_DIR / "visuals.py",
    "DisplayLayout": SP_DIR / "display.py",
    "SunnylinkLayout": SP_DIR / "sunnylink.py",
    "OSMLayout": SP_DIR / "osm.py",
    "ModelsLayout": SP_DIR / "models.py",
    "TripsLayout": SP_DIR / "trips.py",
    "VehicleLayout": SP_DIR / "vehicle" / "__init__.py",
    "NetworkUISP": SP_DIR / "network.py",
}

# Known sub-layout files (panel_stem -> {nav_id -> file})
SUB_LAYOUT_FILES: dict[str, dict[str, Path]] = {
    "steering": {
        "mads": SP_DIR / "steering_sub_layouts" / "mads_settings.py",
        "lane_change": SP_DIR / "steering_sub_layouts" / "lane_change_settings.py",
        "torque_control": SP_DIR / "steering_sub_layouts" / "torque_settings.py",
    },
    "cruise": {
        "sla": SP_DIR / "cruise_sub_layouts" / "speed_limit_settings.py",
    },
}

# Sub-sub-layout files
SUB_SUB_LAYOUT_FILES: dict[str, dict[str, Path]] = {
    "speed_limit_settings": {
        "policy": SP_DIR / "cruise_sub_layouts" / "speed_limit_policy.py",
    },
}


# ── AST Utility Functions ────────────────────────────────────────────────────

def _func_name(node: ast.Call) -> str:
    """Get the simple name of a function call."""
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _dotted(node: ast.expr) -> str:
    """Convert an AST node to a dotted string (e.g. 'self._foo.bar')."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    if isinstance(node, ast.Call):
        return _dotted(node.func)
    if isinstance(node, ast.Subscript):
        base = _dotted(node.value)
        if isinstance(node.slice, ast.Constant):
            return f'{base}["{node.slice.value}"]'
        return f"{base}[?]"
    return "?"


def _kwarg(call: ast.Call, name: str) -> ast.expr | None:
    """Get a keyword argument value from a Call node."""
    for kw in call.keywords:
        if kw.arg == name:
            return kw.value
    return None


def _pos(call: ast.Call, idx: int) -> ast.expr | None:
    """Get a positional argument from a Call node."""
    return call.args[idx] if idx < len(call.args) else None


def _str(node: ast.expr | None) -> str | None:
    """Extract a string literal, unwrapping tr()/tr_noop()/lambda: tr()."""
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.Call):
        fn = _func_name(node)
        if fn in ("tr", "tr_noop") and node.args:
            return _str(node.args[0])
    if isinstance(node, ast.Lambda):
        return _str(node.body)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _str(node.left), _str(node.right)
        if left is not None and right is not None:
            return left + right
    return None


def _num(node: ast.expr | None) -> int | float | None:
    """Extract a numeric literal."""
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        v = _num(node.operand)
        return -v if v is not None else None
    return None


def _bool(node: ast.expr | None) -> bool | None:
    """Extract a boolean literal."""
    if node is None:
        return None
    if isinstance(node, ast.Constant) and isinstance(node.value, bool):
        return node.value
    return None


def _dict_literal(node: ast.expr) -> dict[int, int | float] | None:
    """Extract a simple {int: number} dict literal."""
    if not isinstance(node, ast.Dict):
        return None
    result = {}
    for k, v in zip(node.keys, node.values):
        ki, vi = _num(k), _num(v)
        if ki is not None and vi is not None:
            result[int(ki)] = vi
    return result if result else None


def _button_labels(node: ast.expr) -> list[str]:
    """Extract button label strings from a list expression."""
    if not isinstance(node, ast.List):
        return []
    return [_str(e) or "?" for e in node.elts]


# ── Widget Definition ────────────────────────────────────────────────────────

class WidgetDef:
    """Extracted widget definition from a factory function call."""

    __slots__ = (
        "param", "widget_type", "title", "description", "icon",
        "needs_restart", "min_val", "max_val", "step", "value_map",
        "buttons", "inline", "use_float_scaling", "var_name", "nav_target",
        "_enabled_node",
    )

    def __init__(self):
        self.param: str | None = None
        self.widget_type: str = "unknown"
        self.title: str = ""
        self.description: str = ""
        self.icon: str = ""
        self.needs_restart: bool = False
        self.min_val: int | float | None = None
        self.max_val: int | float | None = None
        self.step: int | float | None = None
        self.value_map: dict | None = None
        self.buttons: list[str] = []
        self.inline: bool | None = None
        self.use_float_scaling: bool = False
        self.var_name: str = ""
        self.nav_target: str | None = None
        self._enabled_node: Any = None


def _extract_widget(call: ast.Call, var_name: str = "") -> WidgetDef | None:
    """Extract a WidgetDef from a factory function Call node."""
    fn = _func_name(call)
    if fn not in ALL_FACTORIES:
        return None

    w = WidgetDef()
    w.var_name = var_name

    # param keyword
    p = _kwarg(call, "param")
    if p:
        w.param = _str(p) or (_num(p) is not None and str(_num(p))) or None
        if isinstance(p, ast.Constant) and isinstance(p.value, str):
            w.param = p.value

    # Fallback: infer param from initial_state=self._params.get_bool("ParamName")
    if not w.param:
        init_state = _kwarg(call, "initial_state")
        if isinstance(init_state, ast.Call):
            init_fn = _dotted(init_state.func)
            if init_fn.endswith(".get_bool") and init_state.args:
                inferred = _str(init_state.args[0])
                if inferred:
                    w.param = inferred

    # Fallback: infer param from selected_index=self._params.get("ParamName", ...)
    if not w.param:
        sel_idx = _kwarg(call, "selected_index")
        if isinstance(sel_idx, ast.Call):
            sel_fn = _dotted(sel_idx.func)
            if sel_fn.endswith(".get") and sel_idx.args:
                inferred = _str(sel_idx.args[0])
                if inferred:
                    w.param = inferred

    # Widget type
    if fn in TOGGLE_FACTORIES:
        w.widget_type = "toggle"
    elif fn in OPTION_FACTORIES:
        w.widget_type = "option"
    elif fn in MULTI_BTN_FACTORIES:
        w.widget_type = "multiple_button"
    elif fn in NAV_BTN_FACTORIES:
        w.widget_type = "nav_button"
    elif fn in BUTTON_FACTORIES:
        w.widget_type = "button"
    elif fn in DUAL_BTN_FACTORIES:
        w.widget_type = "dual_button"
    elif fn in TEXT_FACTORIES:
        w.widget_type = "text"

    # Title
    title_node = _kwarg(call, "title") or _pos(call, 0)
    w.title = _str(title_node) or ""

    # Description
    desc_node = _kwarg(call, "description")
    if desc_node is None and fn in TOGGLE_FACTORIES:
        desc_node = _pos(call, 1)
    w.description = _str(desc_node) or ""

    # Icon
    icon_node = _kwarg(call, "icon")
    w.icon = _str(icon_node) or ""

    # Numeric range
    for kw_name, attr in [("min_value", "min_val"), ("max_value", "max_val"), ("value_change_step", "step")]:
        n = _kwarg(call, kw_name)
        if n is not None:
            setattr(w, attr, _num(n))

    # Value map
    vm = _kwarg(call, "value_map")
    if vm:
        w.value_map = _dict_literal(vm)

    # Buttons
    btn = _kwarg(call, "buttons")
    if btn:
        w.buttons = _button_labels(btn)

    # Inline
    il = _kwarg(call, "inline")
    if il is not None:
        w.inline = _bool(il)

    # Float scaling
    fs = _kwarg(call, "use_float_scaling")
    if fs is not None:
        w.use_float_scaling = _bool(fs) or False

    # Enabled kwarg (for inline enable rules like enabled=ui_state.is_offroad)
    enabled_node = _kwarg(call, "enabled")
    if enabled_node is not None:
        # Store for rule extraction during init phase
        w._enabled_node = enabled_node
    else:
        w._enabled_node = None

    # Nav button specifics
    if fn in NAV_BTN_FACTORIES:
        bt = _kwarg(call, "button_text")
        if bt:
            w.title = _str(bt) or ""
        cb = _kwarg(call, "callback")
        if cb:
            w.nav_target = _extract_nav_target(cb)

    # button_item_sp: use button_text as title fallback
    if fn in BUTTON_FACTORIES:
        bt = _kwarg(call, "button_text")
        if bt and not w.title:
            w.title = _str(bt) or ""

    return w


def _extract_nav_target(node: ast.expr) -> str | None:
    """Extract sub-panel target from lambda: self._set_current_panel(PanelType.X)."""
    if isinstance(node, ast.Lambda):
        node = node.body
    if isinstance(node, ast.Call):
        fn = _dotted(node.func)
        if "set_current_panel" in fn and node.args:
            target = _dotted(node.args[0])
            if "." in target:
                return target.split(".")[-1].lower()
    return None


# ── Rule Compiler ────────────────────────────────────────────────────────────

# Known enum value mappings (avoids importing sunnypilot code)
ENUM_MAP = {
    "car.CarParams.SteerControlType.angle": "angle",
    "car.CarParams.SteerControlType.torque": "torque",
    "SpeedLimitMode.off": 0,
    "SpeedLimitMode.information": 1,
    "SpeedLimitMode.warning": 2,
    "SpeedLimitMode.assist": 3,
    "SpeedLimitOffsetType.off": 0,
    "SpeedLimitOffsetType.fixed": 1,
    "SpeedLimitOffsetType.percentage": 2,
    "MadsSteeringModeOnBrake.DISENGAGE": 2,
    "AutoLaneChangeMode.NUDGE": 0,
    "OnroadBrightness.AUTO": 0,
    "OnroadBrightness.AUTO_DARK": 1,
    "OnroadBrightness.SCREEN_OFF": 2,
    "int(SpeedLimitMode.off)": 0,
    "int(SpeedLimitMode.information)": 1,
    "int(SpeedLimitMode.warning)": 2,
    "int(SpeedLimitMode.assist)": 3,
    "int(SpeedLimitOffsetType.off)": 0,
    "int(SpeedLimitOffsetType.fixed)": 1,
    "int(SpeedLimitOffsetType.percentage)": 2,
    "int(MadsSteeringModeOnBrake.DISENGAGE)": 2,
}


class RuleCompiler:
    """Converts Python AST condition expressions into portable JSON rules.

    The JSON rule language is:
        {"param": "X", "op": "truthy"|"eq"|"neq"|"gt"|"lt", "value": ...}
        {"state": "offroad"|"onroad"|"engaged"|"has_longitudinal_control"|...}
        {"car_param": "field"}          -- from CarParamsPersistent
        {"car_param_sp": "field"}       -- from CarParamsSPPersistent
        {"all": [rule, ...]}
        {"any": [rule, ...]}
        {"not": rule}
        {"raw": "...", "fallback": true} -- unresolvable, safe default
    """

    def __init__(self, var_to_param: dict[str, str]):
        self.v2p = var_to_param

    def compile(self, node: ast.expr) -> dict | None:
        """Compile a Python expression to a JSON rule. Returns None for always-true."""
        if node is None:
            return None

        # Boolean literal
        if isinstance(node, ast.Constant):
            if node.value is True:
                return None
            if node.value is False:
                return {"const": False}

        # not expr
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            inner = self.compile(node.operand)
            if inner is None:
                return {"const": False}
            return {"not": inner}

        # expr and expr
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            parts = [self.compile(v) for v in node.values]
            parts = [p for p in parts if p is not None]
            if not parts:
                return None
            return parts[0] if len(parts) == 1 else {"all": parts}

        # expr or expr
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            parts = [self.compile(v) for v in node.values]
            parts = [p for p in parts if p is not None]
            if not parts:
                return None
            return parts[0] if len(parts) == 1 else {"any": parts}

        # Function calls
        if isinstance(node, ast.Call):
            return self._call(node)

        # Attribute access
        if isinstance(node, ast.Attribute):
            return self._attr(node)

        # Comparisons
        if isinstance(node, ast.Compare):
            return self._compare(node)

        # Name reference
        if isinstance(node, ast.Name):
            return self._name(node)

        return self._raw(node)

    # ── Call patterns ────────────────────────────────────────────

    def _call(self, node: ast.Call) -> dict | None:
        fn = _dotted(node.func)

        # ui_state.is_offroad() / is_onroad()
        if fn == "ui_state.is_offroad":
            return {"state": "offroad"}
        if fn == "ui_state.is_onroad":
            return {"state": "onroad"}

        # Known method patterns
        if fn in ("self._mads_limited_settings",):
            return {"state": "mads_limited_settings"}

        # X.action_item.get_state()
        if fn.endswith(".action_item.get_state"):
            var = fn.rsplit(".action_item.get_state", 1)[0]
            param = self.v2p.get(var)
            if param:
                return {"param": param, "op": "truthy"}

        # X.action_item.get_selected_button() - treat as truthy of the param
        if fn.endswith(".action_item.get_selected_button"):
            var = fn.rsplit(".action_item.get_selected_button", 1)[0]
            param = self.v2p.get(var)
            if param:
                return {"param": param, "op": "truthy"}

        # params.get_bool("X") / params.get("X")
        if fn.endswith(".get_bool") and node.args:
            pname = _str(node.args[0])
            if pname:
                return {"param": pname, "op": "truthy"}

        if fn.endswith(".get") and not fn.endswith(".get_bool") and not fn.endswith(".get_state"):
            if node.args:
                pname = _str(node.args[0])
                if pname:
                    return {"param": pname, "op": "truthy"}

        # int(...) wrapper — unwrap
        if fn == "int" and node.args:
            return self.compile(node.args[0])

        return self._raw(node)

    # ── Attribute patterns ───────────────────────────────────────

    def _attr(self, node: ast.Attribute) -> dict | None:
        full = _dotted(node)

        # ui_state properties (both property access and method references)
        ui_state_map = {
            "ui_state.has_longitudinal_control": {"state": "has_longitudinal_control"},
            "ui_state.engaged": {"state": "engaged"},
            "ui_state.has_icbm": {"state": "has_icbm"},
            "ui_state.started": {"state": "onroad"},
            "ui_state.is_metric": {"param": "IsMetric", "op": "truthy"},
            "ui_state.is_sp_release": {"param": "IsReleaseSpBranch", "op": "truthy"},
            "ui_state.is_release": {"param": "IsReleaseBranch", "op": "truthy"},
            "ui_state.sunnylink_enabled": {"param": "SunnylinkEnabled", "op": "truthy"},
            # Method references (passed as callables without (), e.g. enabled=ui_state.is_offroad)
            "ui_state.is_offroad": {"state": "offroad"},
            "ui_state.is_onroad": {"state": "onroad"},
        }
        if full in ui_state_map:
            return ui_state_map[full]

        # CarParams fields (from CarParamsPersistent)
        if full.startswith("ui_state.CP."):
            field = full.split("ui_state.CP.", 1)[1]
            return {"car_param": field}

        # CarParamsSP fields (from CarParamsSPPersistent)
        if full.startswith("ui_state.CP_SP."):
            field = full.split("ui_state.CP_SP.", 1)[1]
            return {"car_param_sp": field}

        # self._is_release patterns and other common self._ attributes
        self_attr_map = {
            "self._is_release": {"param": "IsReleaseBranch", "op": "truthy"},
            "self._is_release_branch": {
                "any": [
                    {"param": "IsReleaseBranch", "op": "truthy"},
                    {"param": "IsReleaseSpBranch", "op": "truthy"},
                ]
            },
            "self._is_development_branch": {
                "any": [
                    {"param": "IsTestedBranch", "op": "truthy"},
                    {"param": "IsDevelopmentBranch", "op": "truthy"},
                ]
            },
            "self._sunnylink_enabled": {"param": "SunnylinkEnabled", "op": "truthy"},
        }
        if full in self_attr_map:
            return self_attr_map[full]

        # Variable → param mapping
        param = self.v2p.get(full)
        if param:
            return {"param": param, "op": "truthy"}

        # self._X_toggle.action_item.enabled (read the enabled state)
        if full.endswith(".action_item.enabled"):
            var = full.rsplit(".action_item.enabled", 1)[0]
            param = self.v2p.get(var)
            if param:
                return {"param": param, "op": "truthy"}

        return self._raw(node)

    # ── Comparison patterns ──────────────────────────────────────

    def _compare(self, node: ast.Compare) -> dict | None:
        if len(node.ops) != 1 or len(node.comparators) != 1:
            return self._raw(node)

        left, op, right = node.left, node.ops[0], node.comparators[0]
        left_s = _dotted(left)

        # X is not None / X is None
        if isinstance(op, (ast.Is, ast.IsNot)):
            if isinstance(right, ast.Constant) and right.value is None:
                if left_s == "ui_state.CP":
                    r = {"state": "car_params_available"}
                    return r if isinstance(op, ast.IsNot) else {"not": r}
                if left_s == "ui_state.CP_SP":
                    r = {"state": "car_params_sp_available"}
                    return r if isinstance(op, ast.IsNot) else {"not": r}

        # Equality / inequality
        if isinstance(op, (ast.Eq, ast.NotEq)):
            json_op = "eq" if isinstance(op, ast.Eq) else "neq"
            right_val = self._resolve_value(right)

            # Try to resolve left to a param
            left_rule = self.compile(left)
            if left_rule and "param" in left_rule and right_val is not None:
                return {"param": left_rule["param"], "op": json_op, "value": right_val}

            # CarParams field comparison
            if left_s.startswith("ui_state.CP."):
                field = left_s.split("ui_state.CP.", 1)[1]
                return {"car_param": field, "op": json_op, "value": right_val}
            if left_s.startswith("ui_state.CP_SP."):
                field = left_s.split("ui_state.CP_SP.", 1)[1]
                return {"car_param_sp": field, "op": json_op, "value": right_val}

        # Ordered comparisons
        if isinstance(op, (ast.Gt, ast.Lt, ast.GtE, ast.LtE)):
            op_str = {ast.Gt: "gt", ast.Lt: "lt", ast.GtE: "gte", ast.LtE: "lte"}[type(op)]
            right_val = self._resolve_value(right)
            left_rule = self.compile(left)
            if left_rule and "param" in left_rule and right_val is not None:
                return {"param": left_rule["param"], "op": op_str, "value": right_val}

        # In / NotIn: X in (val1, val2, ...) / X not in (val1, val2, ...)
        if isinstance(op, (ast.In, ast.NotIn)):
            if isinstance(right, ast.Tuple):
                values = [self._resolve_value(e) for e in right.elts]
                if all(v is not None for v in values):
                    left_rule = self.compile(left)
                    if left_rule and "param" in left_rule:
                        # X in (a, b) → {"any": [{"param": X, "op": "eq", "value": a}, ...]}
                        eq_rules = [{"param": left_rule["param"], "op": "eq", "value": v} for v in values]
                        in_rule = eq_rules[0] if len(eq_rules) == 1 else {"any": eq_rules}
                        if isinstance(op, ast.NotIn):
                            return {"not": in_rule}
                        return in_rule

        # Bitwise AND (flag checks): ui_state.CP_SP.flags & TeslaFlagsSP.HAS_VEHICLE_BUS
        if isinstance(op, (ast.BitAnd,)):
            return self._raw(node)

        return self._raw(node)

    # ── Name patterns ────────────────────────────────────────────

    def _name(self, node: ast.Name) -> dict | None:
        name = node.id
        # Common local variable patterns we can resolve
        known = {
            "show_advanced": {"param": "ShowAdvancedControls", "op": "truthy"},
            "disable_updates": {"param": "DisableUpdates", "op": "truthy"},
            "has_long": {"state": "has_longitudinal_control"},
            "has_icbm": {"state": "has_icbm"},
            "torque_allowed": {
                "all": [
                    {"state": "car_params_available"},
                    {"car_param": "steerControlType", "op": "neq", "value": "angle"},
                ]
            },
            "sla_available": {
                "any": [
                    {"state": "has_longitudinal_control"},
                    {"state": "has_icbm"},
                ]
            },
            "enable_bsm": {"car_param": "enableBsm"},
            "alpha_avail": {"car_param": "alphaLongitudinalAvailable"},
            "long_man_enabled": {
                "all": [
                    {"state": "has_longitudinal_control"},
                    {"state": "offroad"},
                ]
            },
            "enforce_torque_enabled": {"param": "EnforceTorqueControl", "op": "truthy"},
            "nnlc_enabled": {"param": "NeuralNetworkLateralControl", "op": "truthy"},
            "custom_tune_enabled": {"param": "CustomTorqueParams", "op": "truthy"},
            "sliders_enabled": {
                "any": [
                    {"param": "TorqueParamsOverrideEnabled", "op": "truthy"},
                    {"state": "offroad"},
                ]
            },
            "brightness_val": {"param": "OnroadScreenOffBrightness", "op": "truthy"},
            "offset_type": {"param": "SpeedLimitOffsetType", "op": "truthy"},
        }
        if name in known:
            return known[name]

        param = self.v2p.get(name)
        if param:
            return {"param": param, "op": "truthy"}

        return self._raw(node)

    # ── Helpers ──────────────────────────────────────────────────

    def _resolve_value(self, node: ast.expr) -> Any:
        """Resolve a value node to a Python literal."""
        v = _num(node)
        if v is not None:
            return v
        s = _str(node)
        if s is not None:
            return s
        b = _bool(node)
        if b is not None:
            return b
        # Try enum map
        dotted = _dotted(node)
        if dotted in ENUM_MAP:
            return ENUM_MAP[dotted]
        # int(EnumValue) pattern
        if isinstance(node, ast.Call) and _func_name(node) == "int" and node.args:
            inner_dotted = _dotted(node.args[0])
            key = f"int({inner_dotted})"
            if key in ENUM_MAP:
                return ENUM_MAP[key]
            inner_val = self._resolve_value(node.args[0])
            if inner_val is not None:
                return inner_val
        return None

    @staticmethod
    def _raw(node: ast.expr) -> dict:
        try:
            raw_str = ast.unparse(node)
        except Exception:
            raw_str = "?"
        return {"raw": raw_str, "fallback": True}


# ── Panel Extractor ──────────────────────────────────────────────────────────

class PanelExtractor:
    """Extracts widgets, variable→param mappings, item order, and rules
    from a single Python source file containing a panel Layout class."""

    def __init__(self, source_path: Path):
        self.path = source_path
        self.widgets: list[WidgetDef] = []
        self.v2p: dict[str, str] = {}          # "self._foo" → "ParamKey"
        self.item_order: list[str | dict] = []  # ["ParamKey", {"separator": True}, ...]
        self.rules: dict[str, dict] = {}        # "ParamKey" → {"visible": rule, "enabled": rule}
        self.sub_panel_nav: dict[str, str] = {} # nav_id → label
        self._toggle_defs: dict[str, dict] = {} # for upstream toggles.py dict pattern
        self._descriptions: dict[str, str] = {} # module-level DESCRIPTIONS dict

    def parse(self):
        if not self.path.exists():
            print(f"  [WARN] File not found: {self.path}", file=sys.stderr)
            return
        source = self.path.read_text()
        tree = ast.parse(source, filename=str(self.path))

        # First pass: extract module-level DESCRIPTIONS dict
        self._extract_descriptions(tree)

        # Second pass: extract widgets and ordering from init/initialize methods
        self._walk_methods(tree, target_methods={"_initialize_items", "__init__"}, phase="init")

        # Build v2p from widgets
        for w in self.widgets:
            if w.param and w.var_name:
                self.v2p[w.var_name] = w.param

        # Extract enabled= kwarg rules from widgets (must happen after v2p is built)
        self._extract_enabled_kwarg_rules()

        # Also parse for-loop key→item mappings in _update methods
        self._walk_methods(tree, target_methods={
            "_update_state", "_update_toggles", "show_event",
        }, phase="rules")

        # Walk callback methods (_on_*, _handle_*) with parameter→param resolution
        self._walk_all_methods_for_rules(tree)

    def _walk_all_methods_for_rules(self, tree: ast.Module):
        """Walk all class methods to find set_visible/set_enabled calls not in primary methods.

        This catches rules from callback methods like _on_custom_acc_toggle().
        """
        primary_methods = {"_update_state", "_update_toggles", "show_event",
                           "_initialize_items", "__init__"}

        # Build callback→param mapping: "self._on_foo" → param from the widget that registered it
        callback_param_map = self._build_callback_param_map(tree)

        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef):
                continue
            for item in cls_node.body:
                if isinstance(item, ast.FunctionDef) and item.name not in primary_methods:
                    if item.name.startswith("_on_") or item.name.startswith("_handle_"):
                        # If this method has a "state" param and we know which widget's callback it is,
                        # temporarily add "state" → param to v2p
                        method_key = f"self.{item.name}"
                        if method_key in callback_param_map and len(item.args.args) >= 2:
                            state_param_name = item.args.args[1].arg  # first arg after self
                            self.v2p[state_param_name] = callback_param_map[method_key]
                            self._extract_rules(item)
                            del self.v2p[state_param_name]
                        else:
                            self._extract_rules(item)

    def _build_callback_param_map(self, tree: ast.Module) -> dict[str, str]:
        """Build mapping from callback method references to the param of the widget that uses them.

        E.g. "self._on_custom_acc_toggle" → "CustomAccIncrementsEnabled"
        """
        result = {}
        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef):
                continue
            for item in cls_node.body:
                if isinstance(item, ast.FunctionDef) and item.name in ("__init__", "_initialize_items"):
                    for node in ast.walk(item):
                        if isinstance(node, ast.Call) and _func_name(node) in ALL_FACTORIES:
                            cb = _kwarg(node, "callback")
                            p = _kwarg(node, "param")
                            if cb and p:
                                cb_name = _dotted(cb)
                                param = _str(p)
                                if cb_name and param:
                                    result[cb_name] = param
        return result

    def _extract_enabled_kwarg_rules(self):
        """Extract enabled= kwarg from widget factory calls as rules.

        Handles patterns like:
          toggle_item(..., enabled=ui_state.is_offroad)
          toggle_item(..., enabled=lambda: not ui_state.engaged)
        """
        compiler = RuleCompiler(self.v2p)
        for w in self.widgets:
            if w.param and w._enabled_node is not None:
                node = w._enabled_node
                # Unwrap lambda
                if isinstance(node, ast.Lambda):
                    node = node.body
                rule = compiler.compile(node)
                if rule:
                    self._set_rule(w.param, "enabled", rule)

    def _extract_descriptions(self, tree: ast.Module):
        """Extract module-level DESCRIPTIONS = {...} dict."""
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                if isinstance(node.targets[0], ast.Name) and node.targets[0].id == "DESCRIPTIONS":
                    if isinstance(node.value, ast.Dict):
                        for k, v in zip(node.value.keys, node.value.values):
                            key = _str(k)
                            val = _str(v)
                            if key and val:
                                self._descriptions[key] = val

    def _walk_methods(self, tree: ast.Module, target_methods: set[str], phase: str):
        """Walk all class methods matching target_methods."""
        for cls_node in ast.walk(tree):
            if not isinstance(cls_node, ast.ClassDef):
                continue
            for item in cls_node.body:
                if isinstance(item, ast.FunctionDef) and item.name in target_methods:
                    if phase == "init":
                        self._extract_init(item)
                    elif phase == "rules":
                        self._extract_rules(item)

    # ── Init phase: widget definitions & ordering ────────────────

    def _extract_init(self, func: ast.FunctionDef):
        for node in ast.walk(func):
            # Assignment: self._X = factory_call(...)
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                target = node.targets[0]
                value = node.value

                if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name):
                    if target.value.id == "self":
                        var = f"self.{target.attr}"

                        # Widget factory call
                        if isinstance(value, ast.Call):
                            w = _extract_widget(value, var)
                            if w:
                                self.widgets.append(w)
                                if w.param:
                                    self.v2p[var] = w.param

                        # _toggle_defs dict (upstream toggles.py pattern)
                        if target.attr == "_toggle_defs" and isinstance(value, ast.Dict):
                            self._parse_toggle_defs(value)

                # self._toggles["Key"] = self._some_widget (e.g. LongitudinalPersonality insertion)
                if (isinstance(target, ast.Subscript) and isinstance(target.value, ast.Attribute)
                        and isinstance(target.value.value, ast.Name) and target.value.value.id == "self"
                        and target.value.attr == "_toggles"):
                    key = _str(target.slice)
                    if key:
                        sub_var = f'self._toggles["{key}"]'
                        # Check if value references a self attribute with an existing widget
                        src_var = _dotted(value)
                        src_param = self.v2p.get(src_var)
                        if src_param:
                            self.v2p[sub_var] = src_param
                        elif key not in {w.param for w in self.widgets if w.param}:
                            # Inherit param from the key name (same key as param)
                            self.v2p[sub_var] = key

                # items = [...] or self.items = [...]
                # Also handle: items = list(self._toggles.values()) + [...]
                is_items_target = False
                if isinstance(target, ast.Name) and target.id == "items":
                    is_items_target = True
                elif (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                      and target.value.id == "self" and target.attr == "items"):
                    is_items_target = True

                if is_items_target:
                    if isinstance(value, ast.List):
                        self._extract_item_order(value)
                    elif isinstance(value, ast.BinOp) and isinstance(value.op, ast.Add):
                        # list(self._toggles.values()) + [...more_items...]
                        self._extract_binop_items(value)

                # self._scroller = Scroller([...], ...) or Scroller(list(self._toggles.values()), ...)
                if (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                        and target.value.id == "self" and target.attr == "_scroller"
                        and isinstance(value, ast.Call) and _func_name(value) == "Scroller"):
                    if value.args:
                        scroller_arg = value.args[0]
                        if isinstance(scroller_arg, ast.List) and not self.item_order:
                            self._extract_item_order(scroller_arg)
                        elif isinstance(scroller_arg, ast.Call):
                            # list(self._toggles.values()) → emit all toggle_defs params
                            fn = _dotted(scroller_arg.func)
                            if "list" in fn and not self.item_order:
                                for w in self.widgets:
                                    if w.param:
                                        self.item_order.append(w.param)

    def _parse_toggle_defs(self, dict_node: ast.Dict):
        """Parse _toggle_defs = {"ParamKey": (title, desc, icon, restart), ...}.

        Supports two formats:
        - 4-tuple (upstream toggles.py): (title, desc, icon, needs_restart)
        - 3-tuple (SP visuals.py):       (title, desc, callback)
        """
        for key, val in zip(dict_node.keys, dict_node.values):
            param = _str(key)
            if not param:
                continue
            if not isinstance(val, ast.Tuple) or len(val.elts) < 3:
                continue

            title = _str(val.elts[0]) or ""
            desc_node = val.elts[1]
            # Description may be a DESCRIPTIONS["X"] reference
            desc = _str(desc_node) or ""
            if not desc:
                # Try to resolve from DESCRIPTIONS dict
                if isinstance(desc_node, ast.Subscript):
                    desc_key = _str(desc_node.slice)
                    if desc_key and desc_key in self._descriptions:
                        desc = self._descriptions[desc_key]

            icon = ""
            needs_restart = False

            if len(val.elts) >= 4:
                # 4-tuple: (title, desc, icon, needs_restart)
                icon = _str(val.elts[2]) or ""
                needs_restart = _bool(val.elts[3]) or False

            w = WidgetDef()
            w.param = param
            w.widget_type = "toggle"
            w.title = title
            w.description = desc
            w.icon = icon
            w.needs_restart = needs_restart
            w.var_name = f'self._toggles["{param}"]'
            self.widgets.append(w)
            self.v2p[w.var_name] = param

    def _extract_item_order(self, list_node: ast.List):
        """Extract display order from items = [...] list."""
        # Only set order if not already populated (first wins)
        if self.item_order:
            return

        for elt in list_node.elts:
            # self._some_widget
            if isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name) and elt.value.id == "self":
                var = f"self.{elt.attr}"
                param = self.v2p.get(var)
                if param:
                    self.item_order.append(param)
                else:
                    # Check widgets for nav buttons
                    matched = False
                    for w in self.widgets:
                        if w.var_name == var:
                            if w.widget_type == "nav_button" and w.nav_target:
                                self.item_order.append({"sub_panel": w.nav_target})
                                self.sub_panel_nav[w.nav_target] = w.title
                            elif w.widget_type in ("button", "dual_button", "text"):
                                # Non-param action items — skip in schema
                                pass
                            matched = True
                            break
                    if not matched:
                        # Could be a non-widget item (e.g. text_item inline)
                        pass

            # Factory call inline: toggle_item_sp(...), LineSeparatorSP(...)
            elif isinstance(elt, ast.Call):
                fn = _func_name(elt)
                if fn in ("LineSeparatorSP", "LineSeparator"):
                    self.item_order.append({"separator": True})
                elif fn == "Spacer":
                    pass  # skip spacers
                else:
                    w = _extract_widget(elt)
                    if w:
                        if w.param:
                            self.widgets.append(w)
                            self.item_order.append(w.param)
                        elif w.widget_type == "nav_button" and w.nav_target:
                            self.item_order.append({"sub_panel": w.nav_target})
                            self.sub_panel_nav[w.nav_target] = w.title

    def _extract_binop_items(self, node: ast.BinOp):
        """Handle items = list(self._toggles.values()) + [...] pattern.

        The left side (list(self._toggles.values())) means "all toggle_defs params in order".
        The right side is a regular list of additional items.
        """
        if self.item_order:
            return

        # Left side: list(self._toggles.values()) → emit all _toggle_defs params in order
        if isinstance(node.left, ast.Call):
            fn = _dotted(node.left.func)
            if "list" in fn or "_toggles" in fn:
                # Use the toggle_defs order (already added as widgets with param keys)
                for w in self.widgets:
                    if w.var_name.startswith('self._toggles["') and w.param:
                        self.item_order.append(w.param)

        # Right side: [...] additional items
        if isinstance(node.right, ast.List):
            self._extract_item_order_from_elts(node.right.elts)

    def _extract_item_order_from_elts(self, elts: list[ast.expr]):
        """Extract item order from a list of AST elements."""
        for elt in elts:
            if isinstance(elt, ast.Attribute) and isinstance(elt.value, ast.Name) and elt.value.id == "self":
                var = f"self.{elt.attr}"
                param = self.v2p.get(var)
                if param:
                    self.item_order.append(param)
                else:
                    for w in self.widgets:
                        if w.var_name == var:
                            if w.widget_type == "nav_button" and w.nav_target:
                                self.item_order.append({"sub_panel": w.nav_target})
                                self.sub_panel_nav[w.nav_target] = w.title
                            break
            elif isinstance(elt, ast.Call):
                fn = _func_name(elt)
                if fn in ("LineSeparatorSP", "LineSeparator"):
                    self.item_order.append({"separator": True})
                else:
                    w = _extract_widget(elt)
                    if w and w.param:
                        self.widgets.append(w)
                        self.item_order.append(w.param)

    # ── Rules phase: visibility and enable conditions ────────────

    def _extract_rules(self, func: ast.FunctionDef):
        """Extract visibility/enable rules from _update_state or _update_toggles."""
        # First, pick up any for-loop key→item mappings to enrich v2p
        self._extract_key_item_tuples(func)

        compiler = RuleCompiler(self.v2p)

        # Pre-pass: extract rules from if/else patterns where one branch sets True and the other False
        self._extract_if_else_rules(func.body, compiler, condition=None)

        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue

            func_attr = node.func if isinstance(node.func, ast.Attribute) else None
            if func_attr is None:
                continue

            # X.set_visible(expr)
            if func_attr.attr == "set_visible" and node.args:
                target = _dotted(func_attr.value)
                param = self.v2p.get(target)
                if param:
                    rule = compiler.compile(node.args[0])
                    if rule:
                        self._set_rule(param, "visible", rule)

            # X.action_item.set_enabled(expr)
            if func_attr.attr == "set_enabled" and node.args:
                if isinstance(func_attr.value, ast.Attribute) and func_attr.value.attr == "action_item":
                    target = _dotted(func_attr.value.value)
                    param = self.v2p.get(target)
                    if param:
                        rule = compiler.compile(node.args[0])
                        if rule:
                            self._set_rule(param, "enabled", rule)

        # Also handle for-loop batch rules
        self._extract_for_loop_rules(func, compiler)

    def _extract_if_else_rules(self, stmts: list[ast.stmt], compiler: RuleCompiler, condition: dict | None):
        """Structured walk of if/else blocks to extract rules from conditional patterns.

        Handles:
            if cond:
                X.action_item.set_enabled(True)
            else:
                X.action_item.set_enabled(False)

        The rule for X.enabled = cond (combined with outer condition if nested).
        """
        for stmt in stmts:
            if not isinstance(stmt, ast.If):
                continue

            if_cond = compiler.compile(stmt.test)

            # Scan both branches for set_enabled(True/False) and set_visible(True/False) pairs
            if_setters = self._find_setter_calls(stmt.body)
            else_setters = self._find_setter_calls(stmt.orelse) if stmt.orelse else {}

            for target_key, (setter_type, if_arg) in if_setters.items():
                if_val = _bool(if_arg)
                param = self.v2p.get(target_key)
                if not param:
                    continue

                if target_key in else_setters:
                    else_type, else_arg = else_setters[target_key]
                    else_val = _bool(else_arg)

                    if if_val is True and else_val is False and if_cond is not None:
                        # if cond: set_X(True) / else: set_X(False) → rule = cond
                        full_rule = if_cond
                        if condition is not None:
                            full_rule = {"all": [condition, if_cond]}
                        self._set_rule(param, setter_type, full_rule)
                    elif if_val is False and else_val is True and if_cond is not None:
                        # if cond: set_X(False) / else: set_X(True) → rule = not(cond)
                        full_rule = {"not": if_cond}
                        if condition is not None:
                            full_rule = {"all": [condition, {"not": if_cond}]}
                        self._set_rule(param, setter_type, full_rule)

            # Recurse into nested if blocks
            combined = if_cond
            if condition is not None and if_cond is not None:
                combined = {"all": [condition, if_cond]}
            elif condition is not None:
                combined = condition
            self._extract_if_else_rules(stmt.body, compiler, combined)

            if stmt.orelse:
                neg_cond = {"not": if_cond} if if_cond is not None else None
                neg_combined = neg_cond
                if condition is not None and neg_cond is not None:
                    neg_combined = {"all": [condition, neg_cond]}
                elif condition is not None:
                    neg_combined = condition
                self._extract_if_else_rules(stmt.orelse, compiler, neg_combined)

    @staticmethod
    def _find_setter_calls(stmts: list[ast.stmt]) -> dict[str, tuple[str, ast.expr]]:
        """Find set_enabled(X) and set_visible(X) calls in a statement list (non-recursive into nested ifs).

        Returns {target_var: ("enabled"|"visible", arg_node)}.
        Only scans the top level (Expr statements), not nested.
        """
        result = {}
        for stmt in stmts:
            if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
                continue
            call = stmt.value
            if not isinstance(call.func, ast.Attribute) or not call.args:
                continue

            attr = call.func.attr
            if attr == "set_enabled" and isinstance(call.func.value, ast.Attribute):
                if call.func.value.attr == "action_item":
                    target = _dotted(call.func.value.value)
                    result[target] = ("enabled", call.args[0])
            elif attr == "set_visible":
                target = _dotted(call.func.value)
                result[target] = ("visible", call.args[0])

        return result

    def _set_rule(self, param: str, rule_type: str, rule: dict):
        """Set a rule, preferring non-const rules over const:false.

        When ast.walk visits both if/else branches, it may see:
          if cond: X.set_enabled(complex_expr)   # good rule
          else:    X.set_enabled(False)           # const:false

        We keep the more specific (non-const) rule.
        """
        existing = self.rules.get(param, {}).get(rule_type)
        if existing is not None:
            # If existing is a real rule and new one is just const:false, keep existing
            is_new_const = isinstance(rule, dict) and rule.get("const") is False and len(rule) == 1
            is_existing_const = isinstance(existing, dict) and existing.get("const") is False and len(existing) == 1
            if is_new_const and not is_existing_const:
                return  # keep the better existing rule
        self.rules.setdefault(param, {})[rule_type] = rule

    def _extract_key_item_tuples(self, func: ast.FunctionDef):
        """Extract variable→param from for key, item in (("Key", self._item), ...)."""
        for node in ast.walk(func):
            if not isinstance(node, ast.For):
                continue
            if not isinstance(node.target, ast.Tuple) or not isinstance(node.iter, ast.Tuple):
                continue
            if len(node.target.elts) != 2:
                continue
            for elt in node.iter.elts:
                if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                    key = _str(elt.elts[0])
                    var = _dotted(elt.elts[1])
                    if key and var:
                        self.v2p[var] = key

    def _extract_for_loop_rules(self, func: ast.FunctionDef, compiler: RuleCompiler):
        """Extract rules from for item in (self._X, self._Y, ...): item.set_visible(expr)."""
        for node in ast.walk(func):
            if not isinstance(node, ast.For):
                continue
            if not isinstance(node.iter, ast.Tuple):
                continue
            if not isinstance(node.target, ast.Name):
                continue

            loop_var = node.target.id
            items_in_loop = [_dotted(e) for e in node.iter.elts]

            for stmt in ast.walk(node):
                if not isinstance(stmt, ast.Call) or not isinstance(stmt.func, ast.Attribute):
                    continue

                # item.set_visible(expr)
                if (stmt.func.attr == "set_visible" and isinstance(stmt.func.value, ast.Name)
                        and stmt.func.value.id == loop_var and stmt.args):
                    rule = compiler.compile(stmt.args[0])
                    if rule:
                        for var in items_in_loop:
                            param = self.v2p.get(var)
                            if param:
                                self._set_rule(param, "visible", rule)

                # item.action_item.set_enabled(expr)
                if (stmt.func.attr == "set_enabled" and isinstance(stmt.func.value, ast.Attribute)
                        and stmt.func.value.attr == "action_item"
                        and isinstance(stmt.func.value.value, ast.Name)
                        and stmt.func.value.value.id == loop_var and stmt.args):
                    rule = compiler.compile(stmt.args[0])
                    if rule:
                        for var in items_in_loop:
                            param = self.v2p.get(var)
                            if param:
                                self._set_rule(param, "enabled", rule)


# ── Hierarchy Builder ────────────────────────────────────────────────────────

def _extract_panels_from_settings() -> list[dict]:
    """Parse SP settings.py to extract panel definitions in order."""
    source = SP_SETTINGS.read_text()
    tree = ast.parse(source, filename=str(SP_SETTINGS))

    panels = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not (isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name)
                and target.value.id == "self" and target.attr == "_panels"):
            continue
        if not isinstance(node.value, ast.Dict):
            continue

        for i, (key, val) in enumerate(zip(node.value.keys, node.value.values)):
            panel_type_s = _dotted(key)
            panel_id = panel_type_s.split(".")[-1].lower() if "." in panel_type_s else panel_type_s.lower()

            if not isinstance(val, ast.Call) or len(val.args) < 2:
                continue

            name = _str(val.args[0]) or panel_id
            layout_call = val.args[1]
            layout_class = _func_name(layout_call) if isinstance(layout_call, ast.Call) else ""
            icon_node = _kwarg(val, "icon")
            icon = _str(icon_node) or ""

            panels.append({
                "id": panel_id,
                "name": name,
                "icon": icon,
                "order": i,
                "source_class": layout_class,
            })

    return panels


def _build_panel(panel_meta: dict) -> dict:
    """Build a complete panel with items, rules, and sub-panels."""
    layout_class = panel_meta.get("source_class", "")
    source_file = PANEL_FILES.get(layout_class)

    panel = {
        "id": panel_meta["id"],
        "name": panel_meta["name"],
        "icon": panel_meta["icon"],
        "order": panel_meta["order"],
        "source_class": layout_class,
    }

    if not source_file or not source_file.exists():
        panel["items"] = []
        return panel

    # Parse main panel file
    ext = PanelExtractor(source_file)
    ext.parse()

    # For panels that inherit from upstream, also parse the parent
    parent_file = _get_parent_file(layout_class)
    parent_ext = None
    if parent_file and parent_file.exists():
        parent_ext = PanelExtractor(parent_file)
        parent_ext.parse()

    # Build items list (parent items first, then child items for inheritance panels)
    if parent_ext:
        parent_items = _build_items(parent_ext)
        child_items = _build_items(ext)
        items = parent_items + child_items
    else:
        items = _build_items(ext)
    panel["items"] = items

    # Build sub-panels
    panel_stem = panel_meta["id"]
    sub_defs = SUB_LAYOUT_FILES.get(panel_stem, {})
    sub_panels = []

    for nav_id, nav_label in ext.sub_panel_nav.items():
        sub_file = sub_defs.get(nav_id)
        if sub_file and sub_file.exists():
            sub_ext = PanelExtractor(sub_file)
            sub_ext.parse()

            sub_items = _build_items(sub_ext)
            sub_panel = {"id": nav_id, "name": nav_label, "items": sub_items}

            # Check for sub-sub-panels
            sub_stem = sub_file.stem
            sub_sub_defs = SUB_SUB_LAYOUT_FILES.get(sub_stem, {})
            nested = []
            for snav_id, snav_label in sub_ext.sub_panel_nav.items():
                ss_file = sub_sub_defs.get(snav_id)
                if ss_file and ss_file.exists():
                    ss_ext = PanelExtractor(ss_file)
                    ss_ext.parse()
                    nested.append({
                        "id": snav_id,
                        "name": snav_label,
                        "items": _build_items(ss_ext),
                    })
                    # Merge widgets/rules up
                    ext.widgets.extend(ss_ext.widgets)
                    ext.rules.update(ss_ext.rules)
            if nested:
                sub_panel["sub_panels"] = nested

            sub_panels.append(sub_panel)

            # Merge widgets/rules from sub-panels into main extractor
            ext.widgets.extend(sub_ext.widgets)
            ext.rules.update(sub_ext.rules)

    if sub_panels:
        panel["sub_panels"] = sub_panels

    # Store extractors for later widget/rule collection
    panel["_ext"] = ext
    if parent_ext:
        panel["_parent_ext"] = parent_ext

    return panel


def _get_parent_file(layout_class: str) -> Path | None:
    """Get the parent class file for known inheritance chains."""
    parents = {
        "DeveloperLayoutSP": OP_DEVELOPER,
        "DeviceLayoutSP": OP_DEVICE,
    }
    return parents.get(layout_class)


def _build_items(ext: PanelExtractor) -> list:
    """Build the serializable items list from an extractor."""
    if ext.item_order:
        return list(ext.item_order)

    # Fallback: use widget order
    items = []
    for w in ext.widgets:
        if w.param:
            items.append(w.param)
        elif w.widget_type == "nav_button" and w.nav_target:
            items.append({"sub_panel": w.nav_target})
    return items


# ── Main: Generate Metadata ──────────────────────────────────────────────────

def generate_metadata():
    print("generate_metadata.py: Starting static analysis...")

    # 1. Load existing metadata
    existing: dict[str, Any] = {}
    if EXISTING_METADATA.exists():
        with open(EXISTING_METADATA) as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                pass
    # Handle both v1.0 (flat) and v2.0 (nested) existing formats
    if "params" in existing:
        # v2.0 format: extract params section as the flat map
        existing = existing.get("params", {})
    else:
        # v1.0 format: remove meta keys, rest is flat param entries
        for mk in ("$schema_version", "$generated_at", "$git_commit", "$git_remote", "$schema_md5"):
            existing.pop(mk, None)
        # Remove any non-dict entries (panels list etc. from partial v2.0)
        existing = {k: v for k, v in existing.items() if isinstance(v, dict)}

    print(f"  Loaded {len(existing)} existing param entries")

    # 2. Extract panel hierarchy
    panel_metas = _extract_panels_from_settings()
    print(f"  Discovered {len(panel_metas)} panels from settings.py")

    panels = []
    all_widgets: dict[str, WidgetDef] = {}
    all_rules: dict[str, dict] = {}

    for pm in panel_metas:
        panel = _build_panel(pm)

        # Collect widgets and rules
        ext: PanelExtractor | None = panel.pop("_ext", None)
        parent_ext: PanelExtractor | None = panel.pop("_parent_ext", None)

        if parent_ext:
            for w in parent_ext.widgets:
                if w.param and w.param not in all_widgets:
                    all_widgets[w.param] = w
            for p, r in parent_ext.rules.items():
                all_rules.setdefault(p, {}).update(r)

        if ext:
            for w in ext.widgets:
                if w.param and w.param not in all_widgets:
                    all_widgets[w.param] = w
            for p, r in ext.rules.items():
                all_rules.setdefault(p, {}).update(r)

        panels.append(panel)

    print(f"  Extracted {len(all_widgets)} widget definitions")
    print(f"  Extracted rules for {len(all_rules)} params")

    # 3. Build params section by merging existing + extracted
    params_section: dict[str, dict] = {}

    for param_key in sorted(set(list(existing.keys()) + list(all_widgets.keys()))):
        entry: dict[str, Any] = {}

        # Start with existing metadata (title, description, options, min/max/step, unit)
        if param_key in existing:
            entry.update(existing[param_key])

        # Overlay extracted widget info
        if param_key in all_widgets:
            w = all_widgets[param_key]
            entry["widget"] = w.widget_type
            if w.title:
                entry["title"] = w.title
            if w.description:
                entry["description"] = w.description
            if w.icon:
                entry["icon"] = w.icon
            if w.needs_restart:
                entry["needs_restart"] = True
            if w.min_val is not None:
                entry["min"] = w.min_val
            if w.max_val is not None:
                entry["max"] = w.max_val
            if w.step is not None:
                entry["step"] = w.step
            if w.value_map:
                entry["value_map"] = {str(k): v for k, v in w.value_map.items()}
            if w.buttons:
                # Only override options if not already present from existing metadata
                if "options" not in entry:
                    entry["options"] = [{"value": i, "label": lbl} for i, lbl in enumerate(w.buttons)]
            if w.inline is not None:
                entry["inline"] = w.inline
            if w.use_float_scaling:
                entry["use_float_scaling"] = True

        # Overlay rules
        if param_key in all_rules:
            entry["rules"] = all_rules[param_key]

        # Ensure title exists
        if "title" not in entry:
            entry["title"] = param_key
        if "description" not in entry:
            entry["description"] = ""

        params_section[param_key] = entry

    # 4. Git metadata
    git_commit = _git("rev-parse", "HEAD")
    git_remote = _git("remote", "get-url", "origin")

    # 5. Compute schema content hash (for WebSocket cache validation)
    # Hash is computed over the panels + params content only
    hash_content = json.dumps({"panels": panels, "params": params_section}, sort_keys=True)
    schema_md5 = hashlib.md5(hash_content.encode()).hexdigest()

    # 6. Assemble output
    output = {
        "$schema_version": "2.0",
        "$generated_at": datetime.now(timezone.utc).isoformat(),
        "$git_commit": git_commit,
        "$git_remote": git_remote,
        "$schema_md5": schema_md5,
        "panels": panels,
        "params": params_section,
    }

    # 7. Write
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")

    # 8. Summary
    total = len(params_section)
    with_widget = sum(1 for p in params_section.values() if "widget" in p)
    with_rules = sum(1 for p in params_section.values() if "rules" in p)
    raw_count = 0
    for p in params_section.values():
        for r in p.get("rules", {}).values():
            if isinstance(r, dict) and r.get("fallback"):
                raw_count += 1

    print(f"\nOutput: {OUTPUT_PATH}")
    print(f"  Schema MD5:        {schema_md5}")
    print(f"  Panels:            {len(panels)}")
    print(f"  Total params:      {total}")
    print(f"  With widget info:  {with_widget} ({with_widget * 100 // max(total, 1)}%)")
    print(f"  With rules:        {with_rules}")
    print(f"  Raw/fallback rules: {raw_count}")

    if raw_count > 0:
        print("\n  Unresolved rules:")
        for pk, pv in params_section.items():
            for rule_type, rule in pv.get("rules", {}).items():
                if isinstance(rule, dict) and rule.get("fallback"):
                    print(f"    {pk}.{rule_type}: {rule.get('raw', '?')}")

    return output


def _git(*args: str) -> str:
    try:
        return subprocess.check_output(
            ["git"] + list(args), cwd=str(REPO_ROOT), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


if __name__ == "__main__":
    generate_metadata()
