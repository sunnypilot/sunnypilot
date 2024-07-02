import os


SIMULATION = "SIMULATION" in os.environ


def get_model_generation(params):
  custom_model = params.get_bool("CustomDrivingModel") and not SIMULATION
  gen = int(params.get("DrivingModelGeneration", encoding="utf8"))
  return custom_model, gen
