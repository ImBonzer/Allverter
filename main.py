"""FastAPI application for the Allverter file conversion service."""

from pathlib import Path
import os
from shutil import rmtree
from tempfile import mkdtemp
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.background import BackgroundTask

from core.converter import ConversionError, convert_file, get_supported_targets
from core.media_converter import MediaConversionError, convert_media, ffmpeg_available, get_supported_media_targets

BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="Allverter", description="A universal file conversion starter app")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _cleanup_conversion(temp_dir: Path, result_path: str) -> None:
    """Remove the per-request upload directory and converted output."""
    Path(result_path).unlink(missing_ok=True)
    rmtree(temp_dir, ignore_errors=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Render the upload interface."""
    return templates.TemplateResponse(request, "index.html")


@app.get("/media", response_class=HTMLResponse)
async def media_index(request: Request) -> HTMLResponse:
    """Render the audio and video conversion interface."""
    return templates.TemplateResponse(request, "media.html")


@app.get("/api/formats")
async def formats(filename: str) -> dict[str, object]:
    """Return compatible output formats for a filename."""
    return {"source": Path(filename).suffix.lower().lstrip("."), "targets": get_supported_targets(filename)}


@app.get("/api/media/formats")
async def media_formats(filename: str) -> dict[str, object]:
    """Return media targets and FFmpeg availability."""
    return {"available": ffmpeg_available(), "source": Path(filename).suffix.lower().lstrip("."), "targets": get_supported_media_targets(filename)}


@app.post("/api/convert")
async def convert(upload: UploadFile = File(...), target_format: str = Form("")) -> FileResponse:
    """Convert an uploaded file and stream the result back as a download."""
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Please choose a file to convert.")
    if not target_format:
        raise HTTPException(status_code=400, detail="Please choose an output format.")

    temp_dir = Path(mkdtemp(prefix="allverter-"))
    try:
        source = temp_dir / Path(upload.filename).name
        source.write_bytes(await upload.read())
        result = convert_file(source, target_format)
        return FileResponse(
            result.path,
            media_type=result.mime_type,
            filename=result.filename,
            headers={"X-Content-Type-Options": "nosniff"},
            background=BackgroundTask(_cleanup_conversion, temp_dir, result.path),
        )
    except ConversionError as error:
        rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/media/convert")
async def convert_media_file(upload: UploadFile = File(...), target_format: str = Form("")) -> FileResponse:
    """Convert one audio or video file with FFmpeg."""
    if not upload.filename:
        raise HTTPException(status_code=400, detail="Please choose an audio or video file.")
    if not target_format:
        raise HTTPException(status_code=400, detail="Please choose an output format.")

    temp_dir = Path(mkdtemp(prefix="allverter-media-"))
    try:
        source = temp_dir / Path(upload.filename).name
        source.write_bytes(await upload.read())
        result_path, result_filename, mime_type = convert_media(source, target_format)
        return FileResponse(
            result_path,
            media_type=mime_type,
            filename=result_filename,
            headers={"X-Content-Type-Options": "nosniff"},
            background=BackgroundTask(_cleanup_conversion, temp_dir, result_path),
        )
    except MediaConversionError as error:
        rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=503 if not ffmpeg_available() else 400, detail=str(error)) from error


@app.post("/api/batch-convert")
async def batch_convert(
    uploads: list[UploadFile] = File(...),
    target_format: str = Form(""),
) -> FileResponse:
    """Convert multiple images and return the results as a ZIP archive."""
    if not uploads or len(uploads) > 20:
        raise HTTPException(status_code=400, detail="Choose between 1 and 20 files.")
    if not target_format:
        raise HTTPException(status_code=400, detail="Please choose an output format.")

    temp_dir = Path(mkdtemp(prefix="allverter-batch-"))
    archive_path = temp_dir / "allverter-results.zip"
    try:
        results = []
        for index, upload in enumerate(uploads, start=1):
            if not upload.filename:
                raise ConversionError("One of the selected files has no filename.")
            source = temp_dir / f"source-{index}{Path(upload.filename).suffix.lower()}"
            source.write_bytes(await upload.read())
            results.append(convert_file(source, target_format))

        with ZipFile(archive_path, "w", ZIP_DEFLATED) as archive:
            for index, result in enumerate(results, start=1):
                archive.write(result.path, f"{index:02d}-{result.filename}")

        return FileResponse(
            archive_path,
            media_type="application/zip",
            filename="allverter-results.zip",
            headers={"X-Content-Type-Options": "nosniff"},
            background=BackgroundTask(_cleanup_conversion, temp_dir, archive_path),
        )
    except ConversionError as error:
        rmtree(temp_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(error)) from error
