import os
import base64
import uuid

from flask import Blueprint, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

from models import Upload

routes = Blueprint("routes", __name__)


@routes.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    title = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    sentiment = request.form.get("sentiment", "").strip()
    custom_sentiment = request.form.get("custom_sentiment", "").strip()
    voice_note_data = request.form.get("voice_note_data", "")
    image = request.files.get("image")

    if not title or not description or not image or not sentiment:
        flash("Title, description, image, and sentiment are required.")
        return render_template("upload.html"), 400

    if sentiment == "Custom" and not custom_sentiment:
        flash("Please enter a custom sentiment.")
        return render_template("upload.html"), 400

    if sentiment != "Custom":
        custom_sentiment = ""

    filename = secure_filename(image.filename or "")
    if not filename:
        flash("Please choose a valid image file.")
        return render_template("upload.html"), 400

    save_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    image.save(save_path)

    voice_note_filename = None
    if voice_note_data:
        if "," not in voice_note_data:
            flash("Voice note format is invalid.")
            return render_template("upload.html"), 400
        _, encoded = voice_note_data.split(",", 1)
        try:
            voice_bytes = base64.b64decode(encoded)
        except (ValueError, TypeError):
            flash("Voice note could not be processed.")
            return render_template("upload.html"), 400

        voice_note_filename = f"voice-{uuid.uuid4().hex}.webm"
        voice_path = os.path.join(
            current_app.config["UPLOAD_FOLDER"], voice_note_filename)
        with open(voice_path, "wb") as voice_file:
            voice_file.write(voice_bytes)

    Upload.create(
        current_user.get_id(),
        title,
        description,
        filename,
        sentiment,
        custom_sentiment,
        voice_note_filename,
    )
    flash("Upload saved.")
    return redirect(url_for("routes.records"))


@routes.route("/records")
@login_required
def records():
    uploads = Upload.get_by_user(current_user.get_id())
    page = request.args.get("page", default=1, type=int)
    if page < 1:
        page = 1

    per_page = 25
    total = len(uploads)
    start = (page - 1) * per_page
    end = start + per_page
    paged_uploads = uploads[start:end]

    has_prev = page > 1
    has_next = end < total

    return render_template(
        "records.html",
        uploads=paged_uploads,
        page=page,
        has_prev=has_prev,
        has_next=has_next,
    )


@routes.route("/uploads/<path:filename>")
@login_required
def uploaded_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)
