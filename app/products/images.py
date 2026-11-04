from io import BytesIO
from pathlib import Path
from uuid import uuid4
import warnings

from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
ALLOWED_FORMATS = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG"}

MAX_IMAGE_SIZE = 2 * 1024 * 1024
MAX_IMAGE_PIXELS = 20_000_000


def get_upload_directory():
    directory = Path(
        current_app.config.get(
            "PRODUCTS_UPLOAD_DIR",
            Path(current_app.root_path) / "products" / "static" / "uploads",
        )
    )

    directory.mkdir(parents=True, exist_ok=True)

    return directory


def save_product_image(file):
    if not file or not file.filename:
        return None

    original_name = secure_filename(file.filename)
    extension = Path(original_name).suffix.lower().lstrip(".")

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError("Дозволені лише PNG, JPG і JPEG.")

    image_data = file.stream.read(MAX_IMAGE_SIZE + 1)

    if not image_data:
        raise ValueError("Файл зображення порожній.")

    if len(image_data) > MAX_IMAGE_SIZE:
        raise ValueError("Зображення перевищує 2 МБ.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)

            with Image.open(BytesIO(image_data)) as image:
                if image.format != ALLOWED_FORMATS[extension]:
                    raise ValueError("Формат файлу не відповідає його розширенню.")

                if image.width * image.height > MAX_IMAGE_PIXELS:
                    raise ValueError("Зображення має занадто велику роздільність.")

                image.verify()

            with Image.open(BytesIO(image_data)) as image:
                image.load()

    except ValueError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombWarning,
        Image.DecompressionBombError,
    ):
        raise ValueError("Файл не є коректним зображенням PNG або JPEG.") from None

    filename = f"{uuid4().hex}.{extension}"
    destination = get_upload_directory() / filename

    destination.write_bytes(image_data)

    return f"uploads/{filename}"
