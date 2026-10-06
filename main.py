from pathlib import Path
import re

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from core.converter import convert_file, get_compatible_formats

app = FastAPI(title="Allverter")
templates = Jinja2Templates(directory="templates")


def _safe_stem(filename: str) -> str:
    """Return a filesystem-safe filename stem."""
    stem = Path(filename or "converted-file").stem
    safe_stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", stem).strip("._")
    return safe_stem or "converted-file"


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/formats")
async def formats(file: UploadFile = File(...)):
    compatible_formats = get_compatible_formats(file.content_type, file.filename)
    if not compatible_formats:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    return JSONResponse({"formats": compatible_formats})


@app.post("/convert")
async def convert(file: UploadFile = File(...), target_format: str = Form(...)):
    compatible_formats = get_compatible_formats(file.content_type, file.filename)
    normalized_target = target_format.lower().lstrip(".")

    if normalized_target not in compatible_formats:
        raise HTTPException(status_code=400, detail="Incompatible target format")

    source_bytes = await file.read()
    if not source_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        converted_bytes, media_type, output_extension = convert_file(
            source_bytes=source_bytes,
            source_filename=file.filename,
            target_format=normalized_target,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    output_name = f"{_safe_stem(file.filename)}.{output_extension}"
    return StreamingResponse(
        iter([converted_bytes]),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{output_name}"'},
    )
