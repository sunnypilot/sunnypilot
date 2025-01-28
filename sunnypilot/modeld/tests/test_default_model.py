import os
import subprocess

from openpilot.common.basedir import BASEDIR

REF_COMMIT_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDefaultModel:
  @classmethod
  def setup_class(cls):
    cls.onnx_path = os.path.join(BASEDIR, "selfdrive", "modeld", "models", "supercombo.onnx")
    cls.ref_path = os.path.join(REF_COMMIT_DIR, "ref_commit")

  @staticmethod
  def get_git_ref(path: str) -> str:
    try:
      return subprocess.check_output(['git', 'log', '-n', '1', '--pretty=format:%H', '--', path], cwd=BASEDIR).decode("utf-8").strip()
    except subprocess.CalledProcessError as e:
      raise RuntimeError(f"Failed to get git ref for {path}: {e}") from e

  def test_model_ref_matches(self):
    ref = self.get_git_ref(str(self.onnx_path))

    with open(self.ref_path) as f:
      current_ref = f.read().strip()

    assert ref == current_ref, (
      "Driving model updated!\n" +
      f"Current ref: {current_ref}\n" +
      f"New ref: {ref}\n" +
      "Please update common/model.h if the default driving model name has changed."
    )
