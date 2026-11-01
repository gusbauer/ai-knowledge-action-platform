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
from pydantic import Field
from pydantic.v1 import BaseModel
from app.schemas.agent import (
    AgentRequest,
    AgentResponse,
    AgentResumeRequest,
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
    interrupts = result.get(
        "__interrupt__",
        (),
    )

    if interrupts:
        pending = interrupts[0]

        return AgentResponse(
    thread_id=thread_id,
    status="completed",
    question=payload.question,
    answer=result["answer"],
    route=result["route"],
    handled_by=result[
        "handled_by"
    ],
    tool_used=result.get(
        "tool_used"
    ),
    sources=result.get(
        "sources",
        [],
    ),
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
        }
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