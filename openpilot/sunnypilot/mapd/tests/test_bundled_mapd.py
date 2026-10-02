import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openpilot.sunnypilot.mapd import mapd_installer


class TestBundledMapd(unittest.TestCase):
  def setUp(self):
    self.directory = tempfile.TemporaryDirectory()
    self.addCleanup(self.directory.cleanup)
    self.root = Path(self.directory.name)
    self.binary = self.root / 'mapd'
    self.binary.write_bytes(b'bundled producer')
    self.hash_path = self.root / 'openpilot/sunnypilot/mapd/tests/mapd_hash'
    self.hash_path.parent.mkdir(parents=True)
    self.hash_path.write_text(hashlib.sha256(self.binary.read_bytes()).hexdigest())
    self.manager = mapd_installer.MapdInstallManager.__new__(mapd_installer.MapdInstallManager)
    self.manager._params = object()
    self.manager.get_installed_version = lambda: ''
    for name, value in (('BASEDIR', str(self.root)), ('MAPD_PATH', str(self.binary))):
      patcher = patch.object(mapd_installer, name, value)
      patcher.start()
      self.addCleanup(patcher.stop)

  def test_bundled_hash_prevents_stock_download_without_version(self):
    with patch.object(mapd_installer, 'update_installed_version') as record_version:
      self.assertFalse(self.manager.download_needed())
      record_version.assert_called_once_with(mapd_installer.VERSION, self.manager._params)

  def test_missing_binary_uses_legacy_fallback(self):
    self.binary.unlink()
    self.assertTrue(self.manager.download_needed())

  def test_hash_mismatch_does_not_claim_producer_recovery(self):
    self.binary.write_bytes(b'stock or replaced producer')
    with patch.object(mapd_installer, 'update_installed_version') as record_version:
      self.assertTrue(self.manager.download_needed())
      record_version.assert_not_called()
      self.manager.get_installed_version = lambda: mapd_installer.VERSION
      self.assertFalse(self.manager.download_needed())

  def test_missing_hash_uses_legacy_fallback(self):
    self.hash_path.unlink()
    self.assertTrue(self.manager.download_needed())
