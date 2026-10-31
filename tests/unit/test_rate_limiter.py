import pytest
from redis.exceptions import RedisError

from app.services.rate_limiter import (
    check_rag_rate_limit,
)


class FakeRedis:
    def __init__(
        self,
        response=None,
        error=None,
    ):
        self.response = response
        self.error = error

    async def eval(
        self,
        *args,
    ):
        if self.error:
            raise self.error

        return self.response


@pytest.mark.asyncio
async def test_rate_limit_allows_request():
    redis = FakeRedis(
        response=[
            3,
            45,
        ]
    )

    result = await check_rag_rate_limit(
        "client-a",
        client=redis,
    )

    assert result.allowed is True
    assert result.remaining == 7
    assert result.retry_after == 45


@pytest.mark.asyncio
async def test_rate_limit_blocks_request():
    redis = FakeRedis(
        response=[
            11,
            30,
        ]
    )

    result = await check_rag_rate_limit(
        "client-a",
        client=redis,
    )

    assert result.allowed is False
    assert result.remaining == 0
    assert result.retry_after == 30


@pytest.mark.asyncio
async def test_rate_limit_fails_open():
    redis = FakeRedis(
        error=RedisError(
            "Redis unavailable"
        )
    )

    result = await check_rag_rate_limit(
        "client-a",
        client=redis,
    )

    assert result.allowed is True
    assert result.fail_open is True