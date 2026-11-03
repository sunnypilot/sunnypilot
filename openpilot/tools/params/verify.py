"""Run the actual Params C/Python API in the isolated ARM64 Linux builder.

Only the project's cloud logger and test-root fixture are replaced. The Params
implementation and original test method bodies are executed unchanged.
"""
import ast
import datetime
import gc
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import types
import unittest
import uuid


def run():
  root = Path('/build')
  shutil.copyfile(root / 'openpilot/common/params.py', root / 'out/params.py')
  logger = types.ModuleType('openpilot.common.swaglog')
  logger.cloudlog = types.SimpleNamespace(warning=lambda *args, **kwargs: None)
  sys.modules[logger.__name__] = logger
  spec = importlib.util.spec_from_file_location('isolated_native_params', root / 'out/params.py')
  native = importlib.util.module_from_spec(spec)
  spec.loader.exec_module(native)
  namespace = {'__name__': 'original_params_tests', 'datetime': datetime, 'os': os, 'threading': threading,
               'time': time, 'uuid': uuid, 'OpenpilotTestCase': unittest.TestCase, 'Params': native.Params,
               'ParamKeyFlag': native.ParamKeyFlag, 'UnknownKeyName': native.UnknownKeyName}
  tree = ast.parse((root / 'openpilot/common/tests/test_params.py').read_text())
  tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))]
  exec(compile(tree, 'original_test_params.py', 'exec'), namespace)
  cls = namespace['TestParams']
  original_tests = []
  for name in sorted(name for name in vars(cls) if name.startswith('test_')):
    with tempfile.TemporaryDirectory() as directory:
      os.environ['PARAMS_ROOT'], os.environ['OPENPILOT_PREFIX'] = directory, 'native-test'
      case = cls(name)
      case.setup_method()
      getattr(case, name)()
      case.params._finalizer()
      original_tests.append(name)
      gc.collect()
  tree = ast.parse((root / 'openpilot/common/tests/test_params_flag_buffers.py').read_text())
  tree.body = [node for node in tree.body if not (isinstance(node, ast.ImportFrom) and node.module == 'openpilot.common')]
  namespace = {'__name__': 'flag_buffer_tests', 'native': native}
  exec(compile(tree, 'test_params_flag_buffers.py', 'exec'), namespace)
  result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(namespace['TestParamsFlagBuffers']))
  if not result.wasSuccessful():
    raise RuntimeError('Native flag-buffer tests failed')
  events = ['MapboxTurnIntent', 'MapboxTurnContext', 'MapboxTurnCue']
  with tempfile.TemporaryDirectory() as directory:
    params = native.Params(directory)
    expected = {'MapboxNextTurnEnabled': ('BOOL', False), 'MapboxTurnLeadDistance': ('FLOAT', 20.0),
                **dict.fromkeys(events + ['NavModelState'], ('JSON', None))}
    assert {key: (params.get_type(key).name, params.get_default_value(key)) for key in expected} == expected
    params.put_bool('MapboxNextTurnEnabled', True, block=True)
    params.put('MapboxTurnLeadDistance', 20., block=True)
    for flag in (native.ParamKeyFlag.CLEAR_ON_MANAGER_START, native.ParamKeyFlag.CLEAR_ON_ONROAD_TRANSITION):
      for key in events:
        params.put(key, {'session': 'native-test'}, block=True)
        assert params.get(key) == {'session': 'native-test'}
      params.clear_all(flag)
      assert all(params.get(key) is None for key in events)
      assert params.get_bool('MapboxNextTurnEnabled') is True
      assert params.get('MapboxTurnLeadDistance') == 20.
    for flag in (native.ParamKeyFlag.CLEAR_ON_MANAGER_START, native.ParamKeyFlag.CLEAR_ON_OFFROAD_TRANSITION):
      params.put('NavModelState', {'supported': True, 'active': False}, block=True)
      assert params.get('NavModelState') == {'supported': True, 'active': False}
      params.clear_all(flag)
      assert params.get('NavModelState') is None
    params.put(events[0], {'session': 'async-test'}, block=False)
    deadline = time.monotonic() + 2.
    while params.get(events[0]) != {'session': 'async-test'} and time.monotonic() < deadline:
      time.sleep(.01)
    assert params.get(events[0]) == {'session': 'async-test'}
    params._finalizer()
  library = root / 'out/libparams_c.so'
  symbols = subprocess.check_output(['readelf', '--dyn-syms', '--wide', str(library)], text=True)
  strings = subprocess.check_output(['strings', str(library)], text=True)
  versions = {tag: max(set(re.findall(tag + r'_([0-9.]+)', strings)), key=lambda value: tuple(map(int, value.split('.'))))
              for tag in ('GLIBC', 'GLIBCXX', 'CXXABI')}
  ceilings = {'GLIBC': '2.38', 'GLIBCXX': '3.4.30', 'CXXABI': '1.3.13'}
  assert all(tuple(map(int, versions[tag].split('.'))) <= tuple(map(int, value.split('.'))) for tag, value in ceilings.items())
  dynamic = subprocess.check_output(['readelf', '-d', str(library)], text=True)
  report = {'originalTestMethods': original_tests, 'originalTestCount': len(original_tests),
            'flagBufferTestCount': result.testsRun, 'newKeysTypedRoundTrip': True,
            'lifecycleClears': True, 'asynchronousJson': True, 'maxSymbolVersions': versions,
            'needed': re.findall(r'\(NEEDED\).*\[([^]]+)\]', dynamic),
            'cApi': sorted(set(re.findall(r'\b(params_[a-z_]+)\s*$', symbols, re.M))),
            'hardwareExecuted': False}
  (root / 'out/verification.json').write_text(json.dumps(report, indent=2) + '\n')
  print(json.dumps(report))


if __name__ == '__main__':
  run()
