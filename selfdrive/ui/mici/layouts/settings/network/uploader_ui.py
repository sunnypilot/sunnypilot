from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiParamToggle, BigParamControl
from openpilot.selfdrive.ui.mici.widgets.dialog import BigInputDialog, BigConfirmationDialog
import os
from openpilot.system.ui.widgets.scroller import NavScroller
from openpilot.system.ui.lib.application import gui_app
from openpilot.common.params import Params

class DashcamUploaderLayoutMici(NavScroller):
  def __init__(self, back_callback=None):
    super().__init__()
    self._params = Params()
    self._back_callback = back_callback

    # Provider Toggle
    self._provider_toggle = BigMultiParamToggle(
      "provider", 
      "DashcamUploaderProvider", 
      ["none", "google drive", "rsync"],
      select_callback=self._on_provider_changed
    )

    # Delete Toggle (Global)
    self._delete_synced_toggle = BigParamControl("delete source after upload", "DashcamUploaderDeleteSynced")

    # Sync Connection Toggle
    self._sync_mode_toggle = BigMultiParamToggle(
      "sync mode", 
      "DashcamUploaderSyncMode", 
      ["off", "wifi-only", "wifi+lte"]
    )

    # Video Mode Toggle
    self._video_mode_toggle = BigMultiParamToggle(
      "video mode",
      "DashcamUploaderVideoMode",
      ["off", "low-res", "high-res"]
    )

    # Upload Logs
    self._upload_logs_toggle = BigParamControl("upload logs", "DashcamUploaderUploadLogs")

    # GDrive Widgets
    self._gdrive_auth_btn = BigButton("google drive credentials")
    self._gdrive_auth_btn.set_click_callback(self._edit_gdrive_auth)

    self._gdrive_folder_btn = BigButton("google drive folder id")
    self._gdrive_folder_btn.set_click_callback(self._edit_gdrive_folder)

    # Rsync Widgets
    self._rsync_target_btn = BigButton("rsync target config")
    self._rsync_target_btn.set_click_callback(self._edit_rsync_target)
    
    self._rsync_key_btn = BigButton("rsync private key")
    self._rsync_key_btn.set_click_callback(self._edit_rsync_key)

    # Reset Queue Button
    self._reset_queue_btn = BigButton("reset upload queue")
    self._reset_queue_btn.set_click_callback(self._confirm_reset_queue)

    self._scroller.add_widgets([
      self._provider_toggle,
      self._sync_mode_toggle,
      self._video_mode_toggle,
      self._upload_logs_toggle,
      self._delete_synced_toggle,
      self._gdrive_auth_btn,
      self._gdrive_folder_btn,
      self._rsync_target_btn,
      self._rsync_key_btn,
      self._reset_queue_btn
    ])

    self._update_visibility()

  def _update_visibility(self):
    val = self._params.get("DashcamUploaderProvider")
    # "0": none, "1": google drive, "2": rsync
    idx = 0
    if val is not None:
      try:
        idx = int(val)
      except Exception:
        pass
        
    is_gd = (idx == 1)
    is_rs = (idx == 2)

    self._sync_mode_toggle.set_visible(idx > 0)
    self._video_mode_toggle.set_visible(idx > 0)
    self._upload_logs_toggle.set_visible(idx > 0)
    self._delete_synced_toggle.set_visible(idx > 0)
    self._reset_queue_btn.set_visible(idx > 0)
    
    self._gdrive_auth_btn.set_visible(is_gd)
    self._gdrive_folder_btn.set_visible(is_gd)
    
    self._rsync_target_btn.set_visible(is_rs)
    self._rsync_key_btn.set_visible(is_rs)

  def _on_provider_changed(self, value: str):
    self._update_visibility()

  def _edit_gdrive_auth(self):
    current = self._params.get("DashcamUploaderGDAuth") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderGDAuth", val)
      
    dlg = BigInputDialog("enter google drive credentials...", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _edit_gdrive_folder(self):
    current = self._params.get("DashcamUploaderGDFolder") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderGDFolder", val)
      
    dlg = BigInputDialog("enter folder ID (or leave blank)...", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _edit_rsync_target(self):
    current = self._params.get("DashcamUploaderRsyncTarget") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderRsyncTarget", val)
    dlg = BigInputDialog("e.g. user@192.168.1.100:/mnt", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _edit_rsync_key(self):
    current = self._params.get("DashcamUploaderRsyncKey") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderRsyncKey", val)
    dlg = BigInputDialog("paste base64 or raw private key...", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _confirm_reset_queue(self):
    def clear_flags():
      count = 0
      log_root = '/data/media/0/realdata/'
      try:
        if os.path.exists(log_root):
          for root, dirs, files in os.walk(log_root):
            for f in files:
              path = os.path.join(root, f)
              try:
                if os.getxattr(path, 'user.gd_upload') == b'1':
                  os.removexattr(path, 'user.gd_upload')
                  count += 1
              except Exception:
                pass
              try:
                if os.getxattr(path, 'user.rsync_upload') == b'1':
                  os.removexattr(path, 'user.rsync_upload')
                  count += 1
              except Exception:
                pass
      except Exception:
        pass
        
    dlg = BigConfirmationDialog("reset upload queue", "", confirm_callback=clear_flags, red=True)
    gui_app.push_widget(dlg)
