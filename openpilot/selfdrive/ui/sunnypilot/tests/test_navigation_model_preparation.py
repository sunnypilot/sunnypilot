"""Execute actual UI action/status methods headlessly; no renderer or download."""
import ast
from html import escape
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
BUILD_REF = 'local-prepare-rl-navigation-80eedcdd'
LOCAL_BUILD_REF = 'local-build-staged-models'
DS = NS(downloading=1, verifying=2, failed=3, downloaded=4, cached=5)
SOURCES = ((ROOT/'layouts/settings/models.py', 'ModelsLayout'), (ROOT/'mici/layouts/models.py', 'ModelsLayoutMici'))


def load_methods(path, name):
  tree = ast.parse(path.read_text())
  cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
  names = {'_prepare_navigation_model', '_build_local_models', '_handle_navigation_preparation', '_download_row_state', '_set_item_note',
           '_show_navigation_preparation_details'}
  cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
  cls.bases = []
  ui = NS(is_offroad=Mock(return_value=True), params=Mock())
  ui.params.get.return_value = None
  ui.params.get_bool.return_value = False
  env = {'BUILD_REF': BUILD_REF, 'LOCAL_BUILD_REF': LOCAL_BUILD_REF, 'ui_state': ui, 'custom': NS(ModelManagerSP=NS(DownloadStatus=DS)),
         'escape': escape, 'gui_app': Mock(), 'SettingDescriptionDialog': lambda title, message: NS(title=title, message=message),
         'device': Mock(), 'tr': lambda s: s, 'ON_COLOR': 'green', 'rl': NS(RED='red', GRAY='gray', WHITE='white')}
  exec(compile(ast.Module(body=[cls], type_ignores=[]), str(path), 'exec'), env)
  obj = env[name]()
  obj.prepare_navigation_item = Mock()
  obj.preparation_details_btn = Mock()
  return obj, ui


def bundle(status, *, ref=BUILD_REF, text='Preparing Navigation Model: Downloading…', progress_status=None, stage='building'):
  p = NS(status=progress_status or status, progress=37., canceling=False, speed=2048.)
  return NS(ref=ref, status=status, displayName=text, internalName=stage,
            models=[NS(artifact=NS(fileName='navigation-model', downloadProgress=p))])


class NavigationPreparationUiTests(unittest.TestCase):
  def test_action_queues_special_ref_without_selecting_model(self):
    for path, name in SOURCES:
      with self.subTest(layout=name):
        obj, ui = load_methods(path, name)
        obj._prepare_navigation_model()
        ui.params.put.assert_called_once_with('ModelManager_DownloadRef', BUILD_REF)
        ui.params.put_bool.assert_not_called()
        ui.params.remove.assert_not_called()

  def test_action_rejects_onroad_busy_or_cache_clear(self):
    for path, name in SOURCES:
      for offroad, queued, clearing in ((False, None, False), (True, 'other', False), (True, None, True)):
        with self.subTest(layout=name, offroad=offroad, queued=queued, clearing=clearing):
          obj, ui = load_methods(path, name)
          ui.is_offroad.return_value = offroad
          ui.params.get.return_value = queued
          ui.params.get_bool.return_value = clearing
          obj._prepare_navigation_model()
          ui.params.put.assert_not_called()

  def test_tici_keeps_full_failure_and_success_status(self):
    for status, text in ((DS.failed, 'Preparation failed: LLVM 18+ required'),
                         (DS.downloaded, 'Navigation Model ready — select it below')):
      obj, _ = load_methods(*SOURCES[0])
      obj.cancel_download_item, obj.download_item = Mock(), Mock()
      b = bundle(status, text=text)
      self.assertTrue(obj._handle_navigation_preparation(b, [b.models[0].artifact.downloadProgress]))
      state = obj.download_item.action_item.update.call_args.kwargs
      self.assertEqual(state['name'], text)
      self.assertEqual(state['status_text'], '')
      self.assertFalse(obj._downloading)

  def test_tici_compile_progress_and_cancel(self):
    obj, ui = load_methods(*SOURCES[0])
    ui.params.get.return_value = BUILD_REF
    obj.cancel_download_item, obj.download_item = Mock(), Mock()
    b = bundle(DS.downloading, progress_status=DS.verifying, text='Building Navigation Model…')
    obj._handle_navigation_preparation(b, [b.models[0].artifact.downloadProgress])
    state = obj.download_item.action_item.update.call_args.kwargs
    self.assertEqual(state['name'], b.displayName)
    self.assertEqual(state['status_text'], 'building')
    self.assertTrue(obj._downloading and obj._verifying)
    obj.cancel_download_item.set_visible.assert_called_with(True)

  def test_mici_keeps_full_status_and_offers_cancel_during_build(self):
    for status in (DS.downloading, DS.failed, DS.downloaded):
      obj, ui = load_methods(*SOURCES[1])
      ui.params.get.return_value = BUILD_REF if status == DS.downloading else None
      obj.cancel_download_btn, obj.current_model_info = Mock(), Mock()
      b = bundle(status, text='Full preparation stage or error', progress_status=DS.verifying)
      self.assertTrue(obj._handle_navigation_preparation(b))
      obj.current_model_info.current_model_text.set_text.assert_called_with(b.displayName)
      obj.cancel_download_btn.set_visible.assert_called_with(status == DS.downloading)
      if status != DS.downloading:
        obj.current_model_info.info_text.set_text.assert_called_with(b.displayName)
      else:
        self.assertIn('keep the device parked', obj.current_model_info.info_text.set_text.call_args.args[0])

  def test_checking_is_not_reported_as_building(self):
    for source in SOURCES:
      obj, _ = load_methods(*source)
      obj.cancel_download_item, obj.download_item = Mock(), Mock()
      obj.cancel_download_btn, obj.current_model_info = Mock(), Mock()
      b = bundle(DS.downloading, progress_status=DS.verifying, stage='checking',
                 text='Checking navigation model preparation requirements')
      if source == SOURCES[0]:
        obj._handle_navigation_preparation(b, [b.models[0].artifact.downloadProgress])
        self.assertEqual(obj.download_item.action_item.update.call_args.kwargs['status_text'], 'checking requirements')
        self.assertFalse(obj._verifying)
      else:
        obj._handle_navigation_preparation(b)
        self.assertEqual(obj.current_model_info.info_text.set_text.call_args.args[0], 'checking requirements')

  def test_full_long_error_remains_readable(self):
    message = 'Preparation failed: missing LLVM <18> dependency. ' + 'Detailed diagnostic text. ' * 35
    for source in SOURCES:
      obj, _ = load_methods(*source)
      obj.cancel_download_item, obj.download_item = Mock(), Mock()
      obj.cancel_download_btn, obj.current_model_info = Mock(), Mock()
      b = bundle(DS.failed, stage='failed', text=message)
      if source == SOURCES[0]:
        obj._handle_navigation_preparation(b, [b.models[0].artifact.downloadProgress])
        obj.prepare_navigation_item.set_description.assert_called_with(escape(message))
        obj.prepare_navigation_item.show_description.assert_called_with(True)
      else:
        obj._handle_navigation_preparation(b)
        obj.preparation_details_btn.set_visible.assert_called_with(True)
        obj._show_navigation_preparation_details()
        dialog = obj._show_navigation_preparation_details.__globals__['gui_app'].push_widget.call_args.args[0]
        self.assertEqual(dialog.message, message)

  def test_verification_and_unknown_stage_never_claim_building(self):
    for stage, expected in (('verifying', 'verifying'), ('unexpected', 'preparing')):
      for source in SOURCES:
        obj, _ = load_methods(*source)
        obj.cancel_download_item, obj.download_item = Mock(), Mock()
        obj.cancel_download_btn, obj.current_model_info = Mock(), Mock()
        b = bundle(DS.downloading, progress_status=DS.verifying, stage=stage)
        if source == SOURCES[0]:
          obj._handle_navigation_preparation(b, [b.models[0].artifact.downloadProgress])
          self.assertEqual(obj.download_item.action_item.update.call_args.kwargs['status_text'], expected)
        else:
          obj._handle_navigation_preparation(b)
          self.assertEqual(obj.current_model_info.info_text.set_text.call_args.args[0], expected)

  def test_unmeasured_eta_removed_and_details_clear_with_normal_bundle(self):
    for path, _ in SOURCES:
      self.assertNotIn('several minutes', path.read_text())
    obj, _ = load_methods(*SOURCES[1])
    obj.cancel_download_btn, obj.current_model_info = Mock(), Mock()
    obj._handle_navigation_preparation(bundle(DS.failed, stage='failed'))
    obj._handle_navigation_preparation(bundle(DS.downloading, ref='normal-model'))
    obj.preparation_details_btn.set_visible.assert_called_with(False)
    self.assertEqual(obj._navigation_preparation_message, '')

  def test_normal_bundle_status_follows_original_path(self):
    for path, name in SOURCES:
      obj, _ = load_methods(path, name)
      args = (bundle(DS.downloading, ref='normal-model'), []) if name == 'ModelsLayout' else (bundle(DS.downloading, ref='normal-model'),)
      self.assertFalse(obj._handle_navigation_preparation(*args))

  def test_both_visible_actions_use_exported_ref_and_onroad_disable(self):
    for path, _ in SOURCES:
      source = path.read_text()
      self.assertIn('from openpilot.sunnypilot.models.navigation_model import BUILD_REF', source)
      self.assertIn('self._prepare_navigation_model)', source)
      tree = ast.parse(source)
      attributes = {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
      self.assertTrue('prepare_navigation_item' in attributes or 'prepare_navigation_btn' in attributes)
      self.assertIn('offroad and not self._downloading', source) if 'settings/models' in str(path) else self.assertIn(
        'ui_state.is_offroad() and not is_downloading', source)

  def test_cancel_buttons_remove_existing_request_key(self):
    for path, _ in SOURCES:
      source = path.read_text()
      self.assertIn('ui_state.params.remove("ModelManager_DownloadRef")', source)
      self.assertNotIn('params.put("ModelManager_ActiveBundle', source)


if __name__ == '__main__':
  unittest.main()


class LocalBuildUiTests(unittest.TestCase):
  PATH, NAME = ROOT/'mici/layouts/models.py', 'ModelsLayoutMici'

  def test_build_button_queues_the_local_build_ref_only_when_idle_offroad(self):
    obj, ui = load_methods(self.PATH, self.NAME)
    obj._build_local_models()
    ui.params.put.assert_called_once_with('ModelManager_DownloadRef', LOCAL_BUILD_REF)
    for offroad, queued, clearing in ((False, None, False), (True, 'other', False), (True, None, True)):
      with self.subTest(offroad=offroad, queued=queued, clearing=clearing):
        obj, ui = load_methods(self.PATH, self.NAME)
        ui.is_offroad.return_value = offroad
        ui.params.get.return_value = queued
        ui.params.get_bool.return_value = clearing
        obj._build_local_models()
        ui.params.put.assert_not_called()

  def test_local_build_progress_is_labelled_as_a_local_build(self):
    obj, ui = load_methods(self.PATH, self.NAME)
    obj.cancel_download_btn = Mock()
    obj.current_model_info = Mock()
    self.assertTrue(obj._handle_navigation_preparation(bundle(DS.downloading, ref=LOCAL_BUILD_REF, text='Building FF')))
    obj.current_model_info.current_model_header.set_text.assert_called_with('local model build')
    obj.cancel_download_btn.set_text.assert_called_with('cancel build')
    obj._show_navigation_preparation_details()
