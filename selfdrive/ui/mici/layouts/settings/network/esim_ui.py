import pyray as rl
from collections.abc import Callable
from functools import partial

from openpilot.system.hardware import HARDWARE
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigToggle
from openpilot.selfdrive.ui.mici.widgets.dialog import BigInputDialog, BigConfirmationDialog, BigDialog

def show_error_dialog(message: str, retry_callback: Callable[[], None] | None = None):
  # scroll=True truncates everything after the first newline, so flatten the string
  dlg = BigDialog(tr("Error"), message.replace("\n", " | "), scroll=True)
  if retry_callback:
    dlg.set_back_callback(retry_callback)
  gui_app.push_widget(dlg)


class EsimProfileConfigLayout(NavScroller):
  def __init__(self, profile, lpa, refresh_callback: Callable[[], None], back_callback: Callable[[], None] | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)
    
    self._profile = profile
    self._lpa = lpa
    self._refresh_callback = refresh_callback
    
    self._init_layout()

  def _init_layout(self):
    self._scroller._items.clear()
    
    # 1. Enable Toggle
    enable_toggle = BigToggle(tr("Enable Profile"), "", initial_state=self._profile.enabled, toggle_callback=self._on_enable_toggled)
    self._scroller.add_widget(enable_toggle)

    # 2. Rename Nickname
    rename_btn = BigButton(tr("Rename Nickname"), tr("rename"), scroll=True)
    rename_btn.set_click_callback(self._on_rename_clicked)
    self._scroller.add_widget(rename_btn)
    
    # 3. Delete Profile
    delete_btn = BigButton(tr("Delete Profile"), tr("delete"), scroll=True)
    delete_btn.set_click_callback(self._on_delete_clicked)
    self._scroller.add_widget(delete_btn)

  def _on_enable_toggled(self, checked: bool):
    try:
      if checked:
        self._lpa.switch_profile(self._profile.iccid)
      else:
        self._lpa.disable_profile(self._profile.iccid)
      self._refresh_callback()
    except Exception as e:
      show_error_dialog(str(e))
      self._refresh_callback()

  def _on_rename_clicked(self):
    def update_nickname(new_name: str):
      new_name = new_name.strip()
      try:
        self._lpa.nickname_profile(self._profile.iccid, new_name)
        self._profile.nickname = new_name
        self._refresh_callback()
      except Exception as e:
        show_error_dialog(str(e))
        
    dlg = BigInputDialog(tr("enter nickname..."), self._profile.nickname or "", minimum_length=0, confirm_callback=update_nickname)
    gui_app.push_widget(dlg)

  def _on_delete_clicked(self):
    def confirm_delete():
      try:
        self._lpa.delete_profile(self._profile.iccid)
        gui_app.pop_widget() # Pop Config Layout to return to management list
        self._refresh_callback()
      except Exception as e:
        show_error_dialog(str(e))

    msg = f"{tr('Are you sure you want to delete profile')} {self._profile.iccid}?\n{tr('This cannot be undone.')}"
    dlg = BigConfirmationDialog(msg, None, confirm_callback=confirm_delete)
    gui_app.push_widget(dlg)


class EsimManagementLayoutMici(NavScroller):
  def __init__(self, back_callback: Callable[[], None] | None = None):
    super().__init__()
    if back_callback is not None:
      self.set_back_callback(back_callback)
    
    try:
      self._lpa = HARDWARE.get_sim_lpa()
    except NotImplementedError:
      self._lpa = None

    self._profiles = []
    self._last_download_str = ""
    if self._lpa:
      self.refresh()
    else:
      self._init_unsupported_layout()

  def _init_unsupported_layout(self):
    btn = BigButton(tr("eSIM Not Supported on this hardware"), "")
    btn.set_enabled(False)
    self._scroller.add_widget(btn)

  def refresh(self):
    if not self._lpa:
      return

    self._scroller._items.clear()

    try:
      self._profiles = self._lpa.list_profiles()
    except Exception as e:
      self._profiles = []
      show_error_dialog(f"{tr('Failed to read eSIM profiles')}: {str(e)}")

    # Add Profile Button
    add_btn = BigButton(tr("Add Custom Profile"), tr("download"), scroll=True)
    add_btn.set_click_callback(self._on_add_profile)
    self._scroller.add_widget(add_btn)

    # Sync Notifications Button
    sync_btn = BigButton(tr("Sync Carrier Updates"), tr("sync"), scroll=True)
    sync_btn.set_click_callback(self._on_sync_notifications)
    self._scroller.add_widget(sync_btn)

    # List Current Profiles
    for p in self._profiles:
      nickname = p.nickname if p.nickname else tr("<unnamed>")
      name_str = f"{nickname} - {p.provider}"
      
      btn = BigButton(name_str, p.iccid, scroll=True)
      if p.enabled:
        btn.set_value(tr("Active"))
      
      btn.set_click_callback(partial(self._on_profile_tapped, p))
      self._scroller.add_widget(btn)

  def _on_sync_notifications(self):
    try:
      self._lpa.process_notifications()
    except Exception as e:
      show_error_dialog(f"{tr('Sync failed')}:\n{str(e)}")

  def _on_add_profile(self):
    def perform_download(download_str: str, confirmation_code: str | None = None):
      download_str = download_str.strip()
      if not download_str:
        return
      self._last_download_str = download_str
      try:
        self._lpa.download_profile(download_str, confirmation_code=confirmation_code, nickname="")
        self._last_download_str = ""
        self.refresh()
      except Exception as e:
        if "Confirmation code required" in str(e) and not confirmation_code:
          def retry_with_cc(cc_val: str):
            perform_download(download_str, cc_val.strip())
          cc_dlg = BigInputDialog(tr("enter Confirmation Code..."), "", minimum_length=1, confirm_callback=retry_with_cc)
          gui_app.push_widget(cc_dlg)
        else:
          show_error_dialog(f"{tr('Download failed')}:\n{str(e)}", retry_callback=self._on_add_profile)
            
    dlg = BigInputDialog(tr("enter Activation Text (LPA:1$...)..."), self._last_download_str, minimum_length=0, confirm_callback=perform_download)
    gui_app.push_widget(dlg)

  def _on_profile_tapped(self, profile):
    def back_to_management():
      gui_app.pop_widget()
    
    config_layout = EsimProfileConfigLayout(profile, self._lpa, self.refresh, back_to_management)
    gui_app.push_widget(config_layout)
