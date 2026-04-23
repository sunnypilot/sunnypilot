# sunnylink Settings UI Guide

> Edit one JSON file, run the validator, commit. The sunnylink frontend updates automatically.

For detailed architecture, capability fields, parity analysis, and dialog mappings, see [REFERENCE.md](REFERENCE.md).

## The File You Edit

| File | What | When to edit |
|------|------|-------------|
| `settings_ui.json` | Structure, widget types, display text, options, rules - everything | Adding/moving/removing/renaming a setting |

All metadata (titles, descriptions, options, min/max/step/unit) lives **inline on each item**. There is no separate metadata file.

## Quick Reference: Widget Types

| Widget | Use for | Fields needed |
|--------|---------|---------------|
| `toggle` | On/off boolean | `title` |
| `multiple_button` | 2-4 discrete options | `title` + `options` array |
| `option` | Numeric range or dropdown | `title` + `min/max/step` or `options` |
| `info` | Read-only display | `title` |

## Quick Reference: Item Fields

| Field | Required | Description |
|-------|----------|-------------|
| `key` | Yes | Param key name (must exist in `params_keys.h`) |
| `widget` | Yes | `toggle`, `option`, `multiple_button`, `button`, `info` |
| `title` | Yes | Display name shown to the user |
| `description` | No | Explanatory text below the title |
| `options` | For selectors | Array of `{"value": 0, "label": "Off"}` objects (see per-option enablement below) |
| `min`, `max`, `step` | For sliders | Numeric range constraints |
| `unit` | No | Unit label. Static: `"seconds"`. Dynamic: `{"metric": "km/h", "imperial": "mph"}` (resolved by IsMetric) |
| `visibility` | No | Rules for show/hide. Settings are **never hidden**, always dimmed with UNAVAILABLE badge when rules fail |
| `enablement` | No | Rules for enabled/disabled (all must pass). Dimmed with badge when rules fail |
| `blocked` | No | `true` for device-only settings that cannot be modified remotely. Frontend shows as read-only |
| `title_param_suffix` | No | Dynamic title suffix. Example: `{"param": "IsMetric", "values": {"0": "mph", "1": "km/h"}}` |
| `sub_items` | No | Nested child items |
| `needs_onroad_cycle` | No | `true` if changing this param triggers a system restart. Frontend shows a "Restart" badge. See [REFERENCE.md - Remote Onroad Cycle](REFERENCE.md#remote-onroad-cycle) |

## Quick Reference: Rule Types

| Rule | Example | Use for |
|------|---------|---------|
| `offroad_only` | `{"type": "offroad_only"}` | Grey out while driving |
| `capability` | `{"type": "capability", "field": "has_longitudinal_control", "equals": true}` | Car-dependent visibility |
| `param` | `{"type": "param", "key": "Mads", "equals": true}` | Show/enable based on another setting |
| `param_compare` | `{"type": "param_compare", "key": "SpeedLimitMode", "op": ">", "value": 0}` | Numeric comparison |
| `not` | `{"type": "not", "condition": {...}}` | Negate a rule |
| `any` | `{"type": "any", "conditions": [...]}` | OR logic |
| `all` | `{"type": "all", "conditions": [...]}` | AND logic (for nesting inside `any`/`not`) |

**Visibility design**: Settings are always visible. When visibility rules fail, the setting is dimmed with an UNAVAILABLE badge, so users know it exists but is not applicable.

**Enablement rules**: Grayed out (disabled) when rules fail. Frontend shows a contextual badge explaining why.

**Capability fields** (referenced in rules): `has_longitudinal_control`, `has_icbm`, `icbm_available`, `torque_allowed`, `brand`, `pcm_cruise`, `alpha_long_available`, `steer_control_type`, `enable_bsm`, `is_release`, `is_sp_release`, `is_development`, `tesla_has_vehicle_bus`, `has_stop_and_go`, `stock_longitudinal`

---

## How To

### Add a new toggle

1. Register in `common/params_keys.h`:
   ```cpp
   {"MyToggle", {PERSISTENT | BACKUP, BOOL}},
   ```

2. Add to `settings_ui.json` in the right panel/section `items` array:
   ```json
   {
     "key": "MyToggle",
     "widget": "toggle",
     "title": "My Feature",
     "description": "What this feature does.",
     "enablement": [{"type": "offroad_only"}]
   }
   ```

   If the toggle requires an onroad cycle (system restart) to take effect:
   ```json
   {
     "key": "MyToggle",
     "widget": "toggle",
     "title": "My Feature",
     "description": "What this feature does.",
     "needs_onroad_cycle": true,
     "enablement": [{"type": "offroad_only"}]
   }
   ```

3. Validate: `python sunnypilot/sunnylink/tools/validate_settings_ui.py`

### Add a multi-button selector

```json
{
  "key": "MySelector",
  "widget": "multiple_button",
  "title": "Mode",
  "options": [
    {"value": 0, "label": "Off"},
    {"value": 1, "label": "On"},
    {"value": 2, "label": "Auto"}
  ]
}
```

### Add a slider/range

```json
{
  "key": "MyRange",
  "widget": "option",
  "title": "Follow Distance",
  "description": "Time gap to lead vehicle.",
  "min": 0.5,
  "max": 3.0,
  "step": 0.1,
  "unit": "seconds"
}
```

### Add a slider with metric/imperial unit

For speed or distance values that change based on the user's `IsMetric` preference:

```json
{
  "key": "MinSpeed",
  "widget": "option",
  "title": "Minimum Speed",
  "min": 0,
  "max": 100,
  "step": 5,
  "unit": {"metric": "km/h", "imperial": "mph"}
}
```

The frontend resolves the correct unit string based on the device's `IsMetric` param value. Static units (like `"seconds"`, `"m/s²"`) remain plain strings.

### Add a title with dynamic suffix

Use `title_param_suffix` to append a param value to the title:

```json
{
  "key": "FollowDistance",
  "widget": "option",
  "title": "Follow Distance",
  "title_param_suffix": {
    "param": "IsMetric",
    "values": {"0": "mph", "1": "km/h"}
  },
  "min": 0.5,
  "max": 3.0,
  "step": 0.1
}
```

The title will display as "Follow Distance: mph" or "Follow Distance: km/h" based on the `IsMetric` param value.

### Add a device-only (read-only) setting

Use `blocked: true` for settings that cannot be modified remotely:

```json
{
  "key": "OnroadCyclePendingRemote",
  "widget": "info",
  "title": "Pending Remote Cycle",
  "blocked": true
}
```

The frontend will display this as read-only and prevent any changes.

### Add a dropdown

```json
{
  "key": "MyDropdown",
  "widget": "option",
  "title": "Recording Quality",
  "options": [
    {"value": 0, "label": "Low (720p)"},
    {"value": 1, "label": "Medium (1080p)"},
    {"value": 2, "label": "High (4K)"}
  ]
}
```

### Per-option enablement

Individual options within `multiple_button` or `option` widgets can have their own enablement rules:

```json
{
  "key": "MadsSteeringMode",
  "widget": "multiple_button",
  "title": "Steering Mode on Brake Pedal",
  "options": [
    {
      "value": 0,
      "label": "Remain Active",
      "enablement": [{"type": "capability", "field": "brand", "equals": "tesla"}]
    },
    {
      "value": 1,
      "label": "Pause",
      "enablement": [{"type": "offroad_only"}]
    }
  ]
}
```

When an option's enablement fails, that option is grayed out (disabled) but still visible.

### Show only when another setting is on

```json
{
  "key": "ChildSetting",
  "widget": "toggle",
  "title": "Child Feature",
  "visibility": [{"type": "param", "key": "ParentToggle", "equals": true}]
}
```

Note: Due to the "dim instead of hide" design, this setting will be dimmed (not hidden) when the rule fails.

### Show only for certain cars

```json
{
  "key": "LongFeature",
  "widget": "toggle",
  "title": "Longitudinal Feature",
  "visibility": [{"type": "capability", "field": "has_longitudinal_control", "equals": true}]
}
```

### Mutual exclusion (only one can be on)

```json
{
  "key": "FeatureAlpha",
  "widget": "toggle",
  "title": "Feature Alpha",
  "enablement": [{"type": "param", "key": "FeatureBeta", "equals": false}]
},
{
  "key": "FeatureBeta",
  "widget": "toggle",
  "title": "Feature Beta",
  "enablement": [{"type": "param", "key": "FeatureAlpha", "equals": false}]
}
```

### Add a new section

```json
{
  "id": "my_section",
  "title": "My Section",
  "description": "Optional subtitle",
  "items": [...],
  "enablement": [{"type": "capability", "field": "has_longitudinal_control", "equals": true}]
}
```

Sections can have visibility and enablement rules (optional). When section-level rules fail, all items within are dimmed.

### Add section-level enablement

Sections can be conditionally available or enabled via `visibility` or `enablement`:

```json
{
  "id": "longitudinal_tuning",
  "title": "Longitudinal Tuning",
  "description": "Advanced control parameters",
  "visibility": [{"type": "capability", "field": "has_longitudinal_control", "equals": true}],
  "items": [...]
}
```

### Add a sub-panel (drill-down page)

```json
{
  "id": "my_sub",
  "label": "Advanced Settings",
  "trigger_key": "ParentParam",
  "trigger_condition": {"type": "param", "key": "ParentParam", "equals": true},
  "items": [...]
}
```

### Add vehicle-specific settings

Add to `vehicle_settings` in `settings_ui.json`:
```json
"rivian": {
  "title": "Rivian Settings",
  "items": [
    {
      "key": "RivianFeature",
      "widget": "toggle",
      "title": "Rivian One Pedal",
      "enablement": [{"type": "offroad_only"}]
    }
  ]
}
```

### Change display text

Edit the `title` or `description` on the item in `settings_ui.json`.

### Move a setting between panels

Remove from source panel, add to target panel. Validator catches duplicates.

### Reorder sections

Set `order` field on sections, or reorder the JSON array.

---

### Capability labels and tooltips

The schema response includes `capability_labels` which map capability field names to human-readable descriptions. These are used by the frontend to show contextual tooltips when a capability rule prevents a setting from being used.

The device defines these labels in `capabilities.py:CAPABILITY_LABELS`. Examples:

- `has_longitudinal_control` → "sunnypilot longitudinal control"
- `torque_allowed` → "torque steering (not available for angle steering vehicles)"
- `brand` → "Vehicle brand"

### Centralized param enforcement

The device-side UI enforces capability constraints in `selfdrive/ui/sunnypilot/ui_state.py:_enforce_sp_constraints()`. This method removes incompatible params based on car capabilities, and should be the single source of truth for such constraints.

**Settings layouts should NOT duplicate these params.remove() calls.** Instead, they should rely on schema rules and the centralized enforcement. This prevents duplicate logic and ensures consistency.

Example constraints in `_enforce_sp_constraints()`:
- Angle steering cars: remove `EnforceTorqueControl` and `NeuralNetworkLateralControl`
- No CarParams: remove all car-dependent params
- No longitudinal: remove `ExperimentalMode`
- No ICBM: remove `IntelligentCruiseButtonManagement`
