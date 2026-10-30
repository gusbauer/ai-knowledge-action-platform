import hashlib
import json
import logging

from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_client
from app.services.embedding_service import (
    EMBEDDING_MODEL_NAME,
    generate_query_embeddings,
)


logger = logging.getLogger(
    "app.cache"
)


def _build_cache_key(
    text: str,
) -> str:
    value = (
        f"{EMBEDDING_MODEL_NAME}:{text}"
    )

    digest = hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()

    return (
        f"query_embedding:{digest}"
    )


async def _get_cached_embedding(
    text: str,
) -> list[float] | None:
    key = _build_cache_key(text)

    try:
        cached = await redis_client.get(
            key
        )

    except RedisError:
        logger.exception(
            "query_embedding_cache_read_failed"
        )
        return None

    if cached is None:
        return None

    return [
        float(value)
        for value in json.loads(cached)
    ]


async def _store_embedding(
    text: str,
    embedding: list[float],
) -> None:
    key = _build_cache_key(text)

    try:
        await redis_client.setex(
            key,
            settings.query_embedding_cache_ttl_seconds,
            json.dumps(embedding),
        )

    except RedisError:
        logger.exception(
            "query_embedding_cache_write_failed"
        )


async def generate_cached_query_embeddings(
    texts: list[str],
) -> list[list[float]]:
    results: list[
        list[float] | None
    ] = []

    missing_indices: list[int] = []
    missing_texts: list[str] = []

    for index, text in enumerate(
        texts
    ):
        cached = (
            await _get_cached_embedding(
                text
            )
        )

        results.append(cached)

        if cached is None:
            missing_indices.append(
                index
            )

            missing_texts.append(
                text
            )

    if missing_texts:
        generated = (
            await generate_query_embeddings(
                missing_texts
            )
        )

        for (
            index,
            text,
            embedding,
        ) in zip(
            missing_indices,
            missing_texts,
            generated,
            strict=True,
        ):
            results[index] = embedding

            await _store_embedding(
                text,
                embedding,
            )

    return [
        embedding
        for embedding in results
        if embedding is not None
    ]