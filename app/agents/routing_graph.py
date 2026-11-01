from collections.abc import (
    Awaitable,
    Callable,
)

from langchain_core.messages import (
    HumanMessage,
)
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


def record_question(
    state: AgentState,
) -> dict:
    return {
        "messages": [
            HumanMessage(
                content=state[
                    "normalized_question"
                ]
            )
        ],
        "sources": [],
        "tool_used": None,
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


def system_route(
    state: AgentState,
) -> dict:
    return {
        "handled_by": "system",
    }


NodeHandler = Callable[
    [AgentState],
    dict | Awaitable[dict],
]


def build_routing_graph(
    knowledge_handler: NodeHandler = (
        knowledge_route
    ),
    system_handler: NodeHandler = (
        system_route
    ),
    classifier_handler: NodeHandler = (
        classify_question
    ),
    checkpointer=None,
):
    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "normalize_question",
        normalize_question,
    )

    builder.add_node(
        "record_question",
        record_question,
    )

    builder.add_node(
        "classify_question",
        classifier_handler,
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
        "record_question",
    )

    builder.add_edge(
        "record_question",
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

    return builder.compile(
        checkpointer=checkpointer
    )


routing_graph = (
    build_routing_graph()
)