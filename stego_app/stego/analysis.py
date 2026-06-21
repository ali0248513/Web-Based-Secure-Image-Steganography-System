"""
Digital Image Processing analysis utilities:
 - MSE  (Mean Squared Error)
 - PSNR (Peak Signal-to-Noise Ratio)
 - Side-by-side RGB histogram comparison chart
"""

import io
import base64

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")  # headless backend, no display needed
import matplotlib.pyplot as plt


def compute_mse(original_path: str, stego_path: str) -> float:
    orig = np.array(Image.open(original_path).convert("RGB"), dtype=np.float64)
    stego = np.array(Image.open(stego_path).convert("RGB"), dtype=np.float64)
    if orig.shape != stego.shape:
        stego = np.array(
            Image.open(stego_path).convert("RGB").resize((orig.shape[1], orig.shape[0])),
            dtype=np.float64,
        )
    mse = np.mean((orig - stego) ** 2)
    return float(mse)


def compute_psnr(mse: float, max_pixel: float = 255.0) -> float:
    if mse == 0:
        return float("inf")  # identical images
    return float(20 * np.log10(max_pixel) - 10 * np.log10(mse))


def histogram_comparison_base64(original_path: str, stego_path: str) -> str:
    """Builds a matplotlib RGB-channel histogram comparison and returns it
    as a base64 PNG data-URI string ready for direct embedding in HTML."""
    orig = np.array(Image.open(original_path).convert("RGB"))
    stego = np.array(Image.open(stego_path).convert("RGB"))

    colors = ("red", "green", "blue")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))

    for i, c in enumerate(colors):
        axes[0].hist(orig[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=c, alpha=0.5, label=c.capitalize())
    axes[0].set_title("Original Image Histogram")
    axes[0].set_xlabel("Pixel Value")
    axes[0].set_ylabel("Frequency")
    axes[0].legend()

    for i, c in enumerate(colors):
        axes[1].hist(stego[:, :, i].ravel(), bins=256, range=(0, 256),
                     color=c, alpha=0.5, label=c.capitalize())
    axes[1].set_title("Stego Image Histogram")
    axes[1].set_xlabel("Pixel Value")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110)
    plt.close(fig)
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def analyze(original_path: str, stego_path: str) -> dict:
    mse = compute_mse(original_path, stego_path)
    psnr = compute_psnr(mse)
    hist_b64 = histogram_comparison_base64(original_path, stego_path)
    return {
        "mse": round(mse, 6),
        "psnr": "∞ (identical)" if psnr == float("inf") else round(psnr, 2),
        "histogram": hist_b64,
    }
