from openpilot.common.params import Params


def get_model_generation():
  params = Params()
  custom_model = params.get_bool("CustomDrivingModel")
  gen = int(params.get("DrivingModelGeneration", encoding="utf8"))
  return custom_model, gen
