"""Optional FFmpeg-backed audio and video conversion."""

from pathlib import Path
from shutil import which
from subprocess import CompletedProcess, run
from tempfile import NamedTemporaryFile


class MediaConversionError(Exception):
    """Raised when FFmpeg cannot convert a media file."""


MEDIA_FORMATS: dict[str, tuple[str, str]] = {
    "mp3": ("audio/mpeg", "Audio"),
    "wav": ("audio/wav", "Audio"),
    "aac": ("audio/aac", "Audio"),
    "flac": ("audio/flac", "Audio"),
    "m4a": ("audio/mp4", "Audio"),
    "ogg": ("audio/ogg", "Audio"),
    "mp4": ("video/mp4", "Video"),
    "webm": ("video/webm", "Video"),
    "mov": ("video/quicktime", "Video"),
    "mkv": ("video/x-matroska", "Video"),
    "avi": ("video/x-msvideo", "Video"),
}

READABLE_MEDIA_FORMATS = set(MEDIA_FORMATS)


def ffmpeg_available() -> bool:
    """Return whether FFmpeg is available on PATH."""
    return _ffmpeg_path() is not None


def _ffmpeg_path() -> str | None:
    """Find FFmpeg on PATH or in the standard WinGet package location."""
    executable = which("ffmpeg")
    if executable:
        return executable

    winget_root = Path.home() / "AppData" / "Local" / "Microsoft" / "WinGet" / "Packages"
    matches = list(winget_root.glob("Gyan.FFmpeg.Shared_*/*/bin/ffmpeg.exe"))
    return str(matches[0]) if matches else None


def get_supported_media_targets(filename: str) -> list[str]:
    """Return media targets for an audio or video filename."""
    source = Path(filename).suffix.lower().lstrip(".")
    if source not in READABLE_MEDIA_FORMATS:
        return []
    source_type = MEDIA_FORMATS[source][1]
    return [extension for extension, (_, media_type) in MEDIA_FORMATS.items() if media_type == source_type and extension != source]


def convert_media(source: Path, target_format: str) -> tuple[str, str, str]:
    """Convert media with FFmpeg and return path, filename, and MIME type."""
    target_format = target_format.lower().lstrip(".")
    source_format = source.suffix.lower().lstrip(".")
    ffmpeg = _ffmpeg_path()
    if not ffmpeg:
        raise MediaConversionError("FFmpeg is required for audio and video conversion. Install FFmpeg and add it to PATH.")
    if source_format not in MEDIA_FORMATS or target_format not in MEDIA_FORMATS:
        raise MediaConversionError("This audio or video format is not supported yet.")
    if MEDIA_FORMATS[source_format][1] != MEDIA_FORMATS[target_format][1]:
        raise MediaConversionError("Audio and video formats cannot be mixed in one conversion.")

    output = NamedTemporaryFile(prefix="allverter-media-", suffix=f".{target_format}", delete=False)
    output.close()
    destination = Path(output.name)
    completed: CompletedProcess[str] = run(
        [ffmpeg, "-y", "-i", str(source), str(destination)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        destination.unlink(missing_ok=True)
        raise MediaConversionError("FFmpeg could not read or convert that file.")
    return str(destination), f"{source.stem}.{target_format}", MEDIA_FORMATS[target_format][0]