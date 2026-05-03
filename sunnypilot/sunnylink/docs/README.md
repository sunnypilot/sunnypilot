# sunnylink Settings UI Guide

> One YAML file per page. Edit, run the compiler, commit. The sunnylink frontend updates automatically.

For detailed architecture, capability fields, parity analysis, and dialog mappings, see [REFERENCE.md](REFERENCE.md).

## What you edit (and what's generated)

| File | What | When to edit |
|------|------|-------------|
| `settings_ui_src/pages/<page>.yaml` | One YAML per page (panel). Contains panel metadata + sections + items + sub_panels inline. | Adding/changing/removing a setting. |
| `settings_ui_src/pages/vehicle.yaml` | Per-brand settings page (`kind: vehicle`). Each brand is a section. | Adding/changing a vehicle-specific setting. |
| `settings_ui_src/_macros.yaml` | Named rule fragments referenced via `{$ref: "#/macros/<name>"}`. | Adding a reusable rule (e.g. a new platform gate). |
| **`settings_ui.json`** | **Generated from src tree by `compile_settings_ui.py`. Do not edit by hand.** | Never. Compiler emits it; frontend reads it. |

Pages today: `steering, cruise, display, visuals, toggles, device, software, developer, models, vehicle` (10).

Run `python sunnypilot/sunnylink/tools/compile_settings_ui.py` after edits. Add `--check` in CI to fail on out-of-sync `settings_ui.json`.

Display metadata (titles, descriptions, options, min/max/step/unit) is inline on each item. There is no separate metadata file.

## Page file shape

A page YAML contains the whole panel: metadata at the top, then `sections`. Each section has its own `items` and (optionally) `sub_panels`. Sub-panels are nested inside the section they belong to. Items appear in the order written in the file.

```yaml
# yaml-language-server: $schema=../_schemas/page.schema.json
id: steering
label: Steering
icon: steering_wheel
order: 1
remote_configurable: true
description: Lateral control, lane changes, and steering behavior

sections:
  - id: mads
    title: Modular Assistive Driving System (MADS)
    items:
      - key: Mads
        widget: toggle
        title: Enable Modular Assistive Driving System (MADS)
        description: |
          Enable the beloved MADS feature. Disable toggle to revert back
          to stock sunnypilot engagement/disengagement.
        enablement:
          - {$ref: "#/macros/offroad"}

    sub_panels:
      - id: mads_settings
        label: MADS Settings
        trigger_key: Mads
        trigger_condition: {type: param, key: Mads, equals: true}
        items:
          - key: MadsMainCruiseAllowed
            widget: toggle
            title: Toggle with Main Cruise
            description: |
              Note: For vehicles without LFA/LKAS button, disabling this will
              prevent lateral control engagement.
            enablement:
              - {$ref: "#/macros/offroad"}
              - {$ref: "#/macros/mads_full_platforms"}
```

The vehicle page has the same shape but declares `kind: vehicle`; each section's `id` becomes a brand key under `vehicle_settings` in the compiled JSON.

## Macros (named rule fragments)

`_macros.yaml` declares reusable rule lists. Reference them from any rules array via `{$ref: "#/macros/<name>"}`.

```yaml
macros:
  offroad: [{type: offroad_only}]
  longitudinal: [{type: capability, field: has_longitudinal_control, equals: true}]
  mads_full_platforms:
    - type: not
      condition:
        type: any
        conditions:
          - {type: capability, field: brand, equals: rivian}
          - type: all
            conditions:
              - {type: capability, field: brand, equals: tesla}
              - type: not
                condition: {type: capability, field: tesla_has_vehicle_bus, equals: true}
```

In an item:

```yaml
enablement:
  - {$ref: "#/macros/offroad"}
  - {$ref: "#/macros/mads_full_platforms"}
```

The compiler splices a list-context `$ref` into its parent list. Macros may reference other macros up to depth 3; cycles are an error.

## Compiler workflow

```
1. common/params_keys.h               — add/remove the C++ param key
2. params_metadata.json               — automated via update_params_metadata.py
3. settings_ui_src/pages/<page>.yaml  — add/edit/remove the item in the right section
4. python sunnypilot/sunnylink/tools/compile_settings_ui.py
5. python sunnypilot/sunnylink/tools/validate_settings_ui.py  (or: --check on the compiler)
6. uv run python -m pytest sunnypilot/sunnylink/tests/   # run regression + compiler tests
7. commit
```

CI runs `compile_settings_ui.py --check` to fail on hand-edited `settings_ui.json`.

## Compiled output reference (schema contract)

The tables below describe the **compiled** `settings_ui.json` schema — what the frontend consumes at runtime. JSON snippets show the wire shape; in the src tree you author YAML that compiles to the same shape. Use these as a contract reference for valid fields, their meanings, and rule types.

## Quick reference: widget types

| Widget | Use for | Fields needed |
|--------|---------|---------------|
| `toggle` | On/off boolean | `title` |
| `multiple_button` | 2-4 discrete options | `title` + `options` array |
| `option` | Numeric range or dropdown | `title` + `min/max/step` or `options` |
| `info` | Read-only display | `title` |

## Quick reference: item fields

| Field | Required | Description |
|-------|----------|-------------|
| `key` | Yes | Param key name (must exist in `params_keys.h`) |
| `widget` | Yes | `toggle`, `option`, `multiple_button`, `button`, `info` |
| `title` | Yes | Display name shown to the user |
| `description` | No | Inline explanatory text below the title. May be empty when only `details` is used. |
| `details` | No | Extended help text shown in a modal when the user taps an "i" button on the row. Independent of `description`: either, both, or neither may be present. |
| `options` | For selectors | Array of `{"value": 0, "label": "Off"}` objects (see per-option enablement below) |
| `min`, `max`, `step` | For sliders | Numeric range constraints |
| `unit` | No | Unit label. Static: `"seconds"`. Dynamic: `{"metric": "km/h", "imperial": "mph"}` (resolved by IsMetric) |
| `visibility` | No | Rules for show/hide. Settings are never hidden, always dimmed with UNAVAILABLE badge when rules fail |
| `enablement` | No | Rules for enabled/disabled (all must pass). Dimmed with badge when rules fail |
| `blocked` | No | `true` for device-only settings that cannot be modified remotely. Frontend shows as read-only |
| `title_param_suffix` | No | Dynamic title suffix. Example: `{"param": "IsMetric", "values": {"0": "mph", "1": "km/h"}}` |
| `sub_items` | No | Nested child items |
| `needs_onroad_cycle` | No | `true` if changing this param triggers a system restart. Frontend shows a "Restart" badge. See [REFERENCE.md - Remote Onroad Cycle](REFERENCE.md#remote-onroad-cycle) |

## Quick reference: rule types

| Rule | Example | Use for |
|------|---------|---------|
| `offroad_only` | `{"type": "offroad_only"}` | Grey out while driving |
| `not_engaged` | `{"type": "not_engaged"}` | Grey out only while engaged (started + selfdrive/MADS active) |
| `capability` | `{"type": "capability", "field": "has_longitudinal_control", "equals": true}` | Car-dependent visibility |
| `param` | `{"type": "param", "key": "Mads", "equals": true}` | Show/enable based on another setting |
| `param_compare` | `{"type": "param_compare", "key": "SpeedLimitMode", "op": ">", "value": 0}` | Numeric comparison |
| `not` | `{"type": "not", "condition": {...}}` | Negate a rule |
| `any` | `{"type": "any", "conditions": [...]}` | OR logic |
| `all` | `{"type": "all", "conditions": [...]}` | AND logic (for nesting inside `any`/`not`) |
| `$ref` | `{"$ref": "#/macros/offroad"}` | Reference a named rule fragment in `_macros.yaml` |

**Visibility design**: Settings are always visible. When visibility rules fail, the setting is dimmed with an UNAVAILABLE badge, so users know it exists but is not applicable.

**Enablement rules**: Grayed out (disabled) when rules fail. Frontend shows a contextual badge explaining why.

**Capability fields** (referenced in rules): `has_longitudinal_control`, `has_icbm`, `icbm_available`, `torque_allowed`, `brand`, `pcm_cruise`, `alpha_long_available`, `steer_control_type`, `enable_bsm`, `is_release`, `is_sp_release`, `is_development`, `tesla_has_vehicle_bus`, `has_stop_and_go`, `stock_longitudinal`

---

## How to

### Pick a writability rule (offroad / not_engaged / param-based)

| Use this | When | Why |
|---|---|---|
| `offroad_only` | Param can only be safely changed when the car is parked. Most user-facing toggles. | Strictest. Frontend shows "device is driving" badge and disables the row. |
| `not_engaged` | Param can be changed while the car is started but only when sunnypilot/MADS is **not** actively driving. | Less strict than offroad. Matches Raylib `engaged = started AND (selfdriveState.enabled OR mads.enabled)`. Use for items the device must apply mid-drive (e.g. test maneuvers, longitudinal stock-vs-OP toggle). |
| `param`-based | Behavior depends on another setting's value (parent toggle, mode selector, etc.). | Composes with `not`/`any`/`all` for arbitrary logic. |
| `capability`-based | Behavior depends on the connected car or device (brand, longitudinal, hardware). | Resolved on the device from `CarParams` / hardware. See [`capabilities.py`](../capabilities.py) for the full field list. |
| (no rule) | Param is always writable, no gating. | Rare. Prefer at least `offroad_only` unless the param is genuinely safe to flip mid-drive. |

Default for new toggles: `enablement: [{$ref: "#/macros/offroad"}]`. Drop down to `not_engaged` only if you've confirmed mid-drive write is safe in the controls/UI code path.

### Use `details` for safety notes / extended help

Inline `description` shows under the title. For longer caveats, safety notes, or "learn more" content, use `details` — the frontend renders an info button that opens a modal. Either field may be present alone or both together.

```yaml
- key: AutoLaneChangeTimer
  widget: option
  title: Auto Lane Change by Blinker
  description: |-
    Set a timer to delay the auto lane change operation when the blinker is used.
    No nudge on the steering wheel is required to auto lane change if a timer is set.
    Default is Nudge.
  details: |-
    Please use caution when using this feature. Only use the blinker when traffic
    and road conditions permit.
  options: [...]
```

For an item that is intentionally minimal inline (no inline body, only the modal):

```yaml
- key: SomeAdvancedToggle
  widget: toggle
  title: Some Advanced Feature
  details: |-
    Long-form rationale, caveats, links, etc. — kept entirely behind the info button.
```

### Add a toggle

1. Register in `common/params_keys.h`:
   ```cpp
   {"MyToggle", {PERSISTENT | BACKUP, BOOL}},
   ```

2. Open `settings_ui_src/pages/<page>.yaml`. Add the item to the right section:
   ```yaml
   - key: MyToggle
     widget: toggle
     title: My Feature
     description: What this feature does.
     enablement:
       - {$ref: "#/macros/offroad"}
   ```

   If changing the param requires an onroad cycle to take effect, add `needs_onroad_cycle: true`.

3. Compile + validate + test:
   ```
   python sunnypilot/sunnylink/tools/compile_settings_ui.py
   python sunnypilot/sunnylink/tools/validate_settings_ui.py
   uv run python -m pytest sunnypilot/sunnylink/tests/
   ```

### Add a multi-button option

```yaml
- key: MySelector
  widget: multiple_button
  title: Mode
  options:
    - {value: 0, label: Off}
    - {value: 1, label: On}
    - {value: 2, label: Auto}
```

### Add a slider or range

```yaml
- key: MyRange
  widget: option
  title: Follow Distance
  description: Time gap to lead vehicle.
  min: 0.5
  max: 3.0
  step: 0.1
  unit: seconds
```

### Add a slider with metric/imperial units

```yaml
- key: MinSpeed
  widget: option
  title: Minimum Speed
  min: 0
  max: 100
  step: 5
  unit: {metric: km/h, imperial: mph}
```

Frontend resolves the unit string based on the device's `IsMetric` param. Static units (e.g. `seconds`, `m/s²`) stay plain strings.

### Add a dynamic title suffix

```yaml
- key: FollowDistance
  widget: option
  title: Follow Distance
  title_param_suffix:
    param: IsMetric
    values: {'0': mph, '1': km/h}
  min: 0.5
  max: 3.0
  step: 0.1
```

Renders as "Follow Distance: mph" / "Follow Distance: km/h".

### Add a device-only read-only setting

```yaml
- key: OnroadCyclePendingRemote
  widget: info
  title: Pending Remote Cycle
  blocked: true
```

Frontend treats `blocked: true` items as read-only.

### Add a dropdown option

```yaml
- key: MyDropdown
  widget: option
  title: Recording Quality
  options:
    - {value: 0, label: Low (720p)}
    - {value: 1, label: Medium (1080p)}
    - {value: 2, label: High (4K)}
```

### Per-option enablement rules

```yaml
- key: MadsSteeringMode
  widget: multiple_button
  title: Steering Mode on Brake Pedal
  options:
    - value: 0
      label: Remain Active
      enablement:
        - {$ref: "#/macros/mads_full_platforms"}
    - value: 1
      label: Pause
      enablement:
        - {$ref: "#/macros/mads_full_platforms"}
    - value: 2
      label: Disengage
  enablement:
    - {$ref: "#/macros/offroad"}
```

When an option's enablement fails, that option is grayed out but still visible.

### Show only when another setting is on

```yaml
- key: ChildSetting
  widget: toggle
  title: Child Feature
  visibility:
    - {type: param, key: ParentToggle, equals: true}
```

(With the "dim instead of hide" design, this setting is dimmed, not hidden, when the rule fails.)

### Show only for specific brands

```yaml
- key: LongFeature
  widget: toggle
  title: Longitudinal Feature
  visibility:
    - {$ref: "#/macros/longitudinal"}
```

### Combine multiple conditions

The `enablement` array is implicit-AND: every entry must pass. Use `any` for OR, `all` for nested AND, `not` for negation. Wrap repeated combinations in a macro so future you doesn't re-derive the logic.

**AND across two params** (writable only when both Mads is on AND ICBM is enabled):
```yaml
enablement:
  - {type: param, key: Mads, equals: true}
  - {type: param, key: IntelligentCruiseButtonManagement, equals: true}
```

**OR across two params** (writable when either is on):
```yaml
enablement:
  - type: any
    conditions:
      - {type: param, key: ExperimentalMode, equals: true}
      - {type: param, key: DynamicExperimentalControl, equals: true}
```

**Mixed: capability AND param** (only on longitudinal cars when ShowAdvancedControls is on):
```yaml
enablement:
  - {$ref: "#/macros/longitudinal"}
  - {$ref: "#/macros/advanced_only"}
```

**Three-way: offroad AND torque-allowed AND not-NNLC** (real example: `EnforceTorqueControl`):
```yaml
enablement:
  - {$ref: "#/macros/offroad"}
  - {type: capability, field: torque_allowed, equals: true}
  - {type: param, key: NeuralNetworkLateralControl, equals: false}
```

**Negation across multiple platforms** (everything except Rivian + Tesla-no-bus):
```yaml
enablement:
  - {$ref: "#/macros/offroad"}
  - {$ref: "#/macros/mads_full_platforms"}   # macro encapsulates the not(any(rivian, all(tesla, not(bus)))) logic
```

If the same multi-condition block appears in 2+ items, **promote it to a macro** in `_macros.yaml`. Re-run `python sunnypilot/sunnylink/tools/apply_macros.py` to substitute existing inlined matches automatically.

### Mutual exclusion

```yaml
- key: FeatureAlpha
  widget: toggle
  title: Feature Alpha
  enablement:
    - {type: param, key: FeatureBeta, equals: false}

- key: FeatureBeta
  widget: toggle
  title: Feature Beta
  enablement:
    - {type: param, key: FeatureAlpha, equals: false}
```

### Add a section

In the page YAML, add an entry to the `sections` list:
```yaml
sections:
  - id: my_section
    title: My Section
    description: Optional subtitle
    enablement:
      - {$ref: "#/macros/longitudinal"}
    items:
      - {key: ..., widget: toggle, title: ...}
```

Sections support `visibility`, `enablement`, and `attestation_required`. When section-level rules fail, all items within are dimmed.

### Add a sub-panel

Sub-panels nest inside the section they belong to:
```yaml
sections:
  - id: parent_section
    title: Parent
    items: [...]
    sub_panels:
      - id: my_sub
        label: Advanced Settings
        trigger_key: ParentParam
        trigger_condition: {type: param, key: ParentParam, equals: true}
        items:
          - {key: ..., widget: toggle, title: ...}
```

### Add vehicle-brand settings

Edit `pages/vehicle.yaml`. Each section is a brand:
```yaml
id: vehicle
kind: vehicle
sections:
  - id: rivian
    title: Rivian Settings
    description: ''
    items:
      - key: RivianFeature
        widget: toggle
        title: Rivian One Pedal
        enablement:
          - {$ref: "#/macros/offroad"}
```

`kind: vehicle` tells the compiler to emit this page as `vehicle_settings.<brand>` in the wire JSON.

### Add a feature with toggles, sub-panel, and macro

Example: "Smart Wipers" with a master toggle, intensity selector, and sub-panel for advanced tuning, gated to torque-steering Hyundais on offroad.

1. **Param keys** — register all 4 in `common/params_keys.h`.

2. **Decide on a macro** — if "torque Hyundai" gating is reused, add to `_macros.yaml`:
   ```yaml
   torque_hyundai:
     - {$ref: "#/macros/offroad"}
     - {type: capability, field: brand, equals: hyundai}
     - {type: capability, field: torque_allowed, equals: true}
   ```

3. **Edit the relevant page** — `pages/visuals.yaml` (or wherever the feature lives). Add a new section + sub_panel:
   ```yaml
   sections:
     - id: smart_wipers
       title: Smart Wipers
       description: Camera-driven wiper control (Hyundai/Kia, torque only)
       items:
         - key: SmartWipersEnabled
           widget: toggle
           title: Enable Smart Wipers
           enablement:
             - {$ref: "#/macros/torque_hyundai"}
         - key: SmartWipersIntensity
           widget: multiple_button
           title: Sensitivity
           options:
             - {value: 0, label: Low}
             - {value: 1, label: Medium}
             - {value: 2, label: High}
           visibility:
             - {type: param, key: SmartWipersEnabled, equals: true}
           enablement:
             - {$ref: "#/macros/torque_hyundai"}
       sub_panels:
         - id: smart_wipers_tuning
           label: Smart Wipers Tuning
           trigger_key: SmartWipersEnabled
           trigger_condition: {type: param, key: SmartWipersEnabled, equals: true}
           items:
             - key: SmartWipersHysteresis
               widget: option
               title: Hysteresis (frames)
               min: 1
               max: 30
               step: 1
               enablement:
                 - {$ref: "#/macros/offroad"}
                 - {$ref: "#/macros/advanced_only"}
   ```

4. **Compile / validate / test**:
   ```
   python sunnypilot/sunnylink/tools/compile_settings_ui.py
   python sunnypilot/sunnylink/tools/validate_settings_ui.py
   uv run python -m pytest sunnypilot/sunnylink/tests/
   ```

   `apply_macros.py` is automatic for newly-added items only if you wrote the rule list inline; for greenfield items, you'd write `$ref` directly.

### Change a toggle's behavior

1. Find the item in `pages/<page>.yaml`.
2. Edit `visibility`/`enablement`/`options[].enablement` directly. Use macros where possible.
3. **Add a regression test** in `sunnypilot/sunnylink/tests/test_settings_changes.py` that asserts the new gate exists. Use existing tests (e.g. `TestMadsBrandGates`, `TestNotEngagedReplacement`) as templates: lookup item by key, assert `_references_capability_field(rules, "...")` or `_flatten_rule_types(rules)` contains/excludes a type. This freezes the new behavior so a future edit won't silently revert it.
4. Compile + run the full suite. Per-bug test should pass; structural tests should remain green.

### Change a widget type or options

Editing `widget:` from `toggle` to `multiple_button` is a frontend behavior change. Whenever you change widget shape:
- The param's underlying type (bool / int / string) must match what the new widget writes. `toggle` writes bool; `multiple_button`/`option` write int/string. Update `params_keys.h` if the type changes.
- Add an `options:` list when switching to `multiple_button` or `option`.
- Old values stored on devices may not be valid for the new widget. Consider a migration in `sunnypilot/system/updated/` if users have stale values.

### Deprecate or remove a setting

1. Remove the item from `pages/<page>.yaml`.
2. Remove the param key from `common/params_keys.h` **only after** confirming nothing in `selfdrive/`, `sunnypilot/`, or any controls code reads it.
3. If the param has been on user devices, drop it via a migration (see `sunnypilot/system/updated/`) so stale values don't linger.
4. Compile + validate + test. The validator's "no duplicate keys" + structural checks will fail if anything still references the removed key.

### Move a setting to another page

Cut the item block from one page YAML, paste into the target page's section. Compile + validate. The "no duplicate keys" check catches forgotten copies.

### Change display text

Edit `title:` or `description:` in the page YAML and recompile to regenerate `settings_ui.json`.

### Reorder sections, sub-panels, and items

Reorder them within their parent list in the YAML. The compiler preserves authored order — no `order:` field required at the section/sub_panel/item level (panel-level `order:` controls which page comes first in the side nav).

---

### Capability labels and tooltips

The schema response includes `capability_labels`, which map capability field names to descriptions. The frontend uses these to show contextual tooltips when a capability rule prevents a setting from being used.

The device defines these labels in `capabilities.py:CAPABILITY_LABELS`. Examples:

- `has_longitudinal_control` → "sunnypilot longitudinal control"
- `torque_allowed` → "torque steering (not available for angle steering vehicles)"
- `brand` → "Vehicle brand"

### Centralized param enforcement

The device-side UI enforces capability constraints in `selfdrive/ui/sunnypilot/ui_state.py:_enforce_constraints()`, which removes incompatible params based on car capabilities. This is the single source of truth for such constraints.

Settings layouts should not duplicate these params.remove() calls. Instead, rely on schema rules and centralized enforcement to prevent duplicate logic and ensure consistency.

Example constraints in `_enforce_constraints()`:
- Angle steering cars: remove `EnforceTorqueControl` and `NeuralNetworkLateralControl`
- No CarParams: remove all car-dependent params
- No longitudinal: remove `ExperimentalMode`
- No ICBM: remove `IntelligentCruiseButtonManagement`
