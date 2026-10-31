from collections.abc import (
    Awaitable,
    Callable,
)
from langchain_protocol import NotRequired, TypedDict
from langgraph.graph import (
    END,
    START,
    StateGraph,
)

from app.agents.state import (
    AgentState,
    RouteName,
)


SYSTEM_KEYWORDS = (
    "health",
    "status",
    "version",
    "estado",
    "salud",
    "versión",
)


class AgentState(TypedDict):
    question: str

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

    class AgentSourceState:
        ...

    sources: NotRequired[
        list[AgentSourceState]
    ]    
    chunk_id: int
    document_id: int
    position: int
    similarity: float
    content: str
def normalize_question(
    state: AgentState,
) -> dict:
    normalized = " ".join(
        state["question"]
        .strip()
        .split()
    )

    return {
        "normalized_question": normalized,
    }


def classify_question(
    state: AgentState,
) -> dict:
    question = state[
        "normalized_question"
    ].lower()

    route: RouteName

    if any(
        keyword in question
        for keyword in SYSTEM_KEYWORDS
    ):
        route = "system"

    else:
        route = "knowledge"

    return {
        "route": route,
    }


def select_route(
    state: AgentState,
) -> RouteName:
    return state["route"]


def knowledge_route(
    state: AgentState,
) -> dict:
    return {
        "handled_by": "knowledge",
    }
NodeHandler = Callable[
    [AgentState],
    dict | Awaitable[dict],
]

def system_route(
    state: AgentState,
) -> dict:
    return {
        "handled_by": "system",
    }
    
def build_routing_graph(
    knowledge_handler: NodeHandler = knowledge_route,
    system_handler: NodeHandler = system_route,
):
    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "normalize_question",
        normalize_question,
    )

    builder.add_node(
        "classify_question",
        classify_question,
    )

    builder.add_node(
        "knowledge_route",
        knowledge_handler,
    )

    builder.add_node(
        "system_route",
        system_handler,
    )

    builder.add_edge(
        START,
        "normalize_question",
    )

    builder.add_edge(
        "normalize_question",
        "classify_question",
    )

    builder.add_conditional_edges(
        "classify_question",
        select_route,
        {
            "knowledge": (
                "knowledge_route"
            ),
            "system": (
                "system_route"
            ),
        },
    )

    builder.add_edge(
        "knowledge_route",
        END,
    )

    builder.add_edge(
        "system_route",
        END,
    )

    return builder.compile()


routing_graph = (
    build_routing_graph()
)