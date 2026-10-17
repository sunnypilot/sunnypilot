#!/usr/bin/env python3
from itertools import chain
import json
import os
from pathlib import Path
from openpilot.common.basedir import BASEDIR
from openpilot.selfdrive.ui.translations.potools import extract_strings, generate_pot, merge_po, init_po

SYSTEM_UI_DIR = Path(BASEDIR) / "openpilot/system/ui"
UI_DIR = Path(BASEDIR) / "openpilot/selfdrive/ui"
TRANSLATIONS_DIR = UI_DIR.joinpath("translations")
LANGUAGES_FILE = os.path.join(str(TRANSLATIONS_DIR), "languages.json")
POT_FILE = os.path.join(str(TRANSLATIONS_DIR), "app.pot")


def update_translations():
  files = []
  for root, _, filenames in chain(os.walk(SYSTEM_UI_DIR),
                                  os.walk(os.path.join(str(UI_DIR), "widgets")),
                                  os.walk(os.path.join(str(UI_DIR), "layouts")),
                                  os.walk(os.path.join(str(UI_DIR), "onroad"))):
    for filename in filenames:
      if filename.endswith(".py"):
        files.append(os.path.relpath(os.path.join(root, filename), BASEDIR))

  # The sunnylink settings, consent, and pairing pages live outside the base UI directories.
  sunnylink_sources = chain(UI_DIR.glob("sunnypilot/**/sunnylink*.py"),
                           UI_DIR.glob("sunnypilot/**/onboarding.py"))
  files.extend(os.path.relpath(path, BASEDIR) for path in sorted(sunnylink_sources))

  # Extract translatable strings and generate .pot template
  entries = extract_strings(files, BASEDIR)
  generate_pot(entries, POT_FILE)

  # Generate/update translation files for each language
  with open(LANGUAGES_FILE, encoding="utf-8") as f:
    languages = json.load(f)
  for name in languages.values():
    po_file = os.path.join(str(TRANSLATIONS_DIR), f"app_{name}.po")
    if os.path.exists(po_file):
      merge_po(po_file, POT_FILE)
    else:
      init_po(POT_FILE, po_file, name)


if __name__ == "__main__":
  update_translations()
