import pytest

from app.services.text_chunker import (
    ChunkingError,
    split_text,
)


def test_short_text_returns_single_chunk():
    text = "RAG uses retrieved context to answer questions."

    chunks = split_text(
        text,
        chunk_size=100,
        overlap=20,
    )

    assert chunks == [text]


def test_split_text_applies_overlap():
    text = "abcdefghij"

    chunks = split_text(
        text,
        chunk_size=6,
        overlap=2,
    )

    assert chunks == [
        "abcdef",
        "efghij",
    ]


@pytest.mark.parametrize(
    "text, chunk_size, overlap",
    [
        ("", 100, 20),
        ("valid text", 0, 0),
        ("valid text", 10, 10),
        ("valid text", 10, -1),
    ],
)
def test_invalid_chunking_parameters_raise_error(
    text: str,
    chunk_size: int,
    overlap: int,
):
    with pytest.raises(ChunkingError):
        split_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
        )