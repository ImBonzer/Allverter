"""Conversion registry and the first Pillow-backed image conversion route."""

from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image, UnidentifiedImageError


class ConversionError(Exception):
    """Raised when a file cannot be converted by a registered converter."""


@dataclass(frozen=True)
class ConversionResult:
    """Metadata needed to stream a converted temporary file."""

    path: str
    filename: str
    mime_type: str


IMAGE_FORMATS: dict[str, tuple[str, str]] = {
    "jpg": ("JPEG", "image/jpeg"),
    "jpeg": ("JPEG", "image/jpeg"),
    "png": ("PNG", "image/png"),
    "webp": ("WEBP", "image/webp"),
    "gif": ("GIF", "image/gif"),
    "bmp": ("BMP", "image/bmp"),
    "tif": ("TIFF", "image/tiff"),
    "tiff": ("TIFF", "image/tiff"),
    "ico": ("ICO", "image/x-icon"),
    "ppm": ("PPM", "image/x-portable-pixmap"),
    "pgm": ("PPM", "image/x-portable-graymap"),
    "pbm": ("PPM", "image/x-portable-bitmap"),
    "tga": ("TGA", "image/x-tga"),
    "jp2": ("JPEG2000", "image/jp2"),
    "j2k": ("JPEG2000", "image/jp2"),
    "jpf": ("JPEG2000", "image/jp2"),
    "avif": ("AVIF", "image/avif"),
    "qoi": ("QOI", "image/qoi"),
    "dds": ("DDS", "image/vnd-ms.dds"),
    "pdf": ("PDF", "application/pdf"),
}

READABLE_FORMATS = set(IMAGE_FORMATS) - {"pdf"}


def _convert_image(source: Path, destination: Path, target_format: str) -> None:
    """Convert an image with Pillow, handling transparency for JPEG output."""
    image_format, _ = IMAGE_FORMATS[target_format]
    try:
        with Image.open(source) as image:
            if image_format in ("JPEG", "PDF") and image.mode in ("RGBA", "LA", "P"):
                background = Image.new("RGB", image.size, "white")
                alpha = image.convert("RGBA")
                background.paste(alpha, mask=alpha.getchannel("A"))
                image = background
            elif image_format in ("JPEG", "PDF") and image.mode not in ("1", "L", "RGB"):
                image = image.convert("RGB")
            image.save(destination, format=image_format)
    except (UnidentifiedImageError, OSError) as error:
        raise ConversionError("That file is not a readable image.") from error


def get_supported_targets(filename: str) -> list[str]:
    """Return image formats compatible with the uploaded file."""
    suffix = Path(filename).suffix.lower().lstrip(".")
    if suffix in READABLE_FORMATS:
        return [extension for extension in IMAGE_FORMATS if extension != suffix]
    return []


def convert_file(source: Path, target_format: str) -> ConversionResult:
    """Route a source file to its registered converter.

    Add document, audio, or video routes here as new converters become available.
    Each route should write to the supplied destination and return metadata in the
    same shape so the API stays independent from conversion-library details.
    """
    source_format = source.suffix.lower().lstrip(".")
    target_format = target_format.lower().lstrip(".")
    if source_format not in READABLE_FORMATS or target_format not in IMAGE_FORMATS:
        raise ConversionError("This file type is not supported yet. Try a PNG, JPG, WEBP, BMP, TIFF, or GIF image.")
    if target_format == source_format:
        raise ConversionError("Choose a different output format.")

    extension = ".jpg" if target_format == "jpeg" else f".{target_format}"
    output = NamedTemporaryFile(prefix="allverter-result-", suffix=extension, delete=False)
    output.close()
    destination = Path(output.name)
    try:
        _convert_image(source, destination, target_format)
    except ConversionError:
        destination.unlink(missing_ok=True)
        raise
    mime_type = IMAGE_FORMATS[target_format][1]
    return ConversionResult(str(destination), f"{source.stem}{extension}", mime_type)
