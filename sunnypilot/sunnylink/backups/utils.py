import base64
import hashlib
import zlib

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from sunnypilot.sunnylink.backups.AESCipher import AESCipher


class KeyDerivation:
  @staticmethod
  def _load_key(file_path: str) -> bytes:
    with open(file_path, 'rb') as f:
      return f.read()

  @staticmethod
  def derive_aes_key_iv_from_rsa(key_path: str, use_256: bool) -> tuple[bytes, bytes]:
    rsa_key_pem: bytes = KeyDerivation._load_key(key_path)
    key_plain = rsa_key_pem.decode(errors="ignore")

    if "private" in key_plain.lower():
      key = serialization.load_pem_private_key(rsa_key_pem, password=None, backend=default_backend())
      der_data = key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()
      )
    elif "public" in key_plain.lower():
      key = serialization.load_pem_public_key(rsa_key_pem, backend=default_backend())
      der_data = key.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.PKCS1)
    else:
      raise ValueError("Unknown key format: Unable to determine if key is public or private.")

    sha256_hash = hashlib.sha256(der_data).digest()
    aes_key = sha256_hash[:32] if use_256 else sha256_hash[:16]
    aes_iv = sha256_hash[16:32]

    return aes_key, aes_iv


def qUncompress(data):
  """
  Decompress data using zlib.

  Args:
      data (bytes): Compressed data

  Returns:
      bytes: Decompressed data
  """
  data_stripped_4 = data[4:]
  return zlib.decompress(data_stripped_4)


def qCompress(data):
  """
  Compress data using zlib.

  Args:
      data (bytes): Data to compress

  Returns:
      bytes: Compressed data
  """
  compressed_data = zlib.compress(data, level=9)
  return b"ZLIB" + compressed_data


def decrypt_compressed_data(encrypted_base64, key_path=None):
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
    key, iv = KeyDerivation.derive_aes_key_iv_from_rsa(key_path, use_256=False)
    cipher = AESCipher(key, iv)
    decrypted_data = cipher.decrypt(encrypted_data)

    # Decompress
    decompressed_data = qUncompress(decrypted_data)

    # Decode UTF-8
    result = decompressed_data.decode('utf-8')
    return result
  except Exception as e:
    print(f"Decryption and decompression failed: {e}")
    return ""


def encrypt_compress_data(text, key_path=None):
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
    compressed_data = qCompress(text_bytes)

    # Encrypt
    key, iv = KeyDerivation.derive_aes_key_iv_from_rsa(key_path, use_256=False)
    cipher = AESCipher(key, iv)
    encrypted_data = cipher.encrypt(compressed_data)

    # Encode to base64
    result = base64.b64encode(encrypted_data).decode('utf-8')
    return result
  except Exception as e:
    print(f"Compression and encryption failed: {e}")
    return ""
