"""
Copyright (c) 2026-, Zeph Leggett.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from openpilot.sunnypilot.accelerators.jetlink import lfs

BODY = b'onnx' * 4096
OID = hashlib.sha256(BODY).hexdigest()
SIZE = len(BODY)

POINTER = f"""version https://git-lfs.github.com/spec/v1
oid sha256:{OID}
size {SIZE}
"""


class FakeResponse:
  def __init__(self, payload: bytes):
    self._payload = payload
    self._pos = 0

  def read(self, n=None):
    if n is None:
      n, self._pos = len(self._payload) - self._pos, len(self._payload)
      return self._payload[-n:] if n else b''
    chunk = self._payload[self._pos:self._pos + n]
    self._pos += len(chunk)
    return chunk

  def __enter__(self):
    return self

  def __exit__(self, *_):
    return False


class TestParsePointer(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())

  def write(self, name: str, data) -> Path:
    path = self.tmp / name
    path.write_bytes(data if isinstance(data, bytes) else data.encode())
    return path

  def test_reads_oid_and_size(self):
    assert lfs.parse_pointer(self.write('p', POINTER)) == (OID, SIZE)

  def test_a_real_object_is_not_a_pointer(self):
    # The worktree holds the object once it has been fetched, and it must not
    # be mistaken for something still to download.
    assert lfs.parse_pointer(self.write('big', b'\0' * 8192)) is None

  def test_binary_that_is_small_is_not_a_pointer(self):
    assert lfs.parse_pointer(self.write('junk', b'\x00\x01\x02')) is None

  def test_missing_file_is_not_a_pointer(self):
    assert lfs.parse_pointer(self.tmp / 'absent') is None

  def test_incomplete_pointer_is_rejected(self):
    assert lfs.parse_pointer(self.write('p', 'version x\noid sha256:abc\n')) is None

  def test_non_numeric_size_is_rejected(self):
    assert lfs.parse_pointer(self.write('p', f'oid sha256:{OID}\nsize huge\n')) is None


class TestEndpoints(unittest.TestCase):
  def setUp(self):
    self.root = Path(tempfile.mkdtemp())

  def test_configured_endpoint_comes_first(self):
    (self.root / '.lfsconfig').write_text('[lfs]\n\turl = https://example.com/info/lfs\n')
    assert lfs.endpoints(self.root) == ['https://example.com/info/lfs', lfs.COMMA_LFS]

  def test_commas_endpoint_is_always_there(self):
    # sunnypilot substitutes its own big model, but comma's server is still the
    # only one that has comma's.
    assert lfs.endpoints(self.root) == [lfs.COMMA_LFS]

  def test_no_duplicate_when_already_commas(self):
    (self.root / '.lfsconfig').write_text(f'[lfs]\n\turl = {lfs.COMMA_LFS}\n')
    assert lfs.endpoints(self.root) == [lfs.COMMA_LFS]


class TestResolve(unittest.TestCase):
  def urlopen_returning(self, payload: dict):
    return mock.patch.object(lfs.urllib.request, 'urlopen',
                             return_value=FakeResponse(json.dumps(payload).encode()))

  def test_returns_the_href(self):
    with self.urlopen_returning({'objects': [{'oid': OID, 'actions': {'download': {'href': 'https://x/y'}}}]}):
      assert lfs.resolve('https://e/info/lfs', OID, SIZE) == 'https://x/y'

  def test_an_error_object_is_a_miss_not_a_raise(self):
    with self.urlopen_returning({'objects': [{'oid': OID, 'error': {'code': 404, 'message': 'nope'}}]}):
      assert lfs.resolve('https://e/info/lfs', OID, SIZE) is None

  def test_a_different_oid_is_a_miss(self):
    with self.urlopen_returning({'objects': [{'oid': 'deadbeef', 'actions': {'download': {'href': 'https://x/y'}}}]}):
      assert lfs.resolve('https://e/info/lfs', OID, SIZE) is None

  def test_a_dead_server_is_a_miss_not_a_raise(self):
    # One unreachable endpoint must not stop us asking the next.
    with mock.patch.object(lfs.urllib.request, 'urlopen', side_effect=OSError('refused')):
      assert lfs.resolve('https://e/info/lfs', OID, SIZE) is None


class TestDownload(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.dest = self.tmp / 'big.onnx'

  def urlopen_returning(self, payload: bytes):
    return mock.patch.object(lfs.urllib.request, 'urlopen', return_value=FakeResponse(payload))

  def test_writes_and_verifies(self):
    with self.urlopen_returning(BODY):
      assert lfs.download('https://x/y', OID, SIZE, self.dest) == self.dest
    assert self.dest.read_bytes() == BODY

  def test_a_corrupt_body_leaves_nothing_behind(self):
    # half a model that TensorRT would try to parse is the one outcome worth being paranoid about
    corrupt = b'x' * SIZE
    with self.urlopen_returning(corrupt), self.assertRaises(lfs.LfsError):
      lfs.download('https://x/y', OID, SIZE, self.dest)
    assert not self.dest.exists()
    assert not list(self.tmp.glob('*.part'))

  def test_a_short_body_leaves_nothing_behind(self):
    with self.urlopen_returning(BODY[:100]), self.assertRaises(lfs.LfsError):
      lfs.download('https://x/y', OID, SIZE, self.dest)
    assert not self.dest.exists()
    assert not list(self.tmp.glob('*.part'))

  def test_stopping_leaves_nothing_behind(self):
    with self.urlopen_returning(BODY), self.assertRaises(lfs.LfsError):
      lfs.download('https://x/y', OID, SIZE, self.dest, should_stop=lambda: True)
    assert not list(self.tmp.glob('*.part'))

  def test_refuses_without_room(self):
    with mock.patch.object(lfs.shutil, 'disk_usage') as usage:
      usage.return_value = mock.Mock(free=1024)
      with self.assertRaises(lfs.LfsError):
        lfs.download('https://x/y', OID, 1 << 30, self.dest)

  def test_progress_reaches_one(self):
    seen = []
    with self.urlopen_returning(BODY):
      lfs.download('https://x/y', OID, SIZE, self.dest, progress=seen.append)
    assert seen and seen[-1] == 1.0
    assert seen == sorted(seen)


class TestFetch(unittest.TestCase):
  def setUp(self):
    self.tmp = Path(tempfile.mkdtemp())
    self.pointer = self.tmp / 'big.onnx'
    self.dest = self.tmp / 'out.onnx'

  def test_a_real_object_needs_no_fetch(self):
    self.pointer.write_bytes(b'\0' * 8192)
    assert lfs.fetch(self.pointer, self.dest, self.tmp) is None

  def test_already_fetched_is_returned_as_is(self):
    self.pointer.write_text(POINTER)
    self.dest.write_bytes(BODY)
    with mock.patch.object(lfs, 'resolve') as resolve:
      assert lfs.fetch(self.pointer, self.dest, self.tmp) == self.dest
      resolve.assert_not_called()

  def test_falls_through_to_the_next_endpoint(self):
    self.pointer.write_text(POINTER)
    (self.tmp / '.lfsconfig').write_text('[lfs]\n\turl = https://dead.example/info/lfs\n')
    with mock.patch.object(lfs, 'resolve', side_effect=[None, 'https://x/y']) as resolve, \
         mock.patch.object(lfs.urllib.request, 'urlopen', return_value=FakeResponse(BODY)):
      assert lfs.fetch(self.pointer, self.dest, self.tmp) == self.dest
    assert [call.args[0] for call in resolve.call_args_list] == ['https://dead.example/info/lfs', lfs.COMMA_LFS]

  def test_nowhere_to_get_it_raises(self):
    self.pointer.write_text(POINTER)
    with mock.patch.object(lfs, 'resolve', return_value=None), self.assertRaises(lfs.LfsError):
      lfs.fetch(self.pointer, self.dest, self.tmp)


if __name__ == '__main__':
  unittest.main()
