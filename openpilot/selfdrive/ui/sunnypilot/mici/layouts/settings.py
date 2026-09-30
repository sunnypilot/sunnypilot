"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import math

import pyray as rl

from openpilot.selfdrive.ui.mici.layouts.settings import settings as OP
from openpilot.selfdrive.ui.mici.layouts.settings.settings import SettingsBigButton
from openpilot.selfdrive.ui.mici.layouts.settings.device import DeviceLayoutMici
from openpilot.selfdrive.ui.mici.widgets.button import BigCircleButton
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog, BigDialog
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnylink import SunnylinkLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.models import ModelsLayoutMici
from openpilot.selfdrive.ui.sunnypilot.mici.layouts.sunnydrive import SunnydriveLayoutMici
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.application import gui_app, FontWeight
from openpilot.system.ui.lib.multilang import tr

ICON_SIZE = 70
BIG_ICON_SIZE = 110


class SunnylinkBigButton(SettingsBigButton):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self._label.set_font_weight(FontWeight.AUDIOWIDE)

  def _get_label_font_size(self):
    # Audiowide runs wider than Inter: "sunnylink" wraps to two lines at 64
    return 56


def sunnydrive_icon(width, height):
  """The sunnydrive icon (a sun over a car roof), drawn once in code so it needs no image asset.
  Drawn at 4x on a 336x312 grid, then scaled down for smooth edges."""
  s = 4
  img = rl.gen_image_color(336 * s, 312 * s, rl.BLANK)
  p = rl.ffi.addressof(img)

  def dot(x, y, r, color):
    rl.image_draw_circle(p, int(x * s), int(y * s), int(r * s), color)

  def roof(r, color):   # a shallow circular arc, apex under the sun, ends reaching down beside the wheels
    for i in range(-52, 53):
      t = math.radians(i)
      dot(168 + 194 * math.sin(t), 399 - 194 * math.cos(t), r, color)

  dot(168, 100, 100, rl.WHITE)   # the sun
  roof(28, rl.BLANK)            # a gap between the sun and the roof
  roof(14, rl.WHITE)            # the roof
  rl.image_draw_rectangle(p, 70 * s, 284 * s, 196 * s, 28 * s, rl.WHITE)   # the car's body between its wheels
  for x in (84, 252):
    dot(x, 300, 18, rl.WHITE)
    dot(x, 300, 11, rl.BLANK)   # wheel
  rl.image_resize(p, width, height)
  texture = rl.load_texture_from_image(img)
  rl.unload_image(img)
  rl.set_texture_filter(texture, rl.TextureFilter.TEXTURE_FILTER_BILINEAR)
  return texture


class SunnydriveBigButton(SettingsBigButton):
  def _get_label_font_size(self):
    return 54   # "sunnydrive" wraps under the icon at 64


class SettingsLayoutSP(OP.SettingsLayout):
  def __init__(self):
    OP.SettingsLayout.__init__(self)

    device_panel = DeviceLayoutMici()
    self._scroller._items[2].set_click_callback(lambda: gui_app.push_widget(device_panel))

    self.icon_offroad_enable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/always_offroad.png", BIG_ICON_SIZE,
                                               BIG_ICON_SIZE)
    self.icon_offroad_disable = gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/disable_offroad.png", BIG_ICON_SIZE,
                                                BIG_ICON_SIZE)
    self.icon_offroad_slider = gui_app.texture("icons_mici/settings/device/lkas.png", BIG_ICON_SIZE, BIG_ICON_SIZE)

    sunnylink_panel = SunnylinkLayoutMici()
    sunnylink_btn = SunnylinkBigButton(tr("sunnylink"), "", gui_app.texture("../../sunnypilot/selfdrive/assets/icons_mici/sunnylink.png", 76, 44))
    sunnylink_btn.set_click_callback(lambda: gui_app.push_widget(sunnylink_panel))

    models_panel = ModelsLayoutMici()
    models_btn = SettingsBigButton(tr("models"), "", gui_app.texture("../../sunnypilot/selfdrive/assets/offroad/icon_models.png", ICON_SIZE, ICON_SIZE))
    models_btn.set_click_callback(lambda: gui_app.push_widget(models_panel))

    sunnydrive_panel = SunnydriveLayoutMici()
    sunnydrive_btn = SunnydriveBigButton(tr("sunnydrive"), "", sunnydrive_icon(64, 59))
    sunnydrive_btn.set_click_callback(lambda: gui_app.push_widget(sunnydrive_panel))

    # onroad: enable button sits at the front (left of toggles)
    self._enable_offroad_btn_onroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_onroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_onroad.set_visible(lambda: ui_state.started and not ui_state.always_offroad)

    # offroad: enable button sits at the end (right of developer)
    self._enable_offroad_btn_offroad = BigCircleButton(self.icon_offroad_enable, red=True)
    self._enable_offroad_btn_offroad.set_click_callback(lambda: self._handle_always_offroad(True))
    self._enable_offroad_btn_offroad.set_visible(lambda: not ui_state.started and not ui_state.always_offroad)

    self._disable_offroad_btn = BigCircleButton(self.icon_offroad_disable, red=False)
    self._disable_offroad_btn.set_click_callback(lambda: self._handle_always_offroad(False))
    self._disable_offroad_btn.set_visible(lambda: ui_state.always_offroad)

    items = self._scroller._items.copy()

    items.insert(1, models_btn)
    items.insert(5, sunnylink_btn)

    # front slots (only one ever visible at a time): exit-always-offroad, then enable-onroad
    items.insert(0, self._enable_offroad_btn_onroad)
    items.insert(0, self._disable_offroad_btn)
    items.insert(0, sunnydrive_btn)
    # end slot: enable-offroad (right of developer)
    items.append(self._enable_offroad_btn_offroad)

    self._scroller._items.clear()
    for item in items:
      self._scroller.add_widget(item)

  def _update_state(self):
    super()._update_state()

  def _handle_always_offroad(self, enable: bool):

    def _set_offroad_status(status: bool):
      if not ui_state.engaged:
        ui_state.params.put_bool("OffroadMode", status)
        ui_state.always_offroad = status

    if not enable:
      dlg = BigConfirmationDialog(tr("slide to exit always offroad"), self.icon_offroad_slider, red=False,
                                  confirm_callback=lambda: _set_offroad_status(False))
    else:
      if ui_state.engaged:
        gui_app.push_widget(BigDialog(tr("disengage to enable always offroad"), "", ))
        return

      dlg = BigConfirmationDialog(tr("slide to force offroad"), self.icon_offroad_slider, red=True,
                                  confirm_callback=lambda: _set_offroad_status(True))
    gui_app.push_widget(dlg)
