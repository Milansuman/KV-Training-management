from langgraph.graph import StateGraph, END

from .nodes import (
    fetch_material,
    route_by_content_type,
    parse_binary,
    parse_html,
    clean_markdown,
    analyze_with_llm,
    handle_error,
)
from .state import AgentState


def build_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("fetch_material", fetch_material)
    graph.add_node("parse_binary", parse_binary)
    graph.add_node("parse_html", parse_html)
    graph.add_node("clean_markdown", clean_markdown)
    graph.add_node("analyze_with_llm", analyze_with_llm)
    graph.add_node("handle_error", handle_error)

    graph.set_entry_point("fetch_material")

    graph.add_conditional_edges(
        "fetch_material",
        route_by_content_type,
        {
            "parse_binary": "parse_binary",
            "parse_html": "parse_html",
            "error": "handle_error",
        },
    )

    graph.add_edge("parse_binary", "clean_markdown")
    graph.add_edge("parse_html", "clean_markdown")
    graph.add_edge("clean_markdown", "analyze_with_llm")
    graph.add_edge("analyze_with_llm", END)
    graph.add_edge("handle_error", END)

    return graph.compile()


agent = build_graph()
