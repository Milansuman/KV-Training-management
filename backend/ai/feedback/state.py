from typing import Any, Optional
from typing_extensions import TypedDict


class FeedbackSummaryState(TypedDict):
    # Inputs
    user_id: int
    session_id: int
    db: Any  # AsyncSession — passed in-process, not serialised

    # Populated by fetch_user_role
    user_role: Optional[str]  # "TRAINER" | "MODERATOR" | "CANDIDATE"

    # Populated by fetch_and_group_feedbacks
    # Keys are lowercase role names; values are lists of feedback text strings
    grouped_feedbacks: Optional[dict]

    # Populated by summarize_feedbacks
    # Same keys as grouped_feedbacks; values are summary strings
    summaries: Optional[dict]

    error: Optional[str]

    # Machine-readable code for the router to map to HTTP status
    # e.g. "not_found", "no_feedback", "internal_error"
    error_code: Optional[str]
