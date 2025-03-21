from opendbc.car import structs
from opendbc.sunnypilot.car.hyundai.values import HyundaiFlagsSP
from openpilot.common.params import Params


class HyundaiLongTuneParams:
    @staticmethod
    def param(params, key: str) -> bool:
        val = params.get(key)
        return val in [b"1", b"2"]


def set_hyundai_long_tune_flag(CP: structs.CarParams):
    params = Params()
    if HyundaiLongTuneParams.param(params, "HyundaiLongTune"):
        CP.flags |= HyundaiFlagsSP.HKGLONGTUNING.value
    if params.get_bool("HyundaiSmootherBraking"):
        CP.flags |= HyundaiFlagsSP.HKGLONGTUNING_BRAKING.value
