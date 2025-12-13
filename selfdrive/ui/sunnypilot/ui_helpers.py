"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""


def update_item_from_param(item, key, params):
  if not (action := getattr(item, 'action_item', None)):
    return

  if hasattr(action, 'set_state'):
    action.set_state(params.get_bool(key))
  elif hasattr(action, 'set_value'):
    action.set_value(params.get(key, return_default=True))
  else:
    try:
      val = int(params.get(key, return_default=True))
      if hasattr(action, 'selected_button'):
        action.selected_button = val
      if hasattr(action, 'current_value'):
        action.current_value = val
    except (ValueError, TypeError):
      pass


def sync_layout_params(layout, param_name, params):
  targets = []
  if toggles := getattr(layout, '_toggles', None):
    targets.extend([(item, k) for k, item in toggles.items()])

  items = getattr(layout, 'items', []) or getattr(getattr(layout, '_scroller', None), '_items', [])
  for item in items:
    action = getattr(item, 'action_item', None)
    if key := getattr(action, 'param_key', None) or getattr(getattr(action, 'toggle', None), 'param_key', None):
      targets.append((item, key))

  for item, key in targets:
    if param_name is None or key == param_name:
      update_item_from_param(item, key, params)
