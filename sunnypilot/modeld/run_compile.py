import sys
from subprocess import run

correct_path = "/data/openpilot/sunnypilot/tinygrad"
incorrect_path = "/data/sunnypilot/tinygrad"

sys.path = [p for p in sys.path if p != incorrect_path]

if correct_path not in sys.path:
  sys.path.insert(0, correct_path)

run([
  "python3", "/data/sunnypilot/sunnypilot/tinygrad_repo/openpilot/compile2.py",
  "/data/sunnypilot/sunnypilot/modeld/models/supercombo.onnx",
  "/data/sunnypilot/sunnypilot/modeld/models/supercombo.thneed",
])
