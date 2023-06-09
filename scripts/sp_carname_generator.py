import json
import os
from natsort import natsorted
from typing import Any, Dict, List

from cereal import car
from common.basedir import BASEDIR
from selfdrive.car import gen_empty_fingerprint
from selfdrive.car.car_helpers import interfaces
from selfdrive.car.docs import get_all_footnotes

UNSUPPORTED_BRANDS = ["body", "tesla"]


def get_all_car_names() -> Dict[str, str]:
  car_names = {}
  footnotes = get_all_footnotes()

  car_names["=== Not Selected ==="] = ""

  for model, car_info in get_interface_attr("CAR_INFO", combine_brands=True, exclude_brands=UNSUPPORTED_BRANDS).items():
    CP = interfaces[model][0].get_params(
      model,
      fingerprint=gen_empty_fingerprint(),
      car_fw=[car.CarParams.CarFw(ecu="unknown")],
      experimental_long=False,
      docs=True
    )

    if CP.dashcamOnly or car_info is None:
      continue

    if not isinstance(car_info, list):
      car_info = (car_info,)

    for _car_info in car_info:
      if not hasattr(_car_info, "row"):
        _car_info.init_make(CP)
        _car_info.init(CP, footnotes)
      car_names[_car_info.name] = model

  sorted_car_names = natsorted(car_names.keys(), key=lambda car: car.lower())
  return {car_name: car_names[car_name] for car_name in sorted_car_names}


def get_interface_attr(attr: str, combine_brands: bool = False, ignore_none: bool = False,
                       exclude_brands: List[str] = None) -> Dict[str, Any]:
  if exclude_brands is None:
    exclude_brands = []

  result = {}
  for car_folder in sorted([x[0] for x in os.walk(BASEDIR + '/selfdrive/car')]):
    try:
      brand_name = car_folder.split('/')[-1]

      if brand_name in exclude_brands:
        continue

      brand_values = __import__(f'selfdrive.car.{brand_name}.values', fromlist=[attr])
      if hasattr(brand_values, attr) or not ignore_none:
        attr_data = getattr(brand_values, attr, None)
      else:
        continue

      if combine_brands:
        if isinstance(attr_data, dict):
          for f, v in attr_data.items():
            result[f] = v
      else:
        result[brand_name] = attr_data
    except (ImportError, OSError):
      pass

  return result


if __name__ == "__main__":
  car_names_dict = get_all_car_names()

  with open(BASEDIR + "/selfdrive/car/sunnypilot_carname.json", "w") as json_file:
    json.dump(car_names_dict, json_file, indent=2, ensure_ascii=False)
    json_file.write('\n')
