from typing import (
    Literal,
    NotRequired,
    TypedDict,
)


RouteName = Literal[
    "knowledge",
    "system",
]


class AgentSourceState(TypedDict):
    chunk_id: int
    document_id: int
    position: int
    similarity: float
    content: str


class AgentState(TypedDict):
    question: str
    
    routing_strategy: NotRequired[
    str
]

    routing_reason: NotRequired[
    str
]
    limit: NotRequired[int]

    min_similarity: NotRequired[
        float
    ]

    normalized_question: NotRequired[
        str
    ]

    route: NotRequired[
        RouteName
    ]

    handled_by: NotRequired[
        RouteName
    ]

    answer: NotRequired[str]

    sources: NotRequired[
        list[AgentSourceState]
    ]

    tool_used: NotRequired[str]