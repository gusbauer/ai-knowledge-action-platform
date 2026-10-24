from functools import lru_cache

from fastapi.concurrency import run_in_threadpool
from sentence_transformers import SentenceTransformer


EMBEDDING_MODEL_NAME = (
    "sentence-transformers/"
    "paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_DIMENSION = 384


class EmbeddingGenerationError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        EMBEDDING_MODEL_NAME
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


async def generate_embeddings(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        raise EmbeddingGenerationError(
            "No text chunks were provided."
        )

    try:
        return await run_in_threadpool(
            _generate_embeddings_sync,
            texts,
        )

    except Exception as exc:
        raise EmbeddingGenerationError(
            "Embeddings could not be generated."
        ) from exc