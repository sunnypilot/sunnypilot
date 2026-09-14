from opendbc.car.ford.values import FordFlags

from openpilot.selfdrive.ui.mici.layouts.settings.toggles import TogglesLayoutMici
from openpilot.selfdrive.ui.mici.widgets.button import BigParamControl, GreyBigButton
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.ui.lib.multilang import tr


class TogglesLayoutMiciSP(TogglesLayoutMici):
  def __init__(self):
    super().__init__()
    self._ford_c0_toggle = BigParamControl(tr('C0: 1 second'), 'FordC0TimeBased')
    self._ford_c0_help = GreyBigButton('', tr('off: fixed 7 m\non: 1 second, min 7 m\ndisengage 3 s to apply\nno ignition cycle'))
    self._ford_c0_toggle.set_enabled(lambda: not ui_state.engaged)
    self._scroller.add_widgets([self._ford_c0_toggle, self._ford_c0_help])
    self._refresh_toggles += (('FordC0TimeBased', self._ford_c0_toggle),)
    self._ford_c0_toggle.set_visible(False)
    self._ford_c0_help.set_visible(False)

  def _update_toggles(self):
    super()._update_toggles()
    cp = ui_state.CP
    visible = bool(cp is not None and cp.brand == 'ford' and cp.flags & FordFlags.CANFD
                   and ui_state.params.get_bool('FordModelActionController'))
    self._ford_c0_toggle.set_visible(visible)
    self._ford_c0_help.set_visible(visible)
