from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from uuid import uuid4

from app.agents.dependencies import (
    get_agent_graph,
)
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
)
from app.services.rate_limiter import (
    check_rag_rate_limit,
)


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post(
    "/ask",
    response_model=AgentResponse,
)
async def ask_agent(
    payload: AgentRequest,
    request: Request,
    response: Response,
    graph=Depends(get_agent_graph),
):
    client_identifier = (
        request.client.host
        if request.client
        else "unknown"
    )

    decision = await check_rag_rate_limit(
        client_identifier
    )

    headers = {
        "X-RateLimit-Limit": str(
            decision.limit
        ),
        "X-RateLimit-Remaining": str(
            decision.remaining
        ),
        "X-RateLimit-Reset": str(
            decision.retry_after
        ),
    }

    if not decision.allowed:
        raise HTTPException(
            status_code=(
                status.HTTP_429_TOO_MANY_REQUESTS
            ),
            detail=(
                "Agent request rate limit exceeded."
            ),
            headers={
                **headers,
                "Retry-After": str(
                    decision.retry_after
                ),
            },
        )

    for key, value in headers.items():
        response.headers[key] = value

    thread_id = (
    payload.thread_id
    or uuid4().hex
)
    result = await graph.ainvoke(
    {
        "question": payload.question,
        "limit": payload.limit,
        "min_similarity": (
            payload.min_similarity
        ),
    },
    config={
        "configurable": {
        "thread_id": thread_id,
        }
    },
)

    return AgentResponse(
        question=payload.question,
        answer=result["answer"],
        route=result["route"],
        handled_by=result[
            "handled_by"
        ],
        thread_id=thread_id,
        tool_used=result.get(
            "tool_used"
        ),
        sources=result.get(
            "sources",
            [],
        ),
    )