from langgraph.graph import StateGraph, END

from .nodes import fetch_and_group_feedbacks, fetch_user_role, handle_error, summarize_feedbacks
from .state import FeedbackSummaryState


def _route_after_role(state: FeedbackSummaryState) -> str:
    return "error" if state.get("error") else "fetch_and_group_feedbacks"


def _route_after_group(state: FeedbackSummaryState) -> str:
    return "error" if state.get("error") else "summarize_feedbacks"


def build_graph():
    g = StateGraph(FeedbackSummaryState)

    g.add_node("fetch_user_role", fetch_user_role)
    g.add_node("fetch_and_group_feedbacks", fetch_and_group_feedbacks)
    g.add_node("summarize_feedbacks", summarize_feedbacks)
    g.add_node("error", handle_error)

    g.set_entry_point("fetch_user_role")

    g.add_conditional_edges("fetch_user_role", _route_after_role, {
        "fetch_and_group_feedbacks": "fetch_and_group_feedbacks",
        "error": "error",
    })
    g.add_conditional_edges("fetch_and_group_feedbacks", _route_after_group, {
        "summarize_feedbacks": "summarize_feedbacks",
        "error": "error",
    })

    g.add_edge("summarize_feedbacks", END)
    g.add_edge("error", END)

    return g.compile()


agent = build_graph()
