from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4
import re

from fastapi import HTTPException, UploadFile
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_SIDE = 1920
WEBP_QUALITY = 82

ALLOWED_RASTER_TYPES = {"image/jpeg", "image/png", "image/webp"}


def safe_stem(filename: str | None) -> str:
    stem = Path(filename or "image").stem.lower()
    stem = re.sub(r"[^a-zа-яё0-9_-]+", "-", stem, flags=re.IGNORECASE)
    stem = re.sub(r"-+", "-", stem).strip("-_")
    return stem[:48] or "image"


async def read_limited_upload(file: UploadFile, max_bytes: int = MAX_IMAGE_BYTES) -> bytes:
    content = await file.read()
    await file.close()
    if len(content) > max_bytes:
        raise HTTPException(413, f"Файл {file.filename} больше {max_bytes // (1024 * 1024)} МБ")
    if not content:
        raise HTTPException(400, f"Файл {file.filename} пустой")
    return content


def save_webp_image(
    content: bytes,
    upload_dir: Path,
    original_filename: str | None,
    prefix: str,
) -> str:
    upload_dir.mkdir(parents=True, exist_ok=True)

    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image = Image.open(BytesIO(content))
    except UnidentifiedImageError:
        raise HTTPException(400, f"Файл {original_filename} не является изображением")

    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS)

    filename = f"{prefix}_{uuid4().hex}_{safe_stem(original_filename)}.webp"
    filepath = upload_dir / filename
    image.save(filepath, "WEBP", quality=WEBP_QUALITY, method=6)
    return f"/static/uploads/{filename}"


async def save_upload_image(file: UploadFile, upload_dir: Path, prefix: str) -> str:
    if file.content_type not in ALLOWED_RASTER_TYPES:
        raise HTTPException(400, f"Недопустимый тип файла {file.filename}")
    content = await read_limited_upload(file)
    return save_webp_image(content, upload_dir, file.filename, prefix)


async def save_raw_upload(
    file: UploadFile,
    upload_dir: Path,
    prefix: str,
    allowed_types: set[str],
    max_bytes: int = 512 * 1024,
) -> str:
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Недопустимый тип файла {file.filename}")
    content = await read_limited_upload(file, max_bytes=max_bytes)
    suffix = Path(file.filename or "").suffix.lower()
    filename = f"{prefix}_{uuid4().hex}_{safe_stem(file.filename)}{suffix}"
    upload_dir.mkdir(parents=True, exist_ok=True)
    filepath = upload_dir / filename
    filepath.write_bytes(content)
    return f"/static/icons/{filename}"
