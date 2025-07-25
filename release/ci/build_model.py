#!/usr/bin/env python3
import argparse
import os
import subprocess
import shutil

def run(cmd, cwd=None, check=True, env=None):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, check=check, env=env)
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-dir', required=True)
    parser.add_argument('--output-dir', required=True)
    parser.add_argument('--scons-cache-dir', required=False)
    parser.add_argument('--tinygrad-path', required=True)
    parser.add_argument('--models-dir', required=True)
    parser.add_argument('--custom-name', required=True)
    parser.add_argument('--upstream-branch', required=True)
    parser.add_argument('--is-20hz', default="true")
    parser.add_argument('--powersave-script', required=False, default=None)
    parser.add_argument('--model-generator', required=False, default="release/ci/model_generator.py")
    parser.add_argument('--get-model-metadata', required=False, default=None)
    args = parser.parse_args()

    # Set up environment variables
    env = os.environ.copy()
    env["UV_PROJECT_ENVIRONMENT"] = os.path.expanduser("~/venv")
    env["VIRTUAL_ENV"] = env["UV_PROJECT_ENVIRONMENT"]
    env["PYTHONPATH"] = env.get("PYTHONPATH", "") + f":{args.tinygrad_path}"

    # Setup build environment
    os.makedirs(args.build_dir, exist_ok=True)
    for entry in os.listdir(args.build_dir):
      path = os.path.join(args.build_dir, entry)
      if os.path.islink(path):
        continue
      if os.path.isdir(path):
        shutil.rmtree(path)
      else:
        os.remove(path)

    if args.powersave_script:
      run(f"PYTHONPATH=$PYTHONPATH {args.powersave_script} --disable", env=env)

    # Compile models
    for fname in os.listdir(args.models_dir):
      if fname.endswith('.onnx'):
        onnx_file = os.path.join(args.models_dir, fname)
        base_name = fname[:-5]
        output_file = os.path.join(args.models_dir, f"{base_name}_tinygrad.pkl")
        run(f"QCOM=1 python3 {args.tinygrad_path}/examples/openpilot/compile3.py {onnx_file} {output_file}", env=env)
        if args.get_model_metadata:
          run(f"QCOM=1 python3 {args.get_model_metadata} {onnx_file}", check=False, env=env)

    # Prepare output dir
    if os.path.exists(args.output_dir):
      shutil.rmtree(args.output_dir)
    os.makedirs(args.output_dir, exist_ok=True)

    # Copy model files
    for ext in ['.dlc', '.thneed', '.pkl', '.onnx']:
      for fname in os.listdir(args.models_dir):
        if fname.endswith(ext):
          shutil.copy2(os.path.join(args.models_dir, fname), args.output_dir)

    cmd = " ".join([
      f"python3 {args.model_generator}",
      f"--model-dir \"{args.models_dir}\"",
      f"--output-dir \"{args.output_dir}\"",
      f"--custom-name \"{args.custom_name}\"",
      f"--upstream-branch \"{args.upstream_branch}\"",
      f"{'--is-20hz' if args.is_20hz.lower() == 'true' else ''}"
    ])
    run(cmd, env=env)

    if args.powersave_script:
      run(f"PYTHONPATH=$PYTHONPATH {args.powersave_script} --enable", env=env)

if __name__ == "__main__":
  main()
