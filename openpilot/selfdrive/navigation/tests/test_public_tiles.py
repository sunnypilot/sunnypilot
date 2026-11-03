"""Actual public tile client requests and cache behavior, without accounts/network."""
import ast
import io
import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

import requests
from requests.adapters import BaseAdapter
from requests.structures import CaseInsensitiveDict

SOURCE = Path(__file__).resolve().parents[1]
REAL_SESSION = requests.Session


class PublicServer(BaseAdapter):
  def __init__(self):
    self.archive = b'PMTiles\x03' + bytes(range(256)) * 64
    self.entries = [{'key': '20261103.pmtiles', 'version': '4.15.2', 'size': len(self.archive)}]
    self.etag = '"public-build"'
    self.calls = []
    self.offline = False
    self.index_bytes = None
    self.index_headers = {}
    self.range_headers = {}
    self.range_status = 206
    self.range_body = None

  def send(self, request, **_kwargs):
    self.calls.append(request)
    if self.offline:
      raise requests.ConnectionError('fixture network unavailable')
    response = requests.Response()
    response.request, response.url = request, request.url
    if request.url == 'https://build-metadata.protomaps.dev/builds.json':
      body = self.index_bytes if self.index_bytes is not None else json.dumps(self.entries).encode()
      response.status_code = 200
      headers = {'Content-Length': str(len(body))} | self.index_headers
    else:
      if not re.fullmatch(r'https://build\.protomaps\.com/\d{8}\.pmtiles', request.url):
        raise AssertionError('Client must never contact an account or arbitrary endpoint')
      match = re.fullmatch(r'bytes=(\d+)-(\d+)', request.headers['Range'])
      start, end = map(int, match.groups())
      body = self.archive[start:end + 1] if self.range_body is None else self.range_body
      response.status_code = self.range_status
      headers = {'Content-Range': f'bytes {start}-{end}/{len(self.archive)}', 'ETag': self.etag,
                 'Content-Length': str(len(body))} | self.range_headers
    response.headers = CaseInsensitiveDict(headers)
    response.raw = io.BytesIO(body)
    return response

  def close(self):
    pass


class PublicTilesTests(unittest.TestCase):
  def setUp(self):
    self.temp = tempfile.TemporaryDirectory()
    self.addCleanup(self.temp.cleanup)
    self.home = Path(self.temp.name)
    dependencies = {'openpilot.common.hardware': NS(PC=True),
                    'openpilot.common.hardware.hw': NS(Paths=NS(comma_home=lambda: self.temp.name)),
                    'openpilot.selfdrive.navigation.pmtiles': NS(HEADER_LENGTH=127)}
    spec = importlib.util.spec_from_file_location('actual_public_tiles', SOURCE / 'tiles.py')
    self.tiles = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, dependencies):
      spec.loader.exec_module(self.tiles)
    self.server = PublicServer()
    def session():
      value = REAL_SESSION()
      value.trust_env = False
      value.mount('https://', self.server)
      return value
    self.enterContext(patch.object(self.tiles.requests, 'Session', side_effect=session))

  def client(self):
    value = self.tiles.RemoteTiles()
    self.addCleanup(value.close)
    return value

  def ranges(self):
    return [call for call in self.server.calls if 'Range' in call.headers]

  def test_latest_compatible_public_build_has_no_account_or_token_dependency(self):
    self.server.entries += [{'key': '20261104.pmtiles', 'version': '5.0.0', 'size': len(self.server.archive)},
                            {'key': '20261102.pmtiles', 'version': '4.99.1', 'size': len(self.server.archive)}]
    client = self.client()
    self.assertEqual(client.url, 'https://build.protomaps.com/20261103.pmtiles')
    self.assertEqual(client.read(300, 100), self.server.archive[300:400])
    self.assertEqual(self.ranges()[-1].headers['If-Match'], self.server.etag)
    for call in self.server.calls:
      self.assertNotIn('Authorization', call.headers)
      self.assertNotIn('access_token', call.url)
      self.assertNotIn('comma', call.url)
    imported = [ast.unparse(node) for node in ast.parse((SOURCE / 'tiles.py').read_text()).body if isinstance(node, (ast.Import, ast.ImportFrom))]
    self.assertFalse(any('api' in value.lower() or 'params' in value.lower() for value in imported))

  def test_invalid_index_or_unsupported_schema_fails_before_archive_request(self):
    invalid = ({'url': 'https://untrusted.invalid/archive'}, [],
               [{'key': '../20261103.pmtiles', 'version': '4.15.2', 'size': 200}],
               [{'key': '20260230.pmtiles', 'version': '4.15.2', 'size': 200}],
               [{'key': '20261103.pmtiles', 'version': '5.0.0', 'size': 200}],
               [{'key': '20261103.pmtiles', 'version': '4.15.2', 'size': True}])
    for value in invalid:
      with self.subTest(value=value):
        self.server.entries = value
        with self.assertRaises(OSError):
          self.client()
    self.assertEqual(self.ranges(), [])
    self.server.index_bytes = b'not JSON'
    with self.assertRaises(OSError):
      self.client()

  def test_index_body_and_declared_length_are_bounded(self):
    self.server.index_headers = {'Content-Length': str(self.tiles.INDEX_LIMIT + 1)}
    with self.assertRaises(OSError):
      self.client()
    self.server.index_headers = {}
    self.server.index_bytes = b' ' * (self.tiles.INDEX_LIMIT + 1)
    with self.assertRaises(OSError):
      self.client()
    self.assertEqual(self.ranges(), [])

  def test_range_status_identity_length_and_content_range_fail_closed(self):
    cases = [({'status': 200}), ({'headers': {'Content-Range': 'bytes 1-127/999'}}),
             ({'headers': {'ETag': ''}}), ({'headers': {'ETag': 'W/"weak"'}}),
             ({'headers': {'Content-Length': '99999999999999'}}),
             ({'headers': {'Content-Encoding': 'gzip'}}),
             ({'body': b'x' * 126, 'headers': {'Content-Length': '127'}}),
             ({'body': b'x' * 128, 'headers': {'Content-Length': '127'}})]
    for case in cases:
      with self.subTest(case=case):
        self.server.range_status = case.get('status', 206)
        self.server.range_headers = case.get('headers', {})
        self.server.range_body = case.get('body')
        with self.assertRaises(OSError):
          self.client()

  def test_archive_cannot_change_etag_or_total_size_mid_reader(self):
    client = self.client()
    self.server.etag = '"changed"'
    with self.assertRaisesRegex(OSError, 'changed'):
      client.read(200, 100)
    self.assertFalse((client.cache / '200-100').exists())
    self.server.etag = client.etag
    self.server.range_headers = {'Content-Range': f'bytes 200-299/{client.size + 1}'}
    with self.assertRaises(OSError):
      client.read(200, 100)

  def test_restart_revalidates_header_and_reuses_only_same_archive_ranges(self):
    first = self.client()
    first.read(200, 100)
    count = len(self.server.calls)
    second = self.client()
    self.assertEqual(second.cache, first.cache)
    self.assertEqual(second.read(200, 100), self.server.archive[200:300])
    self.assertEqual(len(self.server.calls), count + 2)  # build index and pinned header only
    self.server.entries[0]['key'] = '20261104.pmtiles'
    third = self.client()
    self.assertNotEqual(third.cache, first.cache)
    count = len(self.server.calls)
    third.read(200, 100)
    self.assertEqual(len(self.server.calls), count + 1)

  def test_offline_restart_reuses_pinned_header_and_cached_ranges_only(self):
    first = self.client()
    first.read(200, 100)
    self.server.offline = True
    second = self.client()
    self.assertEqual(second.url, first.url)
    self.assertEqual(second.etag, first.etag)
    self.assertEqual(second.read(200, 100), self.server.archive[200:300])
    with self.assertRaises(OSError):
      second.read(500, 100)

  def test_malformed_fresh_index_does_not_fall_back_or_relabel_old_bytes(self):
    first = self.client()
    first.read(200, 100)
    self.server.entries = []
    with self.assertRaises(OSError):
      self.client()
    self.assertEqual(first.read(200, 100), self.server.archive[200:300])

  def test_prefetch_merges_nearby_ranges_but_caps_every_request(self):
    client = self.client()
    with patch.object(self.tiles, 'MAX_RANGE', 64):
      count = len(self.ranges())
      client.prefetch([(200, 32), (244, 32), (400, 16), (400, 16)])
      added = self.ranges()[count:]
      self.assertEqual(len(added), 3)
      for call in added:
        start, end = map(int, call.headers['Range'][6:].split('-'))
        self.assertLessEqual(end - start + 1, 64)
      count = len(self.server.calls)
      self.assertEqual(client.read(244, 32), self.server.archive[244:276])
      self.assertEqual(len(self.server.calls), count)
    count = len(self.ranges())
    client.prefetch([(600, 10), (620, 10)])
    self.assertEqual(len(self.ranges()), count + 1)

  def test_cache_limit_counts_ranges_from_all_archive_identities(self):
    client = self.client()
    with patch.object(self.tiles, 'CACHE_LIMIT', 160):
      client.read(200, 100)
      total = sum(path.stat().st_size for path in client.base.rglob('*') if path.is_file() and re.fullmatch(r'\d+-\d+', path.name))
      self.assertLessEqual(total, 160)

  def test_cache_trim_retains_current_header_for_offline_restart(self):
    first = self.client()
    with patch.object(self.tiles, 'CACHE_LIMIT', 228):
      first.read(200, 100)
      first.read(400, 100)
      self.assertTrue((first.cache / '0-127').exists())
      self.assertFalse((first.cache / '200-100').exists())
      self.server.offline = True
      second = self.client()
      self.assertEqual(second.read(400, 100), self.server.archive[400:500])

  def test_invalid_or_excessive_ranges_do_not_make_requests(self):
    client = self.client()
    count = len(self.server.calls)
    for offset, length in ((-1, 1), (0, 0), (0, self.tiles.MAX_RANGE + 1), (client.size, 1), (True, 1)):
      with self.subTest(offset=offset, length=length), self.assertRaises(ValueError):
        client.read(offset, length)
    self.assertEqual(len(self.server.calls), count)


if __name__ == '__main__':
  unittest.main()
