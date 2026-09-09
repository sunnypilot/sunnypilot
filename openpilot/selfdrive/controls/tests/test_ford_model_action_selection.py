"""Exercise real startup selection and Sunnylink writes without starting hardware."""
import ast
import base64
import itertools
from pathlib import Path
from types import SimpleNamespace

import pytest

from opendbc.car.ford.values import FordFlags
from openpilot.common.params import Params, ParamKeyFlag, ParamKeyType
from openpilot.selfdrive.controls.lib.ford_model_action import FordModelActionController, select_model_action_controller
from openpilot.selfdrive.controls.lib.ford_path import FordPath, FordPathController, FordPscmObserverPathController


def car_params(**overrides):
  return SimpleNamespace(**({'brand': 'ford', 'flags': FordFlags.CANFD, 'carFingerprint': 'FORD_F_150_LIGHTNING_MK1',
                             'carFw': []} | overrides))


def startup(cp=None, params=None):
  filename = Path(__file__).resolve().parents[1]/'controlsd.py'
  tree = ast.parse(filename.read_text())
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'Controls')
  body = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__').body
  start = next(i for i, n in enumerate(body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'self.ford_pscm_observer')
  end = next(i for i, n in enumerate(body) if isinstance(n, ast.Assign) and ast.unparse(n.targets[0]) == 'self.ford_path')
  if params is None:
    params = SimpleNamespace(get_bool=lambda key: key == 'FordModelActionController')
  controls = SimpleNamespace(CP=cp or car_params(), params=params)
  environment = {'self': controls, 'FordFlags': FordFlags, 'FordPath': FordPath,
                 'FordPathController': FordPathController, 'FordPscmObserverPathController': FordPscmObserverPathController,
                 'FordModelActionController': FordModelActionController,
                 'select_model_action_controller': select_model_action_controller,
                 'cloudlog': SimpleNamespace(event=lambda *args, **kwargs: None)}
  exec(compile(ast.Module(body=body[start:end+1], type_ignores=[]), str(filename), 'exec'), environment)
  return controls


@pytest.mark.parametrize('candidate,observer', list(itertools.product((False, True), repeat=2)))
def test_actual_startup_priority(candidate, observer):
  settings = {'FordModelActionController': candidate, 'FordPscmObserver': observer}
  selected = startup(params=SimpleNamespace(get_bool=settings.__getitem__))
  previous = FordPscmObserverPathController if observer else FordPathController
  expected = FordModelActionController if candidate else previous
  assert type(selected.ford_path_controller) is expected
  assert selected.ford_model_action == candidate
  assert selected.ford_path == FordPath()


@pytest.mark.parametrize('overrides', [{'brand': 'tesla'}, {'flags': 0}, {'carFingerprint': 'FORD_F_150_MK14'}])
@pytest.mark.parametrize('observer', [False, True])
def test_other_vehicles_keep_their_previous_selection(overrides, observer):
  settings = {'FordModelActionController': False, 'FordPscmObserver': observer}
  params = SimpleNamespace(get_bool=settings.__getitem__)
  before = startup(car_params(**overrides), params)
  settings['FordModelActionController'] = True
  after = startup(car_params(**overrides), params)
  assert type(after.ford_path_controller) is type(before.ford_path_controller)
  assert not after.ford_model_action


@pytest.mark.parametrize('firmware', [[], [SimpleNamespace(ecu='eps', fwVersion=b'other')]])
def test_candidate_does_not_depend_on_eps_firmware_query(firmware):
  assert isinstance(startup(car_params(carFw=firmware)).ford_path_controller, FordModelActionController)


@pytest.mark.parametrize('observer', [False, True])
def test_sunnylink_write_takes_effect_on_restart_and_restores_stored_selection(tmp_path, monkeypatch, observer):
  from openpilot.sunnypilot.sunnylink import utils

  params = Params(str(tmp_path))
  monkeypatch.setattr(utils, 'Params', lambda: params)
  assert params.get_default_value('FordModelActionController') is False
  assert params.get_type('FordModelActionController') == ParamKeyType.BOOL
  assert b'FordModelActionController' in params.all_keys(ParamKeyFlag.PERSISTENT)
  assert b'FordModelActionController' in params.all_keys(ParamKeyFlag.BACKUP)
  params.put_bool('FordPscmObserver', observer, block=True)
  old = startup(params=params)
  assert not isinstance(old.ford_path_controller, FordModelActionController)
  utils.save_param_from_base64_encoded_string('FordModelActionController', base64.b64encode(b'true').decode())
  enabled = startup(params=params)
  assert isinstance(enabled.ford_path_controller, FordModelActionController)
  assert not isinstance(old.ford_path_controller, FordModelActionController)
  utils.save_param_from_base64_encoded_string('FordModelActionController', base64.b64encode(b'false').decode())
  assert isinstance(enabled.ford_path_controller, FordModelActionController)
  assert type(startup(params=params).ford_path_controller) is type(old.ford_path_controller)
  assert params.get_bool('FordPscmObserver') == observer


def test_stored_retired_toggle_cannot_enable_the_candidate(tmp_path):
  params = Params(str(tmp_path))
  Path(params.get_param_path('FordVirtualAngleController')).write_text('1')
  assert b'FordVirtualAngleController' not in params.all_keys()
  assert params.get_bool('FordModelActionController') is False
  assert type(startup(params=params).ford_path_controller) is FordPathController
  params.put_bool('FordModelActionController', True, block=True)
  params.clear_all(ParamKeyFlag.CLEAR_ON_MANAGER_START)
  assert not Path(params.get_param_path('FordVirtualAngleController')).exists()
  assert params.get_bool('FordModelActionController') is True
