from pydantic import BaseModel

from langchain_core.tools import (
    tool,
)
from langgraph.types import (
    interrupt,
)

from app.services.query_embedding_cache import (
    clear_cached_query_embeddings,
)


class CacheClearApproval(BaseModel):
    approved: bool
    note: str | None = None


@tool
async def clear_embedding_cache() -> str:
    """
    Clear cached query embeddings.

    This administrative action requires
    explicit human approval.
    """

    decision = interrupt(
        {
            "action": (
                "clear_embedding_cache"
            ),
            "message": (
                "¿Quieres borrar la "
                "caché de embeddings?"
            ),
        },
        response_schema=(
            CacheClearApproval
        ),
    )

    if not decision.approved:
        return (
            "Cache clearing cancelled "
            "by the user."
        )

    deleted = (
        await clear_cached_query_embeddings()
    )

    return (
        f"Query embedding cache cleared. "
        f"{deleted} keys deleted."
    )