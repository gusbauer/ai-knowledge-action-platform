DEFAULT_CHUNK_SIZE = 1000
DEFAULT_CHUNK_OVERLAP = 200


class ChunkingError(ValueError):
    pass


def split_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if not text.strip():
        raise ChunkingError(
            "Cannot chunk empty text."
        )

    if chunk_size <= 0:
        raise ChunkingError(
            "Chunk size must be greater than zero."
        )

    if overlap < 0 or overlap >= chunk_size:
        raise ChunkingError(
            "Overlap must be between 0 and chunk_size - 1."
        )

    chunks: list[str] = []

    start = 0
    text_length = len(text)

    while start < text_length:
        tentative_end = min(
            start + chunk_size,
            text_length,
        )

        end = tentative_end

        if tentative_end < text_length:
            last_space = text.rfind(
                " ",
                start,
                tentative_end,
            )

            if last_space > start + (chunk_size // 2):
                end = last_space

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = max(
            end - overlap,
            start + 1,
        )

    return chunks