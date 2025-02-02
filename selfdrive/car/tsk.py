from openpilot.common.swaglog import cloudlog
from openpilot.selfdrive.car import Car

class TSK:
  """
  Handles security key install, extraction, and validation for TSK vehicles.
  """

  def __init__(
    self,
    car: Car,
    user_key_path: str = "/cache/params/SecOCKey",
    params_key: str = "SecOCKey"
  ):
    self.car: Car = car
    self.user_key_path: str = user_key_path
    self.params_key: str = params_key

  def get_installed(self, should_auto_install_user_key: bool = True) -> bytes | None:
    """
    Retrieve the installed security key for the car.

    This method first checks if a valid key is already installed in the car's parameters.
    If a valid key is found, it is returned as bytes. If not, and if auto-installation is
    enabled, it attempts to read a user key, validate it, install it, and then return it.

    Args:
        should_auto_install_user_key (bool, optional): If True, automatically attempt to install
            a user key if no valid key is already installed. Defaults to True.

    Returns:
        bytes | None: The valid security key as a bytes object if found or installed; otherwise, None.
    """

    # If a valid key is already installed, simply return
    installed_key: str = self.car.params.get(self.params_key, encoding='utf8').strip()
    if installed_key:
      if self.is_key_valid_for_this_car(installed_key):
        cloudlog.info("TSK: Valid key already installed")
        return bytes.fromhex(installed_key)
      else:
        cloudlog.warning(f"TSK: Installed key is not valid for this car: {installed_key}")
    else:
      cloudlog.warning("TSK: Key not installed")

    if should_auto_install_user_key:
      # If user key is available, install and return
      try:
        with open(self.user_key_path) as f:
          user_key: str = f.readline().strip()
          if self.is_key_valid_for_this_car(user_key):
            self.car.params.put(self.params_key, user_key)
            cloudlog.info(f"TSK: Found a valid user key and installed successfully: {user_key}")
            return bytes.fromhex(user_key)
          else:
            cloudlog.warning(f"TSK: User key is not valid for this car: {user_key}")
      except Exception as e:
        cloudlog.warning(f"TSK: Failed to read user key: {e}")
        # Suppress the error and continue
        pass
    else:
      cloudlog.warning("TSK: User key not auto installed as requested")

    cloudlog.warning("TSK: Valid key not found")
    return None

  def extract(self) -> bytes | None:
    """
    Extract the security key using I-CAN-HACK's extract_keys.py

    Returns:
        bytes | None: The extracted security key as bytes if successful; otherwise, None.
    """
    # TODO
    return None

  def is_key_valid_for_this_car(self, key: str) -> bool:
    if len(key) != 32:
      cloudlog.warning(f"TSK: Invalid key length: {key}")
      return False

    hex_chars_lower: set[str] = set(x for x in "0123456789abcdef")
    if not hex_chars_lower.issuperset(set(key)):
      cloudlog.warning(f"TSK: Invalid key characters: {key}")
      return False

    try:
      key_bytes: bytes = bytes.fromhex(key)
    except ValueError as e:
      cloudlog.warning(f"TSK: Failed to convert key to bytes: {key} - {e}")
      return False
    if len(key_bytes) != 16:
      cloudlog.warning(f"TSK: Invalid key length: {key}")
      return False

    # TODO
    # 1. Read a few CAN messages
    # 2. Generate a signature using the provided key
    # 3. Return True if the existing signatures match the generated
    # 4. Return False otherwise

    cloudlog.info(f"TSK: Key is valid for this car: {key}")
    return True
