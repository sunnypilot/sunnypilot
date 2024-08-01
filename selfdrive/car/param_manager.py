from types import SimpleNamespace

from openpilot.common.params import Params


class ParamManager:
  def __init__(self):
    self.params_list: SimpleNamespace = self.convert_to_namespace({
      "below_speed_pause": False,
      "experimental_mode": False,
      "is_metric": False,
      "pause_lateral_speed": 0,
      "reverse_dm_cam": False,
    })

  @staticmethod
  def convert_to_namespace(data: dict) -> SimpleNamespace:
    return SimpleNamespace(**data)

  def get_params(self) -> SimpleNamespace:
    return self.params_list

  def update(self, params: Params) -> None:
    self.params_list = self.convert_to_namespace({
      "below_speed_pause": params.get_bool("BelowSpeedPause"),
      "experimental_mode": params.get_bool("ExperimentalMode"),
      "is_metric": params.get_bool("IsMetric"),
      "pause_lateral_speed": int(params.get("PauseLateralSpeed", encoding="utf8")),
      "reverse_dm_cam": params.get_bool("ReverseDmCam"),
    })
