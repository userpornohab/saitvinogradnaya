from __future__ import annotations

from io import BytesIO
from pathlib import Path
from uuid import uuid4
import re
import warnings
from xml.etree import ElementTree as ET

from fastapi import HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_IMAGE_SIDE = 1920
WEBP_QUALITY = 82

ALLOWED_RASTER_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_SVG_TYPES = {"image/svg+xml"}


def safe_stem(filename: str | None) -> str:
    stem = Path(filename or "image").stem.lower()
    stem = re.sub(r"[^a-zа-яё0-9_-]+", "-", stem, flags=re.IGNORECASE)
    stem = re.sub(r"-+", "-", stem).strip("-_")
    return stem[:48] or "image"


async def read_limited_upload(file: UploadFile, max_bytes: int = MAX_IMAGE_BYTES) -> bytes:
    try:
        content = await file.read(max_bytes + 1)
    finally:
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
    public_dir: str = "uploads",
) -> str:
    upload_dir.mkdir(parents=True, exist_ok=True)

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(BytesIO(content))
            if image.width * image.height > 24_000_000:
                raise HTTPException(413, "Image exceeds 24 megapixels")
            image.verify()
            image = Image.open(BytesIO(content))
            image.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        raise HTTPException(400, f"Файл {original_filename} не является изображением")

    image = ImageOps.exif_transpose(image)
    if image.mode not in ("RGB", "RGBA"):
        image = image.convert("RGB")

    image.thumbnail((MAX_IMAGE_SIDE, MAX_IMAGE_SIDE), Image.Resampling.LANCZOS)

    filename = f"{prefix}_{uuid4().hex}_{safe_stem(original_filename)}.webp"
    filepath = upload_dir / filename
    image.save(filepath, "WEBP", quality=WEBP_QUALITY, method=6)
    return f"/static/{public_dir}/{filename}"


async def save_upload_image(file: UploadFile, upload_dir: Path, prefix: str) -> str:
    if file.content_type not in ALLOWED_RASTER_TYPES:
        raise HTTPException(400, f"Недопустимый тип файла {file.filename}")
    content = await read_limited_upload(file)
    return await run_in_threadpool(save_webp_image, content, upload_dir, file.filename, prefix)


def save_svg_image(content: bytes, upload_dir: Path, original_filename: str | None, prefix: str, public_dir: str = "uploads") -> str:
    try:
        source = content.decode("utf-8")
        if "<!doctype" in source.lower() or "<!entity" in source.lower():
            raise ValueError("XML declarations are not allowed")
        root = ET.fromstring(source)
        tags = {"svg", "g", "path", "rect", "circle", "ellipse", "line", "polyline", "polygon",
                "defs", "linearGradient", "radialGradient", "stop", "clipPath", "mask", "use",
                "symbol", "title", "desc", "text", "tspan"}
        if root.tag not in {"svg", "{http://www.w3.org/2000/svg}svg"}:
            raise ValueError("Not an SVG")
        for element in root.iter():
            tag = element.tag.removeprefix("{http://www.w3.org/2000/svg}")
            if tag not in tags:
                raise ValueError("Unsupported SVG element")
            for key, value in element.attrib.items():
                key = key.rsplit("}", 1)[-1].lower()
                compact = re.sub(r"\s+", "", value).lower()
                if key.startswith("on") or key in {"base", "src"}:
                    raise ValueError("Active SVG attribute")
                if key == "href" and not re.fullmatch(r"#[\w.-]+", value):
                    raise ValueError("External SVG reference")
                if any(token in compact for token in ("javascript:", "data:", "http:", "https:", "//", "@", "\\", "expression(")):
                    raise ValueError("Unsafe SVG value")
                if "url(" in compact and not re.fullmatch(r"url\(#[\w.-]+\)", compact):
                    raise ValueError("Unsafe SVG URL")
        content = ET.tostring(root, encoding="utf-8")
    except (UnicodeDecodeError, ET.ParseError, ValueError):
        raise HTTPException(400, "SVG contains unsupported or unsafe content")

    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{prefix}_{uuid4().hex}_{safe_stem(original_filename)}.svg"
    filepath = upload_dir / filename
    filepath.write_bytes(content)
    return f"/static/{public_dir}/{filename}"


async def save_upload_image_or_svg(file: UploadFile, upload_dir: Path, prefix: str) -> str:
    if file.content_type in ALLOWED_RASTER_TYPES:
        content = await read_limited_upload(file)
        return await run_in_threadpool(save_webp_image, content, upload_dir, file.filename, prefix)
    if file.content_type in ALLOWED_SVG_TYPES:
        content = await read_limited_upload(file, max_bytes=512 * 1024)
        return await run_in_threadpool(save_svg_image, content, upload_dir, file.filename, prefix)
    raise HTTPException(400, f"Недопустимый тип файла {file.filename}")


async def save_raw_upload(
    file: UploadFile,
    upload_dir: Path,
    prefix: str,
    allowed_types: set[str],
    max_bytes: int = 512 * 1024,
    public_dir: str = "icons",
) -> str:
    if file.content_type not in allowed_types:
        raise HTTPException(400, f"Недопустимый тип файла {file.filename}")
    content = await read_limited_upload(file, max_bytes=max_bytes)
    if file.content_type in ALLOWED_SVG_TYPES:
        return await run_in_threadpool(save_svg_image, content, upload_dir, file.filename, prefix, public_dir)
    if file.content_type in ALLOWED_RASTER_TYPES:
        return await run_in_threadpool(save_webp_image, content, upload_dir, file.filename, prefix, public_dir)
    raise HTTPException(400, "Unsupported image type")
