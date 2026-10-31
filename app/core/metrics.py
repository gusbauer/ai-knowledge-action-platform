from prometheus_client import (
    Counter,
    Histogram,
)


HTTP_REQUESTS = Counter(
    "ai_platform_http_requests",
    "Total HTTP requests.",
    [
        "method",
        "path",
        "status_code",
    ],
)


HTTP_REQUEST_DURATION_SECONDS = (
    Histogram(
        "ai_platform_http_request_duration_seconds",
        "HTTP request duration in seconds.",
        [
            "method",
            "path",
        ],
    )
)


QUERY_EMBEDDING_CACHE_EVENTS = Counter(
    "ai_platform_query_embedding_cache_events",
    "Query embedding cache events.",
    [
        "event",
    ],
)


RATE_LIMIT_DECISIONS = Counter(
    "ai_platform_rate_limit_decisions",
    "RAG rate limiting decisions.",
    [
        "decision",
    ],
)