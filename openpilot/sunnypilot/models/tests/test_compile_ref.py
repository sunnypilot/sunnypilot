import re

from openpilot.common.basedir import BASEDIR
from openpilot.common.test import OpenpilotTestCase
from openpilot.sunnypilot.models.compile_ref import COMPILE_SCRIPTS


class TestCompileRef(OpenpilotTestCase):
  def test_matches_sconscript_dependencies(self):
    with open(f"{BASEDIR}/openpilot/selfdrive/modeld/SConscript") as f:
      sconscript = f.read()
    deps = set()
    for name in ("compile_modeld_script", "compile_dm_warp_script"):
      block = re.search(rf"^{name} = \[(.*?)\]", sconscript, re.M | re.S).group(1)
      deps |= {p.lstrip("#").replace("{modeld_dir}", "openpilot/selfdrive/modeld").lstrip("/")
               for p in re.findall(r'File\(f?"([^"]+)"', block)}
    assert deps == set(COMPILE_SCRIPTS)
