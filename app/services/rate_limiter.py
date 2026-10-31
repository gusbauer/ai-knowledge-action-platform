import hashlib
import logging
from dataclasses import dataclass

from app.core.metrics import (
    RATE_LIMIT_DECISIONS,
)
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.redis import redis_client


logger = logging.getLogger(
    "app.rate_limit"
)


RATE_LIMIT_SCRIPT = """
local current = redis.call("INCR", KEYS[1])

if current == 1 then
    redis.call(
        "EXPIRE",
        KEYS[1],
        ARGV[1]
    )
end

local ttl = redis.call(
    "TTL",
    KEYS[1]
)

return {current, ttl}
"""


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    retry_after: int
    fail_open: bool = False


def _build_rate_limit_key(
    identifier: str,
) -> str:
    digest = hashlib.sha256(
        identifier.encode("utf-8")
    ).hexdigest()

    return (
        f"rate_limit:rag:{digest}"
    )


async def check_rag_rate_limit(
    identifier: str,
    client=redis_client,
) -> RateLimitDecision:
    limit = (
        settings.rag_rate_limit_requests
    )

    window = (
        settings.rag_rate_limit_window_seconds
    )

    key = _build_rate_limit_key(
        identifier
    )

    try:
        current, ttl = await client.eval(
            RATE_LIMIT_SCRIPT,
            1,
            key,
            window,
        )

    except RedisError:
        logger.exception(
            "rate_limit_check_failed"
        )
        RATE_LIMIT_DECISIONS.labels(
            decision="fail_open"
        ).inc()
        return RateLimitDecision(
            allowed=True,
            limit=limit,
            remaining=limit,
            retry_after=0,
            fail_open=True,
        )

    current = int(current)
    ttl = max(int(ttl), 0)

    remaining = max(
        limit - current,
        0,
    )
    decision_name = (
        "allowed"
        if current <= limit
        else "blocked"
    )

    RATE_LIMIT_DECISIONS.labels(
        decision=decision_name
    ).inc()
    return RateLimitDecision(
        allowed=current <= limit,
        limit=limit,
        remaining=remaining,
        retry_after=ttl,
    )