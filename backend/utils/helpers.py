import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename: str) -> bool:
    """Return True if the file has an allowed extension (PDF only)."""
    allowed = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed


def save_uploaded_file(file) -> str:
    """Save an uploaded FileStorage object to UPLOAD_FOLDER.
    Returns the saved filename (not the full path).
    """
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    save_path = os.path.join(upload_folder, filename)
    # Avoid name collisions by appending a short uuid prefix
    if os.path.exists(save_path):
        import uuid
        prefix = uuid.uuid4().hex[:8]
        filename = f"{prefix}_{filename}"
        save_path = os.path.join(upload_folder, filename)
    file.save(save_path)
    return filename
