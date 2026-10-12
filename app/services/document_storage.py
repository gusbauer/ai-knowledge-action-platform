import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool


UPLOAD_DIR = Path("data/uploads")

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}

MAX_FILE_SIZE = 10 * 1024 * 1024


class InvalidDocumentFileError(ValueError):
    pass


async def save_upload(file: UploadFile) -> tuple[str, int]:
    if not file.filename:
        raise InvalidDocumentFileError(
            "The uploaded file must have a filename."
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise InvalidDocumentFileError(
            "Only PDF, TXT and Markdown files are allowed."
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / stored_filename

    try:
        with destination.open("wb") as buffer:
            await run_in_threadpool(
                shutil.copyfileobj,
                file.file,
                buffer,
            )

        size_bytes = destination.stat().st_size

        if size_bytes == 0:
            raise InvalidDocumentFileError(
                "The uploaded file is empty."
            )

        if size_bytes > MAX_FILE_SIZE:
            raise InvalidDocumentFileError(
                "The uploaded file exceeds the 10 MB limit."
            )

        return destination.as_posix(), size_bytes

    except Exception:
        destination.unlink(missing_ok=True)
        raise

    finally:
        await file.close()