"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
import base64
import hashlib
import os
import zlib
import re
import json
from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec

from openpilot.common.api.base import KEYS
from openpilot.sunnypilot.sunnylink.backups.AESCipher import AESCipher
from openpilot.system.hardware.hw import Paths


class KeyDerivation:
  @staticmethod
  def _load_key(file_path: str) -> bytes:
    with open(file_path, 'rb') as f:
      return f.read()

  @staticmethod
  def derive_aes_key_iv(key_path: str, use_aes_256: bool) -> tuple[bytes, bytes]:
    key_pem: bytes = KeyDerivation._load_key(key_path)
    key_plain = key_pem.decode(errors="ignore")

    if "private" in key_plain.lower():
      private_key = serialization.load_pem_private_key(key_pem, password=None, backend=default_backend())
      if isinstance(private_key, (rsa.RSAPrivateKey, ec.EllipticCurvePrivateKey)):
        public_key = private_key.public_key()
      else:
        raise ValueError("Invalid key format: Unable to determine if key is public or private.")
    elif "public" in key_plain.lower():
      public_key = serialization.load_pem_public_key(key_pem, backend=default_backend())
      if not isinstance(public_key, (rsa.RSAPublicKey, ec.EllipticCurvePublicKey)):
        raise ValueError("Invalid key format: Unable to determine if key is public or private.")
    else:
      raise ValueError("Invalid key format: Unable to determine if key is public or private.")

    if isinstance(public_key, rsa.RSAPublicKey):
      der_data = public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.PKCS1)
    elif isinstance(public_key, ec.EllipticCurvePublicKey):
      der_data = public_key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo)
    else:
      raise ValueError("Unsupported key type.")

    if use_aes_256:
      # AES-256-CBC
      key = hashlib.sha256(der_data).digest()
      iv = hashlib.md5(der_data).digest()
    else:
      # AES-128-CBC
      key = hashlib.md5(der_data).digest()
      iv = hashlib.md5(der_data).digest()  # Insecure IV reuse, kept for compatibility

    return key, iv


def uncompress_dat(data):
  """
  Decompress data using zlib.

  Args:
      data (bytes): Compressed data

  Returns:
      bytes: Decompressed data
  """
  data_stripped_4 = data[4:]
  return zlib.decompress(data_stripped_4)


def compress_dat(data):
  """
  Compress data using zlib.

  Args:
      data (bytes): Data to compress

  Returns:
      bytes: Compressed data
  """
  compressed_data = zlib.compress(data, level=9)
  return b"ZLIB" + compressed_data


def get_key_path(use_aes_256=False) -> str:
  key_path = ""
  for key in KEYS:
    if os.path.isfile(Paths.persist_root() + f'/comma/{key}') and os.path.isfile(Paths.persist_root() + f'/comma/{key}.pub'):
      key_path = str(Path(Paths.persist_root() + f'/comma/{key}') if use_aes_256 else Path(Paths.persist_root() + f'/comma/{key}.pub'))
      break

  if not key_path:
    raise FileNotFoundError("No valid key pair found in persist storage.")

  return key_path


def decrypt_compressed_data(encrypted_base64, use_aes_256=False):
  """
  Decrypt and decompress data from base64 string.

  Args:
      encrypted_base64 (str): Base64 encoded encrypted data
      key_path (str, optional): Path to RSA public key

  Returns:
      str: Decrypted and decompressed string
  """
  try:
    # Decode base64
    encrypted_data = base64.b64decode(encrypted_base64)

    # Decrypt
    key, iv = KeyDerivation.derive_aes_key_iv(get_key_path(use_aes_256), use_aes_256)
    cipher = AESCipher(key, iv)
    decrypted_data = cipher.decrypt(encrypted_data)

    # Decompress
    decompressed_data = uncompress_dat(decrypted_data)

    # Decode UTF-8
    result = decompressed_data.decode('utf-8')
    return result
  except Exception as e:
    print(f"Decryption and decompression failed: {e}")
    return ""


def encrypt_compressed_data(text, use_aes_256=True):
  """
  Compress and encrypt string data to base64.

  Args:
      text (str): Text to compress and encrypt
      key_path (str, optional): Path to RSA public key

  Returns:
      str: Base64 encoded encrypted data
  """
  try:
    # Encode to UTF-8
    text_bytes = text.encode('utf-8')

    # Compress
    compressed_data = compress_dat(text_bytes)

    # Encrypt
    key, iv = KeyDerivation.derive_aes_key_iv(get_key_path(use_aes_256), use_aes_256)
    cipher = AESCipher(key, iv)
    encrypted_data = cipher.encrypt(compressed_data)

    # Encode to base64
    result = base64.b64encode(encrypted_data).decode('utf-8')
    return result
  except Exception as e:
    print(f"Compression and encryption failed: {e}")
    return ""


def camel_to_snake(name):
  """Convert camelCase to snake_case."""
  name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
  return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def transform_dict(obj):
  """Recursively transform dictionary keys from camelCase to snake_case."""
  if isinstance(obj, dict):
    return {camel_to_snake(k): transform_dict(v) for k, v in obj.items()}
  elif isinstance(obj, list):
    return [transform_dict(item) for item in obj]
  return obj


class SnakeCaseEncoder(json.JSONEncoder):
  def encode(self, obj):
    transformed_obj = transform_dict(obj)
    return super().encode(transformed_obj)
