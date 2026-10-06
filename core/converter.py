from io import BytesIO
from pathlib import Path

from PIL import Image

# Target formats available for each supported image source extension.
# Extend this map when adding new converters (documents, audio, video, etc.).
IMAGE_FORMAT_MAP = {
    "png": ["jpg", "webp", "pdf"],
    "jpg": ["png", "webp", "pdf"],
    "jpeg": ["png", "webp", "pdf"],
    "webp": ["png", "jpg", "pdf"],
}

# Canonical media types for the generated output.
OUTPUT_MEDIA_TYPES = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "webp": "image/webp",
    "pdf": "application/pdf",
}


def _source_extension(content_type: str | None, filename: str | None) -> str | None:
    """Resolve source extension from MIME type first, then from filename."""
    mime_lookup = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }

    if content_type and content_type.lower() in mime_lookup:
        return mime_lookup[content_type.lower()]

    if filename:
        suffix = Path(filename).suffix.lower().lstrip(".")
        if suffix:
            return "jpg" if suffix == "jpeg" else suffix
    return None


def get_compatible_formats(content_type: str | None, filename: str | None) -> list[str]:
    """Return compatible output formats for the uploaded source file."""
    source_ext = _source_extension(content_type, filename)
    if not source_ext:
        return []
    return IMAGE_FORMAT_MAP.get(source_ext, [])


def _convert_image(source_bytes: bytes, source_ext: str, target_format: str) -> bytes:
    if target_format not in IMAGE_FORMAT_MAP.get(source_ext, []):
        raise ValueError(f"Conversion from .{source_ext} to .{target_format} is not supported")

    with Image.open(BytesIO(source_bytes)) as image:
        # JPEG/PDF do not support alpha, so convert to RGB when required.
        if target_format in {"jpg", "pdf"} and image.mode not in {"RGB", "L"}:
            image = image.convert("RGB")

        output = BytesIO()
        if target_format == "jpg":
            image.save(output, format="JPEG", quality=95)
        elif target_format == "png":
            image.save(output, format="PNG")
        elif target_format == "webp":
            image.save(output, format="WEBP")
        elif target_format == "pdf":
            image.save(output, format="PDF")
        else:
            raise ValueError(f"Target format .{target_format} is not supported")

        return output.getvalue()


def convert_file(source_bytes: bytes, source_filename: str | None, target_format: str) -> tuple[bytes, str, str]:
    """
    Route uploaded data to the correct converter.
    Add more branches here for documents, spreadsheets, media, etc.
    """
    normalized_target = target_format.lower().lstrip(".")
    source_ext = _source_extension(content_type=None, filename=source_filename)
    if not source_ext:
        raise ValueError("Unable to determine source format")

    converted_bytes = _convert_image(source_bytes, source_ext, normalized_target)
    media_type = OUTPUT_MEDIA_TYPES[normalized_target]
    output_extension = "jpg" if normalized_target == "jpeg" else normalized_target
    return converted_bytes, media_type, output_extension
