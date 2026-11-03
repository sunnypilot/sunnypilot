"""Bounded byte ranges of a public Protomaps v4 basemap; no device account.

Experimental single-device transport. Public daily-build hosting is not a fleet
backend: deployments should mirror the archive while preserving its identity.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import requests

from openpilot.common.hardware import PC
from openpilot.common.hardware.hw import Paths
from openpilot.selfdrive.navigation.pmtiles import HEADER_LENGTH

BUILD_INDEX_URL = 'https://build-metadata.protomaps.dev/builds.json'
BUILD_BASE_URL = 'https://build.protomaps.com/'
INDEX_LIMIT = 512 * 1024
MAX_RANGE = 4 * 1024 * 1024
CACHE_LIMIT = 64 * 1024 * 1024
MERGE_GAP = 256 * 1024
TIMEOUT = (5, 10)


def _build(entry):
  """Only supported official dated archives, never a URL supplied by metadata."""
  if not isinstance(entry, dict):
    return None
  key, size, version = (entry.get(name) for name in ('key', 'size', 'version'))
  if (not isinstance(key, str) or not re.fullmatch(r'\d{8}\.pmtiles', key) or
      isinstance(size, bool) or not isinstance(size, int) or not HEADER_LENGTH <= size <= 1024 ** 4 or
      not isinstance(version, str) or not re.fullmatch(r'4\.\d+\.\d+', version)):
    return None
  try:
    date(int(key[:4]), int(key[4:6]), int(key[6:8]))
  except ValueError:
    return None
  return {'key': key, 'size': size, 'version': version, 'url': BUILD_BASE_URL + key}


def _strong_etag(value):
  return isinstance(value, str) and re.fullmatch(r'"[\x21\x23-\x7e]{1,510}"', value) is not None


class RemoteTiles:
  def __init__(self):
    self.base = Path(Paths.comma_home() if PC else '/data') / 'navigation' / 'tiles'
    self.base.mkdir(parents=True, exist_ok=True, mode=0o700)
    self.session = requests.Session()
    self.url, self.etag, self.size = '', None, 0
    self.cache = None
    saved = self._saved_identity()
    try:
      try:
        build = self._latest_build()
        self.url, self.size = build['url'], build['size']
        header = self._fetch(0, HEADER_LENGTH)
        identity = build | {'etag': self.etag}
      except requests.RequestException:
        # An offline reader may reuse only a previously pinned archive with its
        # exact cached header. Missing ranges still fail; no route-only raster.
        if saved is None:
          raise
        identity = saved
        self.url, self.etag, self.size = identity['url'], identity['etag'], identity['size']
        self.cache = self._cache_for(identity)
        header = (self.cache / f'0-{HEADER_LENGTH}').read_bytes()
      if len(header) != HEADER_LENGTH or header[:8] != b'PMTiles\x03':
        raise ValueError('Invalid public PMTiles header')
      self.cache = self._cache_for(identity)
      self.cache.mkdir(parents=True, exist_ok=True)
      self._store(0, header)
      temporary = self.base / 'archive.tmp'
      temporary.write_text(json.dumps(identity))
      temporary.replace(self.base / 'archive.json')
      self._trim()
    except (requests.RequestException, OSError, ValueError, TypeError, KeyError):
      self.close()
      raise OSError('Unable to load public Protomaps basemap') from None

  def _cache_for(self, identity):
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:32]
    return self.base / 'archives' / key

  def _saved_identity(self):
    try:
      path = self.base / 'archive.json'
      if path.stat().st_size > 4096:
        return None
      saved = json.loads(path.read_text())
      build = _build(saved)
      if build is not None and saved.get('url') == build['url'] and _strong_etag(saved.get('etag')):
        return build | {'etag': saved['etag']}
    except (OSError, ValueError, TypeError):
      pass
    return None

  def _latest_build(self):
    with self.session.get(BUILD_INDEX_URL, headers={'Accept-Encoding': 'identity'}, timeout=TIMEOUT, stream=True,
                          allow_redirects=False) as response:
      response.raise_for_status()
      if response.status_code != 200:
        raise ValueError('Unexpected public build index response')
      declared = response.headers.get('Content-Length')
      if declared is not None and not 0 <= int(declared) <= INDEX_LIMIT:
        raise ValueError('Oversized public build index')
      data = bytearray()
      for chunk in response.iter_content(chunk_size=65536):
        if len(data) + len(chunk) > INDEX_LIMIT:
          raise ValueError('Oversized public build index')
        data.extend(chunk)
    entries = json.loads(data)
    if not isinstance(entries, list) or len(entries) > 4096:
      raise ValueError('Invalid public build index')
    builds = [build for entry in entries if (build := _build(entry)) is not None]
    if not builds:
      raise ValueError('No compatible public Protomaps v4 build')
    return max(builds, key=lambda build: build['key'])

  def _range(self, offset, length):
    if (isinstance(offset, bool) or isinstance(length, bool) or not isinstance(offset, int) or not isinstance(length, int) or
        offset < 0 or not 0 < length <= MAX_RANGE or offset + length > self.size):
      raise ValueError('Invalid or oversized public map range')

  def _fetch(self, offset: int, length: int) -> bytes:
    self._range(offset, length)
    headers = {'Range': f'bytes={offset}-{offset + length - 1}', 'Accept-Encoding': 'identity'}
    if self.etag is not None:
      headers['If-Match'] = self.etag
    with self.session.get(self.url, headers=headers, timeout=TIMEOUT, stream=True, allow_redirects=False) as response:
      response.raise_for_status()
      if response.status_code != 206:
        raise OSError(f'Public map range request failed ({response.status_code})')
      match = re.fullmatch(r'bytes (\d+)-(\d+)/(\d+)', response.headers.get('Content-Range', ''))
      if match is None or tuple(map(int, match.groups())) != (offset, offset + length - 1, self.size):
        raise OSError('Invalid public map range response')
      etag = response.headers.get('ETag')
      if not _strong_etag(etag) or (self.etag is not None and etag != self.etag):
        raise OSError('Public map archive changed during read')
      declared = response.headers.get('Content-Length')
      if declared is not None and int(declared) != length:
        raise OSError('Invalid public map range length')
      if response.headers.get('Content-Encoding', 'identity') != 'identity':
        raise OSError('Encoded public map range response')
      data = bytearray()
      for chunk in response.iter_content(chunk_size=min(length + 1, 65536)):
        if len(data) + len(chunk) > length:
          raise OSError('Oversized public map range response')
        data.extend(chunk)
      if len(data) != length:
        raise OSError('Truncated public map range response')
      self.etag = etag
      return bytes(data)

  def _store(self, offset: int, data: bytes):
    path = self.cache / f'{offset}-{len(data)}'
    temporary = path.with_suffix('.tmp')
    temporary.write_bytes(data)
    temporary.replace(path)

  def _trim(self):
    files = [(cached.stat().st_mtime, cached.stat().st_size, cached) for cached in self.base.rglob('*')
             if cached.is_file() and re.fullmatch(r'\d+-\d+', cached.name)]
    size = sum(cached_size for _, cached_size, _ in files)
    for _, cached_size, cached in sorted(files):
      if size <= CACHE_LIMIT:
        break
      if cached == self.cache / f'0-{HEADER_LENGTH}':
        continue  # Required for an offline restart of the current pinned archive.
      cached.unlink(missing_ok=True)
      size -= cached_size

  def read(self, offset: int, length: int) -> bytes:
    self._range(offset, length)
    try:
      data = (self.cache / f'{offset}-{length}').read_bytes()
      if len(data) == length:
        return data
    except FileNotFoundError:
      pass
    try:
      data = self._fetch(offset, length)
    except (requests.RequestException, ValueError):
      raise OSError('Unable to fetch public map tiles') from None
    self._store(offset, data)
    self._trim()
    return data

  def prefetch(self, ranges):
    missing = []
    for offset, length in sorted(set(ranges)):
      self._range(offset, length)
      if not (self.cache / f'{offset}-{length}').exists():
        missing.append((offset, length))
    if not missing:
      return
    groups = [[missing[0]]]
    for offset, length in missing[1:]:
      start = groups[-1][0][0]
      last_offset, last_length = groups[-1][-1]
      if offset - (last_offset + last_length) <= MERGE_GAP and offset + length - start <= MAX_RANGE:
        groups[-1].append((offset, length))
      else:
        groups.append([(offset, length)])
    for group in groups:
      start, end = group[0][0], max(offset + length for offset, length in group)
      try:
        data = self._fetch(start, end - start)
      except (requests.RequestException, ValueError):
        raise OSError('Unable to prefetch public map tiles') from None
      for offset, length in group:
        self._store(offset, data[offset - start:offset - start + length])
    self._trim()

  def close(self):
    self.session.close()
