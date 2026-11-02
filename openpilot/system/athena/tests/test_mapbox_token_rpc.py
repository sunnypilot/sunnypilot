"""Exercise the credential RPC without loading device hardware dependencies."""

import ast
from contextlib import suppress
from functools import partial
import importlib.util
import json
import os
from pathlib import Path
import queue
import re
import stat
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ATHENA = Path(__file__).resolve().parents[1]
ROOT = ATHENA.parents[2]
TOKEN = 'pk.test_payload.test_signature'


def function_from_source(path, name, namespace):
  function = next(node for node in ast.parse(path.read_text()).body if isinstance(node, ast.FunctionDef) and node.name == name)
  function.decorator_list = []
  module = ast.Module(body=[*ast.parse('from __future__ import annotations').body, function], type_ignores=[])
  exec(compile(module, str(path), 'exec'), namespace)
  return namespace[name]


class TestMapboxTokenRpc(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.target = Path(self.directory.name) / 'navigation' / 'mapbox_token'
    self.namespace = {'os': os, 'tempfile': tempfile, 're': re, 'suppress': suppress, 'MAPBOX_TOKEN_PATH': str(self.target)}
    self.setter = function_from_source(ATHENA / 'athenad.py', 'setMapboxToken', self.namespace)
    spec = importlib.util.spec_from_file_location('mapbox_rpc_under_test', ATHENA / 'rpc.py')
    self.rpc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(self.rpc)

  def test_invalid_probe_never_creates_files(self):
    for token in ('', 'sk.payload.signature', 'pk.onlyonepart', 'pk.a.b c', 'pk.a.b.c', 'pk.' + 'a' * 4096 + '.b', None, 1):
      with self.subTest(token_type=type(token).__name__):
        self.assertEqual(self.setter(token), {'success': 0, 'error': 'Invalid public Mapbox token'})
        self.assertFalse(self.target.parent.exists())

  def test_private_atomic_install_and_replacement(self):
    self.assertEqual(self.setter(TOKEN), {'success': 1})
    self.assertEqual(self.target.read_text(), TOKEN)
    self.assertEqual(stat.S_IMODE(self.target.stat().st_mode), 0o600)
    self.assertEqual(stat.S_IMODE(self.target.parent.stat().st_mode), 0o700)
    self.assertEqual(self.setter('pk.new_payload.new_signature'), {'success': 1})
    self.assertEqual(self.target.read_text(), 'pk.new_payload.new_signature')
    self.assertEqual(list(self.target.parent.iterdir()), [self.target])

  def test_failed_replace_preserves_previous_token_and_sanitizes_rpc_error(self):
    self.setter(TOKEN)
    with patch.object(os, 'replace', side_effect=OSError(TOKEN)):
      response = self.rpc.handle(
        {'jsonrpc': '2.0', 'id': 1, 'method': 'setMapboxToken', 'params': {'token': 'pk.new_payload.new_signature'}}, {'setMapboxToken': self.setter}
      )
    self.assertEqual(json.loads(response)['result'], {'success': 0, 'error': 'Unable to save Mapbox token'})
    self.assertNotIn(TOKEN, response)
    self.assertEqual(self.target.read_text(), TOKEN)
    self.assertEqual(list(self.target.parent.iterdir()), [self.target])

  def test_athena_logs_method_without_credentials(self):
    end = threading.Event()
    raw = json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'setMapboxToken', 'params': {'token': TOKEN}})
    incoming = Mock()
    incoming.get.side_effect = lambda **kwargs: (end.set(), raw)[1]
    logger = Mock()
    namespace = {
      'threading': threading,
      'partial': partial,
      'startLocalProxy': Mock(),
      'dispatcher': {'setMapboxToken': self.setter},
      'recv_queue': incoming,
      'loads': self.rpc.loads,
      'is_call': self.rpc.is_call,
      'is_response': self.rpc.is_response,
      'cloudlog': logger,
      'send_queue_push': Mock(),
      'handle': self.rpc.handle,
      'SEND_PRIORITY_HIGH': 0,
      'queue': queue,
      'json': json,
    }
    function_from_source(ATHENA / 'athenad.py', 'jsonrpc_handler', namespace)(end)
    logger.event.assert_called_once_with('athena.jsonrpc_handler.call_method', method='setMapboxToken')
    self.assertNotIn(TOKEN, repr(logger.mock_calls))
    self.assertNotIn(TOKEN, namespace['send_queue_push'].call_args.args[0])

  def test_sunnylink_receives_credentials_without_logging_them(self):
    end = threading.Event()
    raw = json.dumps({'method': 'setMapboxToken', 'params': {'token': TOKEN}})
    ws = Mock()
    ws.recv_data.side_effect = lambda **kwargs: (end.set(), (1, raw.encode()))[1]
    logger = Mock()
    incoming = queue.Queue()
    namespace = {
      'time': time,
      'threading': threading,
      'ABNF': SimpleNamespace(OPCODE_TEXT=1, OPCODE_BINARY=2, OPCODE_PING=9, OPCODE_PONG=10),
      'recv_queue': incoming,
      'cloudlog': logger,
    }
    path = ROOT / 'openpilot/sunnypilot/sunnylink/athena/sunnylinkd.py'
    function_from_source(path, 'ws_recv', namespace)(ws, end)
    self.assertEqual(incoming.get_nowait(), raw)
    logger.debug.assert_called_once_with('sunnylinkd.ws_recv.received')
    self.assertNotIn(TOKEN, repr(logger.mock_calls))


if __name__ == '__main__':
  unittest.main()
