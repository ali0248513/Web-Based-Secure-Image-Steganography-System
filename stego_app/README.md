# 🔐 Secure Image Steganography System (LSB Technique)

A web-based application that hides secret text messages inside images using the **Least Significant Bit (LSB)** technique, with optional **AES-256 encryption** and a built-in **Digital Image Processing analysis** module (MSE, PSNR, histogram comparison).

Built with **Python, Flask, Pillow, NumPy, and PyCryptodome**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.x-black)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Demo / Screenshots](#-demo--screenshots)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Installation](#-installation)
- [Usage](#-usage)
- [Image Quality Metrics](#-image-quality-metrics)
- [Limitations](#-limitations)
- [Future Improvements](#-future-improvements)
- [License](#-license)

---

## 📖 Overview

Steganography hides the *existence* of a message, rather than just scrambling it like encryption does. This project demonstrates a practical implementation of **image steganography** using LSB substitution: the least significant bit of each pixel's color value is replaced with a bit of the secret message, producing a "stego image" that is visually indistinguishable from the original.

The system also layers on **AES-256 encryption** (optional) for confidentiality, and includes a **Digital Image Processing analysis page** to quantitatively prove the embedding is imperceptible — using MSE, PSNR, and RGB histogram comparisons.

---

## ✨ Features

- 🖼️ **Encode** — Upload a cover image, type a secret message, optionally set an encryption key, and download the resulting stego image.
- 🔓 **Decode** — Upload a stego image (and key, if used) to recover the original hidden message.
- 🔑 **AES-256 Encryption** — Optional passphrase-based encryption (SHA-256 key derivation, random IV per operation) applied before embedding.
- 📊 **Analysis Dashboard** — Side-by-side original vs. stego image, RGB histogram comparison chart, MSE, and PSNR.
- 🌐 **Simple Web UI** — Bootstrap 5 interface, no installation needed beyond Python.
- 🔒 **Lossless Output** — Stego images are always saved as PNG to guarantee the hidden bits survive.

---

## 🎬 Demo / Screenshots

> Replace these with your own screenshots before publishing.

| Home Page | Encode Page | Analysis Page |
|---|---|---|
| ![home](docs/screenshots/home.png) | ![encode](docs/screenshots/encode.png) | ![analysis](docs/screenshots/analysis.png) |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Backend | Python 3, Flask |
| Image Processing | Pillow (PIL), NumPy, OpenCV |
| Encryption | PyCryptodome (AES-256-CBC) |
| Analysis / Charts | NumPy (MSE/PSNR), Matplotlib (histograms) |
| Templating | Jinja2 |

---

## 📂 Project Structure

```
stego_app/
├── app.py                  # Flask routes (home, encode, decode, analysis)
├── requirements.txt
├── README.md
├── stego/
│   ├── __init__.py
│   ├── lsb.py               # LSB encode/decode engine
│   ├── crypto_utils.py      # AES-256-CBC encrypt/decrypt helpers
│   └── analysis.py          # MSE, PSNR, histogram comparison
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── encode.html
│   ├── decode.html
│   └── analysis.html
├── static/
│   ├── css/style.css
│   └── results/              # generated stego images & analysis assets (gitignored)
└── uploads/                   # temp uploads for decoding (gitignored)
```

---

## ⚙️ How It Works

### Encoding
1. The secret message is optionally encrypted with **AES-256-CBC** (key derived from your passphrase via SHA-256, random IV per run).
2. A small binary header is built: `[8-bit flag][32-bit payload length]`.
3. Header + payload bits replace the least significant bit of each pixel's R, G, B values in sequence:
   ```
   pixel = (pixel & 0xFE) | bit
   ```
4. The result is saved as a **lossless PNG** — JPEG compression would destroy the hidden bits.

### Decoding
1. Read the first 40 LSBs to recover the flag and payload length.
2. Read the next `length × 8` LSBs to reconstruct the payload bytes.
3. If the flag indicates encryption, decrypt with the supplied key.

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python3 app.py
```

Open **http://localhost:5000** in your browser.

---

## ▶️ Usage

1. **Home** — Read a quick overview of the system.
2. **Encode** — Upload a cover image, type your message, (optionally) set an encryption key, and hit *Hide Message in Image*. Download the resulting stego image.
3. **Decode** — Upload a stego image, enter the key if one was used, and extract the hidden message.
4. **Analysis** — From the Encode result, click *View Analysis* to see MSE, PSNR, and histogram comparisons for that specific operation.

---

## 📐 Image Quality Metrics

**MSE (Mean Squared Error)**
```
MSE = (1 / (W × H × C)) × Σ (Original(x,y,c) − Stego(x,y,c))²
```
Lower is better — measures the average squared pixel-level difference.

**PSNR (Peak Signal-to-Noise Ratio)**
```
PSNR = 20 × log₁₀(MAX_PIXEL) − 10 × log₁₀(MSE)
```
Higher is better — values above ~40 dB are generally considered visually lossless. This system typically achieves 60–80+ dB.

**Histogram Comparison** — RGB channel pixel-intensity distributions plotted for both images; LSB embedding keeps them nearly identical, a sign of strong imperceptibility.

---

## ⚠️ Limitations

- Embedding capacity ≈ `(width × height × 3) / 8` bytes per image.
- Cover images must stay lossless (PNG) after encoding — re-saving as JPEG destroys hidden data.
- LSB steganography, while visually imperceptible, can be detected by advanced statistical steganalysis (e.g. chi-square attacks).

## 🔮 Future Improvements

- Support hiding files/images, not just text.
- Frequency-domain embedding (DCT/DWT) for stronger steganalysis resistance.
- User accounts and a history of past encode/decode operations.
- Cloud deployment with HTTPS.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙋 Author

**[Your Name]**
Digital Image Processing Course Project — [Your University Name]
