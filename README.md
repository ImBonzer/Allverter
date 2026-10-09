# Allverter

Allverter is an easy-to-use universal file converter starter built with FastAPI, Pillow, and vanilla JavaScript.

The image converter supports JPG, JPEG, PNG, WEBP, GIF, BMP, TIFF, ICO, PPM, PGM, PBM, TGA, JPEG 2000, AVIF, QOI, and DDS input/output formats. Images can also be exported as PDF files. Audio and video conversion is available on the `/media` page when FFmpeg is installed; document conversion is not implemented yet.

The web interface supports direct single-file downloads or ZIP downloads for multiple files, image previews, shared output-format detection, server-side upload limits, keyboard-accessible drag and drop, and a persisted dark mode. The `/media` page exposes an FFmpeg-backed audio/video converter for MP3, WAV, AAC, FLAC, M4A, OGG, MP4, WEBM, MOV, MKV, and AVI. Render installs FFmpeg through the Dockerfile; local development requires FFmpeg on PATH.
