"""
AES-256-CBC encryption helpers.

The user-supplied "Encryption Key" (any passphrase string) is hashed with
SHA-256 to derive a fixed 32-byte AES key. A random 16-byte IV is generated
per encryption and prepended to the ciphertext so it can be recovered
during decryption.
"""

import hashlib
import os

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def _derive_key(passphrase: str) -> bytes:
    return hashlib.sha256(passphrase.encode("utf-8")).digest()


def encrypt(message: str, passphrase: str) -> bytes:
    key = _derive_key(passphrase)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ct = cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
    return iv + ct  # prepend IV so decrypt() can read it back out


def decrypt(blob: bytes, passphrase: str) -> str:
    key = _derive_key(passphrase)
    iv, ct = blob[:16], blob[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt.decode("utf-8")
