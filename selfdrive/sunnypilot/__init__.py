def get_model_generation(params):
  custom_model = params.get_bool("CustomDrivingModel")
  gen = int(params.get("DrivingModelGeneration", encoding="utf8"))
  return custom_model, gen
