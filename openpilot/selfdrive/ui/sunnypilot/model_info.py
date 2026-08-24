"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.models.helpers import get_active_source, get_selected_bundle
from openpilot.sunnypilot.models.model_name import DEFAULT_BIG_MODEL, DEFAULT_MODEL


def model_info() -> tuple[str, str, str]:
  """returns (active source, active model name, other model name)"""
  source = get_active_source(usbgpu=ui_state.usbgpu,
                             usbgpu_active=ui_state.usbgpu_active, usbgpu_loading=ui_state.usbgpu_loading,
                             offroad=ui_state.is_offroad())
  other = "qcom" if source == "usbgpu" else "usbgpu"
  active_bundle = get_selected_bundle(ui_state.params, source)
  other_bundle = get_selected_bundle(ui_state.params, other)

  active_name = active_bundle.displayName if active_bundle \
    else f"{DEFAULT_BIG_MODEL if source == 'usbgpu' else DEFAULT_MODEL} (Default)"
  other_name = other_bundle.displayName if other_bundle \
    else f"{DEFAULT_MODEL if source == 'usbgpu' else DEFAULT_BIG_MODEL} (Default)"
  return source, active_name, other_name
