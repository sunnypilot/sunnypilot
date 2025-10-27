import subprocess

import openpilot.system.sentry as sentry


def run_cmd(cmd, success_message, fail_message, report=True, env=None):
  try:
    result = subprocess.run(cmd, capture_output=True, check=True, env=env, text=True)
    print(success_message)
    return result.stdout.strip()
  except subprocess.CalledProcessError as error:
    print(f"Command failed with return code {error.returncode}")
    if error.stderr:
      print(f"Error Output: {error.stderr.strip()}")
    if report:
      sentry.capture_exception(error)
    return None
  except Exception as exception:
    print(f"Unexpected error occurred: {exception}")
    print(fail_message)
    if report:
      sentry.capture_exception(exception)
    return None
