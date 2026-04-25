from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigMultiParamToggle, BigParamControl
from openpilot.selfdrive.ui.mici.widgets.dialog import BigInputDialog, BigConfirmationDialog
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
      "upload provider", 
      "DashcamUploaderProvider", 
      ["none", "syncthing", "google drive", "rsync"],
      select_callback=self._on_provider_changed
    )

    # Delete Toggle (Global)
    self._delete_synced_toggle = BigParamControl("delete source after upload", "DashcamUploaderDeleteSynced")

    # Sync Connection Toggle
    self._sync_mode_toggle = BigMultiParamToggle(
      "sync connection", 
      "DashcamUploaderSyncMode", 
      ["off", "wifi-only", "wifi+lte"]
    )

    # Video Mode Toggle
    self._video_mode_toggle = BigMultiParamToggle(
      "video upload",
      "DashcamUploaderVideoMode",
      ["off", "low-res", "high-res"]
    )

    # Upload Logs
    self._upload_logs_toggle = BigParamControl("upload logs", "DashcamUploaderUploadLogs")

    # Syncthing Widgets
    self._st_url_btn = BigButton("syncthing url")
    self._st_url_btn.set_click_callback(self._edit_st_url)
    
    self._st_key_btn = BigButton("syncthing api key")
    self._st_key_btn.set_click_callback(self._edit_st_key)

    st_path = "/data/syncthing/syncthing"
    btn_text = "uninstall local syncthing" if __import__('os').path.exists(st_path) else "install local syncthing"
    self._st_install_btn = BigButton(btn_text, "auto setup")
    self._st_install_btn.set_click_callback(self._prompt_st_install)

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

    self._scroller.add_widgets([
      self._provider_toggle,
      self._sync_mode_toggle,
      self._video_mode_toggle,
      self._upload_logs_toggle,
      self._delete_synced_toggle,
      self._st_install_btn,
      self._st_url_btn,
      self._st_key_btn,
      self._gdrive_auth_btn,
      self._gdrive_folder_btn,
      self._rsync_target_btn,
      self._rsync_key_btn
    ])

    self._update_visibility()

  def _update_visibility(self):
    val = self._params.get("DashcamUploaderProvider")
    # "0": none, "1": syncthing, "2": google drive
    idx = 0
    if val is not None:
      try:
        idx = int(val)
      except Exception:
        pass
        
    is_st = (idx == 1)
    is_gd = (idx == 2)
    is_rs = (idx == 3)

    self._sync_mode_toggle.set_visible(idx > 0)
    self._video_mode_toggle.set_visible(idx > 0)
    self._upload_logs_toggle.set_visible(idx > 0)
    self._delete_synced_toggle.set_visible(idx > 0)
    
    self._st_url_btn.set_visible(is_st)
    self._st_key_btn.set_visible(is_st)
    self._st_install_btn.set_visible(is_st)
    
    self._gdrive_auth_btn.set_visible(is_gd)
    self._gdrive_folder_btn.set_visible(is_gd)
    
    self._rsync_target_btn.set_visible(is_rs)
    self._rsync_key_btn.set_visible(is_rs)

  def _on_provider_changed(self, value: str):
    self._update_visibility()

  def _edit_st_url(self):
    current = self._params.get("DashcamUploaderSTUrl") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderSTUrl", val)
    dlg = BigInputDialog("enter syncthing url...", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _edit_st_key(self):
    current = self._params.get("DashcamUploaderSTKey") or b""
    if type(current) is bytes:
      current = current.decode('utf8')
    def update(val: str):
      self._params.put("DashcamUploaderSTKey", val)
    dlg = BigInputDialog("enter syncthing api key...", current, minimum_length=0, confirm_callback=update)
    gui_app.push_widget(dlg)

  def _prompt_st_install(self):
    import os
    st_path = "/data/syncthing/syncthing"
    is_installed = os.path.exists(st_path)

    if is_installed:
      def run_uninstall():
        import shutil
        try:
          shutil.rmtree("/data/syncthing")
        except Exception as e:
          print(f"Uninstall failed: {e}")
        self._st_install_btn.set_text("install local syncthing")
        gui_app.pop_widget()

      txt_icon = gui_app.texture("icons_mici/settings/developer_icon.png", 64, 60)
      dlg = BigConfirmationDialog("uninstall syncthing?", txt_icon, run_uninstall, red=True)
      gui_app.push_widget(dlg)
    else:
      def run_install():
        import threading
        import requests
        import tarfile
        import io
        import stat

        def _installer_thread():
          print("Starting Syncthing download...")
          try:
            url = "https://github.com/syncthing/syncthing/releases/download/v1.27.6/syncthing-linux-arm64-v1.27.6.tar.gz"
            r = requests.get(url, stream=True, timeout=30)
            
            os.makedirs("/data/syncthing", exist_ok=True)
            with tarfile.open(fileobj=io.BytesIO(r.content), mode="r:gz") as tar:
              for member in tar.getmembers():
                if member.name.endswith("/syncthing") and member.isfile():
                  member.name = "syncthing"  # Flatten to drop parent directories
                  tar.extract(member, path="/data/syncthing")
                  
            # Ensure the binary is executable
            if os.path.exists(st_path):
              os.chmod(st_path, os.stat(st_path).st_mode | stat.S_IEXEC)
              print("Syncthing installed successfully to /data/syncthing/syncthing")
              
              # Schedule a UI update from the main thread (optional: for immediate text refresh)
              # On next settings opening, it will be refreshed anyway.
          except Exception as e:
            print(f"Failed to install Syncthing: {e}")

        # Run the download in a background thread to avoid freezing the UI
        threading.Thread(target=_installer_thread, daemon=True).start()
        gui_app.pop_widget()

      txt_icon = gui_app.texture("icons_mici/settings/developer_icon.png", 64, 60)
      dlg = BigConfirmationDialog("install syncthing?", txt_icon, run_install, red=False)
      gui_app.push_widget(dlg)

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
