#!/usr/bin/env python3
import filecmp
import subprocess

from collections.abc import Callable
from pathlib import Path

from laica.common.util import run_cmd


def laica_manager_init(func: Callable) -> Callable:
  """Decorator for manager initialization with Laica setup."""

  def wrapper(*args, **kwargs):
    boot_logo_location = Path("/usr/comma/bg.jpg")
    laica_boot_logo = Path(__file__).parents[1] / "assets/boot/laica_boot_logo.jpg"
    if not filecmp.cmp(laica_boot_logo, boot_logo_location, shallow=False):
      stock_mount_options = subprocess.run(["findmnt", "-no", "OPTIONS", "/"], capture_output=True, text=True, check=True).stdout.strip()

      run_cmd(["sudo", "mount", "-o", "remount,rw", "/"], \
        "Successfully remounted / as read-write", \
        "Failed to remount / as read-write")
      run_cmd(["sudo", "cp", laica_boot_logo, boot_logo_location], \
        "Successfully replaced boot logo", \
        "Failed to replace boot logo")
      run_cmd(["sudo", "mount", "-o", f"remount,{stock_mount_options}", "/"], \
        "Successfully restored stock mount options", \
        "Failed to restore stock mount options")

    # Call the original manager_init function
    return func(*args, **kwargs)

  return wrapper

