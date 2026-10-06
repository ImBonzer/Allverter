# Allverter

Allverter is an easy-to-use universal file converter starter built with FastAPI, Pillow, and vanilla JavaScript.

The current image converter supports JPG, JPEG, PNG, WEBP, GIF, BMP, TIFF, ICO, PPM, PGM, PBM, TGA, JPEG 2000, AVIF, QOI, and DDS input/output formats. Images can also be exported as PDF files. PDF is currently output-only; document, audio, and video conversion are not included yet.

The web interface supports direct single-file downloads or ZIP downloads for multiple files, image previews, shared output-format detection, file-size validation, keyboard-accessible drag and drop, and a persisted dark mode. The `/media` page now exposes an FFmpeg-backed audio/video converter for MP3, WAV, AAC, FLAC, M4A, OGG, MP4, WEBM, MOV, MKV, and AVI. FFmpeg must be installed and available on PATH. Document conversion is not implemented yet and will require an engine such as LibreOffice.
