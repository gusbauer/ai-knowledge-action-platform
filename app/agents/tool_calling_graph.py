import json

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import (
    tool,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
)
from langgraph.prebuilt import (
    ToolNode,
)

from app.agents.agent_graph import (
    RAGAnswerService,
)
from app.agents.state import (
    AgentState,
)
from app.agents.tools.system_info import (
    get_system_info,
)


TOOL_AGENT_SYSTEM_PROMPT = """
You are the AI agent for the
AI Knowledge & Action Platform.

You have tools available.

Use get_system_info when the user asks
about this platform, its version,
environment, status or metadata.

Use search_knowledge when the user asks
a question that should be answered from
uploaded documents or the knowledge base.

Use the tool results as evidence.

Do not invent information that is not
available in the tools.

You may answer directly only for simple
conversation that does not require
platform or document information.
""".strip()


def build_tool_calling_graph(
    rag_service,
    model,
    checkpointer=None,
):
    @tool
    async def search_knowledge(
        question: str,
    ) -> str:
        """
        Search uploaded documents for
        information relevant to a question.
        """

        matches = await rag_service.retrieve(
            question=question,
            limit=5,
            min_similarity=0.25,
        )

        sources = []

        for chunk, distance in matches:
            sources.append(
                {
                    "chunk_id": chunk.id,
                    "document_id": (
                        chunk.document_id
                    ),
                    "position": (
                        chunk.position
                    ),
                    "similarity": (
                        1.0
                        - float(distance)
                    ),
                    "content": (
                        chunk.content
                    ),
                }
            )

        return json.dumps(
            {
                "sources": sources,
            },
            ensure_ascii=False,
        )

    tools = [
        get_system_info,
        search_knowledge,
    ]

    model_with_tools = (
        model.bind_tools(
            tools
        )
    )

    async def record_question(
        state: AgentState,
    ) -> dict:
        return {
            "messages": [
                HumanMessage(
                    content=state[
                        "question"
                    ]
                )
            ],
            "sources": [],
            "tool_used": None,
        }

    async def call_model(
        state: AgentState,
    ) -> dict:
        response = (
            await model_with_tools
            .ainvoke(
                [
                    SystemMessage(
                        content=(
                            TOOL_AGENT_SYSTEM_PROMPT
                        )
                    ),
                    *state["messages"],
                ]
            )
        )

        update = {
            "messages": [
                response
            ],
        }

        if not response.tool_calls:
            content = response.content

            update["answer"] = (
                content
                if isinstance(
                    content,
                    str,
                )
                else str(content)
            )

        return update

    def should_continue(
        state: AgentState,
    ):
        last_message = (
            state["messages"][-1]
        )

        if (
            isinstance(
                last_message,
                AIMessage,
            )
            and last_message.tool_calls
        ):
            return "tools"

        return END

    def capture_tool_result(
        state: AgentState,
    ) -> dict:
        tool_call_message = next(
            message
            for message in reversed(
                state["messages"]
            )
            if (
                isinstance(
                    message,
                    AIMessage,
                )
                and message.tool_calls
            )
        )

        tool_names = [
            call["name"]
            for call in (
                tool_call_message
                .tool_calls
            )
        ]

        updates = {
            "tool_used": ",".join(
                tool_names
            ),
        }

        if (
            "search_knowledge"
            in tool_names
        ):
            updates[
                "route"
            ] = "knowledge"

            updates[
                "handled_by"
            ] = "knowledge"

            for message in reversed(
                state["messages"]
            ):
                if not isinstance(
                    message,
                    ToolMessage,
                ):
                    continue

                try:
                    payload = json.loads(
                        message.content
                    )

                except (
                    json.JSONDecodeError,
                    TypeError,
                ):
                    continue

                if "sources" in payload:
                    updates[
                        "sources"
                    ] = payload[
                        "sources"
                    ]

                    break

        elif (
            "get_system_info"
            in tool_names
        ):
            updates[
                "route"
            ] = "system"

            updates[
                "handled_by"
            ] = "system"

        return updates

    builder = StateGraph(
        AgentState
    )

    builder.add_node(
        "record_question",
        record_question,
    )

    builder.add_node(
        "agent",
        call_model,
    )

    builder.add_node(
        "tools",
        ToolNode(tools),
    )

    builder.add_node(
        "capture_tool_result",
        capture_tool_result,
    )

    builder.add_edge(
        START,
        "record_question",
    )

    builder.add_edge(
        "record_question",
        "agent",
    )

    builder.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END,
        },
    )

    builder.add_edge(
        "tools",
        "capture_tool_result",
    )

    builder.add_edge(
        "capture_tool_result",
        "agent",
    )

    return builder.compile(
        checkpointer=checkpointer
    )