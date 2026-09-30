import time

from openpilot.selfdrive.ui.mici.widgets.button import BigButton, BigParamControl
from openpilot.selfdrive.ui.mici.widgets.dialog import BigConfirmationDialog
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.sunnypilot.sunnydrive import pairing
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.widgets.scroller import NavScroller


class SunnydriveLayoutMici(NavScroller):
  def __init__(self):
    super().__init__()
    self._pending_id = ""
    self._prompted_id = ""
    self._approval_dialog = None
    self._opened_for_prompt = False
    self._next_prompt_check = 0.0
    self._enable = BigParamControl("enabled", "SunnydriveEnabled")
    self._pairing_prompts = BigParamControl("allow pairing", "SunnydriveAutoPairPrompt")
    self._unpair = BigButton("paired phones", "none")
    self._unpair.set_click_callback(self._confirm_unpair_all)
    self._scroller.add_widgets([self._enable, self._pairing_prompts, self._unpair])
    gui_app.add_nav_stack_tick(self._pairing_tick)

  def _update_state(self):
    super()._update_state()
    self._enable.refresh()
    self._pairing_prompts.refresh()
    requests = pairing.pairing_requests()
    pending = next(((request_id, request) for request_id, request in reversed(list(requests.items())) if request.get("status") == "pending"), None)
    self._pending_id = pending[0] if pending else ""
    count = len(pairing.paired_clients())
    self._unpair.set_value(f"{count} paired" if count else "none")
    self._unpair.set_visible(count > 0)

  def _pairing_tick(self):
    if time.monotonic() < self._next_prompt_check:
      return
    self._next_prompt_check = time.monotonic() + 0.5
    if not ui_state.params.get_bool("SunnydriveAutoPairPrompt"):
      return
    requests = reversed(list(pairing.pairing_requests().items()))
    pending = next(((request_id, request) for request_id, request in requests if request.get("status") == "pending"), None)
    answered = not pending or pending[0] == self._prompted_id   # approved, expired, or its slide was dismissed
    if self._opened_for_prompt and answered and gui_app.get_active_widget() is self:   # back to whatever was showing
      self._opened_for_prompt = False
      self.dismiss()
    if pending and self._prompted_id != pending[0]:
      self._pending_id = self._prompted_id = pending[0]
      if self._approval_dialog and gui_app.widget_in_stack(self._approval_dialog):
        self._approval_dialog.dismiss(self._confirm_pending)
      else:
        self._confirm_pending()

  def _confirm_pending(self):
    if not self._pending_id or (self._approval_dialog and gui_app.widget_in_stack(self._approval_dialog)):
      return
    request_id = self._pending_id
    icon = gui_app.texture("icons_mici/settings/device/pair.png", 64, 64)
    if not gui_app.widget_in_stack(self):
      # The screen right under a dialog keeps handling touches, and onroad that's the driving view,
      # whose swipe-left bookmark is the same gesture as this slider. Showing this panel underneath keeps it out.
      gui_app.push_widget(self)
      self._opened_for_prompt = True
    self._approval_dialog = BigConfirmationDialog("slide to approve phone", icon, lambda: pairing.approve_request(request_id))
    gui_app.push_widget(self._approval_dialog)

  def _confirm_unpair_all(self):
    icon = gui_app.texture("icons_mici/settings/network/new/trash.png", 54, 64)
    gui_app.push_widget(BigConfirmationDialog("slide to unpair all phones", icon, lambda: pairing.unpair(), red=True))
