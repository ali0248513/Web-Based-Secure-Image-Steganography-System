"""
LSB (Least Significant Bit) Steganography Engine
--------------------------------------------------
Embeds and extracts arbitrary byte payloads inside the LSBs of an
RGB image's pixel values.

Bit layout of the embedded payload:
    [ 8 bits  : flag  ]  -> 1 = AES encrypted, 0 = plain text
    [ 32 bits : length]  -> length of payload (in bytes) that follows
    [ N bits  : payload]  -> the actual message (or AES iv+ciphertext)

Using a length header (instead of a delimiter sequence) makes
extraction deterministic and avoids false-positive delimiter matches.
"""

import numpy as np
from PIL import Image


class StegoCapacityError(Exception):
    """Raised when the message is too large for the chosen cover image."""
    pass


def _bytes_to_bits(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    bits = np.unpackbits(arr)
    return bits


def _bits_to_bytes(bits: np.ndarray) -> bytes:
    # pad to a multiple of 8 just in case
    pad = (-len(bits)) % 8
    if pad:
        bits = np.concatenate([bits, np.zeros(pad, dtype=np.uint8)])
    arr = np.packbits(bits)
    return arr.tobytes()


def _int_to_bits(value: int, n_bits: int) -> np.ndarray:
    return np.array([(value >> i) & 1 for i in range(n_bits - 1, -1, -1)], dtype=np.uint8)


def _bits_to_int(bits: np.ndarray) -> int:
    value = 0
    for b in bits:
        value = (value << 1) | int(b)
    return value


def max_capacity_bytes(image_path: str) -> int:
    """Maximum number of payload bytes that can be hidden in this image."""
    img = Image.open(image_path).convert("RGB")
    w, h = img.size
    total_bits = w * h * 3
    header_bits = 8 + 32
    return max(0, (total_bits - header_bits) // 8)


def encode_image(cover_path: str, payload: bytes, flag: int, out_path: str) -> str:
    """
    Hides `payload` bytes inside `cover_path` image and writes the
    resulting stego image (lossless PNG) to `out_path`.
    """
    img = Image.open(cover_path).convert("RGB")
    arr = np.array(img)
    flat = arr.reshape(-1)  # view of all R,G,B values in sequence

    flag_bits = _int_to_bits(flag, 8)
    length_bits = _int_to_bits(len(payload), 32)
    payload_bits = _bytes_to_bits(payload)

    all_bits = np.concatenate([flag_bits, length_bits, payload_bits])

    if len(all_bits) > flat.size:
        raise StegoCapacityError(
            f"Message too large for this image. "
            f"Max capacity is {max_capacity_bytes(cover_path)} bytes, "
            f"message needs {len(payload)} bytes."
        )

    # Clear LSBs of the pixels we are about to use, then set them
    flat = flat.copy()
    flat[:len(all_bits)] = (flat[:len(all_bits)] & 0xFE) | all_bits

    stego_arr = flat.reshape(arr.shape)
    stego_img = Image.fromarray(stego_arr.astype(np.uint8), mode="RGB")
    stego_img.save(out_path, format="PNG")  # PNG = lossless, required for LSB integrity
    return out_path


def decode_image(stego_path: str):
    """
    Extracts the hidden payload from a stego image.
    Returns (flag, payload_bytes).
    """
    img = Image.open(stego_path).convert("RGB")
    arr = np.array(img)
    flat = arr.reshape(-1)

    header_bits = flat[:40] & 1
    flag = _bits_to_int(header_bits[:8])
    length = _bits_to_int(header_bits[8:40])

    if length < 0 or length > (flat.size - 40) // 8:
        raise ValueError("No valid hidden message found (corrupted or non-stego image).")

    payload_bits = flat[40:40 + length * 8] & 1
    payload = _bits_to_bytes(payload_bits)
    return flag, payload
