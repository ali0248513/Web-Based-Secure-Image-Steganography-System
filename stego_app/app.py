import os
import uuid

from flask import (
    Flask, render_template, request, redirect, url_for,
    send_from_directory, flash, abort
)
from werkzeug.utils import secure_filename

from stego import lsb, crypto_utils, analysis

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "static", "results")
ALLOWED_EXT = {"png", "jpg", "jpeg", "bmp"}

app = Flask(__name__)
app.secret_key = "dip-stego-secret-key"  # only needed for flash messages
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB upload limit

os.makedirs(RESULTS_DIR, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ---------------------------------------------------------------- HOME ----
@app.route("/")
def home():
    return render_template("index.html")


# -------------------------------------------------------------- ENCODE ----
@app.route("/encode", methods=["GET", "POST"])
def encode():
    if request.method == "GET":
        return render_template("encode.html")

    file = request.files.get("cover_image")
    message = request.form.get("message", "")
    key = request.form.get("enc_key", "").strip()

    if not file or file.filename == "":
        flash("Please choose a cover image.", "danger")
        return redirect(url_for("encode"))
    if not allowed_file(file.filename):
        flash("Unsupported file type. Use PNG, JPG, JPEG, or BMP.", "danger")
        return redirect(url_for("encode"))
    if not message:
        flash("Please enter a secret message.", "danger")
        return redirect(url_for("encode"))

    # Create a unique result folder for this operation
    result_id = uuid.uuid4().hex[:12]
    folder = os.path.join(RESULTS_DIR, result_id)
    os.makedirs(folder, exist_ok=True)

    cover_filename = "original_" + secure_filename(file.filename)
    cover_path = os.path.join(folder, cover_filename)
    file.save(cover_path)

    # Build payload (optionally AES-encrypted)
    if key:
        payload = crypto_utils.encrypt(message, key)
        flag = 1
    else:
        payload = message.encode("utf-8")
        flag = 0

    stego_path = os.path.join(folder, "stego.png")
    try:
        lsb.encode_image(cover_path, payload, flag, stego_path)
    except lsb.StegoCapacityError as e:
        flash(str(e), "danger")
        return redirect(url_for("encode"))

    return render_template(
        "encode.html",
        result_id=result_id,
        cover_filename=cover_filename,
        stego_ready=True,
        was_encrypted=bool(key),
    )


# -------------------------------------------------------------- DECODE ----
@app.route("/decode", methods=["GET", "POST"])
def decode():
    if request.method == "GET":
        return render_template("decode.html")

    file = request.files.get("stego_image")
    key = request.form.get("enc_key", "").strip()

    if not file or file.filename == "":
        flash("Please choose a stego image.", "danger")
        return redirect(url_for("decode"))

    tmp_name = uuid.uuid4().hex[:12] + "_" + secure_filename(file.filename)
    tmp_path = os.path.join(BASE_DIR, "uploads", tmp_name)
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)
    file.save(tmp_path)

    try:
        flag, payload = lsb.decode_image(tmp_path)
    except Exception as e:
        flash(f"Could not extract a message: {e}", "danger")
        return redirect(url_for("decode"))

    if flag == 1:
        if not key:
            flash("This message is encrypted. Please provide the encryption key.", "warning")
            return render_template("decode.html")
        try:
            message = crypto_utils.decrypt(payload, key)
        except Exception:
            flash("Wrong decryption key, or corrupted data.", "danger")
            return redirect(url_for("decode"))
    else:
        message = payload.decode("utf-8", errors="replace")

    return render_template("decode.html", extracted_message=message)


# ------------------------------------------------------------ ANALYSIS ----
@app.route("/analysis/<result_id>")
def analysis_page(result_id):
    folder = os.path.join(RESULTS_DIR, result_id)
    if not os.path.isdir(folder):
        abort(404)

    files = os.listdir(folder)
    cover_filename = next((f for f in files if f.startswith("original_")), None)
    if cover_filename is None or "stego.png" not in files:
        abort(404)

    cover_path = os.path.join(folder, cover_filename)
    stego_path = os.path.join(folder, "stego.png")

    metrics = analysis.analyze(cover_path, stego_path)

    return render_template(
        "analysis.html",
        result_id=result_id,
        cover_filename=cover_filename,
        metrics=metrics,
    )


@app.route("/results/<result_id>/<filename>")
def serve_result_file(result_id, filename):
    folder = os.path.join(RESULTS_DIR, result_id)
    return send_from_directory(folder, filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
