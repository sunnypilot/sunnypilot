from openpilot.common.params import Params


def get_model_generation(default_gen=3):  # TODO: SP - Refactor for cleaner code/future model adoption
  params = Params()
  custom_model = params.get_bool("CustomDrivingModel")
  gen = int(params.get("DrivingModelGeneration", encoding="utf8")) or default_gen
  return custom_model, gen
