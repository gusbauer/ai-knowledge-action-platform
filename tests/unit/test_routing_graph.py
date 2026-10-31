from app.agents.routing_graph import (
    routing_graph,
)


def test_routes_knowledge_question():
    result = routing_graph.invoke(
        {
            "question": (
                "¿Qué es RAG?"
            ),
        }
    )

    assert (
        result["route"]
        == "knowledge"
    )

    assert (
        result["handled_by"]
        == "knowledge"
    )


def test_routes_system_question():
    result = routing_graph.invoke(
        {
            "question": (
                "¿Qué versión tiene "
                "el sistema?"
            ),
        }
    )

    assert (
        result["route"]
        == "system"
    )

    assert (
        result["handled_by"]
        == "system"
    )


def test_normalizes_question():
    result = routing_graph.invoke(
        {
            "question": (
                "   ¿Qué   es RAG?   "
            ),
        }
    )

    assert (
        result[
            "normalized_question"
        ]
        == "¿Qué es RAG?"
    )