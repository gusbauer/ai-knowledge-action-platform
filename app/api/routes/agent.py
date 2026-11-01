from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)
from langgraph.types import (
    Command,
)
from pydantic import BaseModel, Field

from app.agents.dependencies import (
    get_agent_graph,
)
from app.core.config import settings
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
)
from app.services.rate_limiter import (
    check_rag_rate_limit,
)


class AgentResumeRequest(BaseModel):
    thread_id: str = Field(
        min_length=1,
        max_length=128,
    )

    approved: bool

    note: str | None = Field(
        default=None,
        max_length=500,
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

    config = {
        "configurable": {
            "thread_id": thread_id,
        },
        "run_name": "agent_request",
        "tags": [
            "agent",
            settings.agent_mode,
        ],
        "metadata": {
            "thread_id": thread_id,
            "agent_mode": (
                settings.agent_mode
            ),
        },
    }

    result = await graph.ainvoke(
        {
            "question": payload.question,
            "limit": payload.limit,
            "min_similarity": (
                payload.min_similarity
            ),
        },
        config=config,
    )

    interrupts = result.get(
        "__interrupt__",
        (),
    )

    if interrupts:
        pending = interrupts[0]

        return AgentResponse(
            thread_id=thread_id,
            status="interrupted",
            question=payload.question,
            interrupt={
                "id": pending.id,
                "value": pending.value,
            },
        )

    return AgentResponse(
        thread_id=thread_id,
        status="completed",
        question=payload.question,
        answer=result.get("answer"),
        route=result.get("route"),
        handled_by=result.get(
            "handled_by"
        ),
        tool_used=result.get(
            "tool_used"
        ),
        sources=result.get(
            "sources",
            [],
        ),
    )


@router.post(
    "/resume",
    response_model=AgentResponse,
)
async def resume_agent(
    payload: AgentResumeRequest,
    graph=Depends(get_agent_graph),
):
    config = {
        "configurable": {
            "thread_id": (
                payload.thread_id
            ),
        },
        "run_name": "agent_resume",
        "tags": [
            "agent",
            "human_in_the_loop",
        ],
        "metadata": {
            "thread_id": (
                payload.thread_id
            ),
            "agent_mode": (
                settings.agent_mode
            ),
        },
    }

    result = await graph.ainvoke(
        Command(
            resume={
                "approved": (
                    payload.approved
                ),
                "note": payload.note,
            }
        ),
        config=config,
    )

    interrupts = result.get(
        "__interrupt__",
        (),
    )

    if interrupts:
        pending = interrupts[0]

        return AgentResponse(
            thread_id=(
                payload.thread_id
            ),
            status="interrupted",
            question=result.get(
                "question"
            ),
            interrupt={
                "id": pending.id,
                "value": pending.value,
            },
        )

    return AgentResponse(
        thread_id=payload.thread_id,
        status="completed",
        question=result.get(
            "question"
        ),
        answer=result.get(
            "answer"
        ),
        route=result.get(
            "route"
        ),
        handled_by=result.get(
            "handled_by"
        ),
        tool_used=result.get(
            "tool_used"
        ),
        sources=result.get(
            "sources",
            [],
        ),
    )