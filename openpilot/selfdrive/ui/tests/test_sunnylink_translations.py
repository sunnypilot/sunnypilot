import ast
from pathlib import Path
import string
import unittest

from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.translations.potools import extract_strings, parse_po


SOURCES = (
  "openpilot/selfdrive/ui/sunnypilot/layouts/settings/sunnylink.py",
  "openpilot/selfdrive/ui/sunnypilot/layouts/onboarding.py",
  "openpilot/selfdrive/ui/sunnypilot/mici/layouts/sunnylink.py",
  "openpilot/selfdrive/ui/sunnypilot/mici/layouts/onboarding.py",
  "openpilot/selfdrive/ui/sunnypilot/mici/widgets/sunnylink_pairing_dialog.py",
  "openpilot/system/ui/sunnypilot/widgets/sunnylink_pairing_dialog.py",
)
TRANSLATIONS = Path(BASEDIR) / "openpilot/selfdrive/ui/translations"


class TestSunnylinkTranslations(unittest.TestCase):
  def test_all_sunnylink_messages_are_translated(self):
    sources = extract_strings(list(SOURCES), BASEDIR)
    self.assertGreater(len(sources), 80)
    formatter = string.Formatter()
    for language in ("ja", "zh-CHT", "ko"):
      _, entries = parse_po(TRANSLATIONS / f"app_{language}.po")
      catalog = {entry.msgid: entry.msgstr for entry in entries}
      for entry in sources:
        with self.subTest(language=language, source=entry.msgid):
          translated = catalog.get(entry.msgid)
          self.assertTrue(translated, "missing or empty sunnylink translation")
          source_fields = sorted((name, spec, conv) for _, name, spec, conv in formatter.parse(entry.msgid) if name is not None)
          translated_fields = sorted((name, spec, conv) for _, name, spec, conv in formatter.parse(translated) if name is not None)
          self.assertEqual(source_fields, translated_fields)

  def test_sunnylink_sources_use_extractable_translation_keys(self):
    for source in SOURCES:
      tree = ast.parse((Path(BASEDIR) / source).read_text(encoding="utf-8"))
      for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "tr":
          with self.subTest(source=source, line=node.lineno):
            self.assertIsInstance(node.args[0], ast.Constant)
            self.assertIsInstance(node.args[0].value, str)

  def test_progress_translations_accept_runtime_values(self):
    for language in ("ja", "zh-CHT", "ko"):
      _, entries = parse_po(TRANSLATIONS / f"app_{language}.po")
      catalog = {entry.msgid: entry.msgstr for entry in entries}
      for key in ("Backing up {progress}%", "Restoring {progress}%", "{progress}%"):
        for progress in (0, 37.5, 100):
          with self.subTest(language=language, key=key, progress=progress):
            self.assertIn(f"{progress}%", catalog[key].format(progress=progress))


if __name__ == "__main__":
  unittest.main()
