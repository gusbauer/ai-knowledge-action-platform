from pathlib import Path

from fastapi.concurrency import run_in_threadpool
from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
}


class DocumentParsingError(ValueError):
    pass


def _read_text_file(path: Path) -> str:
    encodings = (
        "utf-8",
        "utf-8-sig",
        "utf-16",
    )

    for encoding in encodings:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue

    raise DocumentParsingError(
        "The text file encoding is not supported."
    )


def _read_pdf(path: Path) -> str:
    reader = PdfReader(path)

    pages = []

    for page in reader.pages:
        page_text = page.extract_text() or ""

        if page_text.strip():
            pages.append(page_text.strip())

    return "\n\n".join(pages)


def _extract_text_sync(path: Path) -> str:
    if not path.exists():
        raise DocumentParsingError(
            "The stored document does not exist."
        )

    extension = path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise DocumentParsingError(
            "Unsupported document format."
        )

    if extension in {".txt", ".md"}:
        text = _read_text_file(path)

    else:
        text = _read_pdf(path)

    text = text.strip()

    if not text:
        raise DocumentParsingError(
            "No extractable text was found in the document."
        )

    return text


async def extract_text(storage_path: str) -> str:
    path = Path(storage_path)

    try:
        return await run_in_threadpool(
            _extract_text_sync,
            path,
        )

    except DocumentParsingError:
        raise

    except Exception as exc:
        raise DocumentParsingError(
            "The document could not be parsed."
        ) from exc