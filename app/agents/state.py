from typing import (
    Literal,
    NotRequired,
    TypedDict,
)


RouteName = Literal[
    "knowledge",
    "system",
]


class AgentState(TypedDict):
    question: str

    normalized_question: NotRequired[
        str
    ]

    route: NotRequired[
        RouteName
    ]

    handled_by: NotRequired[
        RouteName
    ]