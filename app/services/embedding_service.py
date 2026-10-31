from functools import lru_cache

from fastapi.concurrency import run_in_threadpool
from sentence_transformers import SentenceTransformer

from app.core.errors import ExternalServiceError
EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_DIMENSION = 384


class EmbeddingGenerationError(
    ExternalServiceError
):
    code = "embedding_generation_failed"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )


def _validate_texts(
    texts: list[str],
) -> None:
    if not texts:
        raise EmbeddingGenerationError(
            "No texts were provided."
        )


def _generate_embeddings_sync(
    texts: list[str],
) -> list[list[float]]:
    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()


def _generate_document_embeddings_sync(
    texts: list[str],
) -> list[list[float]]:
    model = get_embedding_model()

    embeddings = model.encode_document(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()


def _generate_query_embeddings_sync(
    texts: list[str],
) -> list[list[float]]:
    model = get_embedding_model()

    embeddings = model.encode_query(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )

    return embeddings.tolist()


async def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    _validate_texts(texts)

    try:
        return await run_in_threadpool(
            _generate_embeddings_sync,
            texts,
        )

    except Exception as exc:
        raise EmbeddingGenerationError(
            "Embeddings could not be generated."
        ) from exc


async def generate_document_embeddings(
    texts: list[str],
) -> list[list[float]]:
    _validate_texts(texts)

    try:
        return await run_in_threadpool(
            _generate_document_embeddings_sync,
            texts,
        )

    except Exception as exc:
        raise EmbeddingGenerationError(
            "Document embeddings could not be generated."
        ) from exc


async def generate_query_embeddings(
    texts: list[str],
) -> list[list[float]]:
    _validate_texts(texts)

    try:
        return await run_in_threadpool(
            _generate_query_embeddings_sync,
            texts,
        )

    except Exception as exc:
        raise EmbeddingGenerationError(
            "Query embeddings could not be generated."
        ) from exc