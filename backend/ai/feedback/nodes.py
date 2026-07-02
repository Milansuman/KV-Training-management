import json

from openai import OpenAI
from sqlalchemy import and_, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from config import env
from models.feedback import Feedback
from models.feedback_submission import FeedbackSubmission
from models.session_permission import SessionPermission, SessionRoles

from .state import FeedbackSummaryState

# Role → which sender roles should be included in the summary
_VISIBLE_ROLES: dict[SessionRoles, list[SessionRoles]] = {
    SessionRoles.TRAINER: [SessionRoles.MODERATOR, SessionRoles.CANDIDATE],
    SessionRoles.CANDIDATE: [SessionRoles.TRAINER, SessionRoles.MODERATOR],
    SessionRoles.MODERATOR: [SessionRoles.TRAINER, SessionRoles.CANDIDATE, SessionRoles.MODERATOR],
}

_SYSTEM_PROMPT = """\
You are summarising feedback that a person has received from their peers.
You will be given feedback grouped by the sender's role.
For each role group, write a concise summary (2-4 sentences) that captures the key themes.
Return ONLY a JSON object where each key is a role name (lowercase) and the value is the summary string.
Example: {"trainer": "...", "moderator": "..."}
Do not include any text outside the JSON object.
"""


async def fetch_user_role(state: FeedbackSummaryState) -> FeedbackSummaryState:
    db: AsyncSession = state["db"]
    try:
        permission = (await db.scalars(
            select(SessionPermission)
            .where(SessionPermission.user_id == state["user_id"])
            .where(SessionPermission.session_id == state["session_id"])
            .where(SessionPermission.deleted_at.is_(None))
        )).first()

        if permission is None:
            return {
                **state,
                "error": f"User {state['user_id']} has no role in session {state['session_id']}",
                "error_code": "not_found",
            }

        return {**state, "user_role": permission.role.value}
    except Exception as exc:
        return {
            **state,
            "error": f"fetch_user_role failed: {exc}",
            "error_code": "internal_error",
        }


async def fetch_and_group_feedbacks(state: FeedbackSummaryState) -> FeedbackSummaryState:
    if state.get("error"):
        return state

    db: AsyncSession = state["db"]
    user_role = SessionRoles(state["user_role"])
    visible_sender_roles = _VISIBLE_ROLES[user_role]

    try:
        # Fetch all submissions addressed to this user within the session,
        # joined with the sender's session_permission to get their role.
        rows = (await db.execute(
            select(FeedbackSubmission.text, SessionPermission.role)
            .join(Feedback, FeedbackSubmission.feedback_id == Feedback.id)
            .join(
                SessionPermission,
                (SessionPermission.user_id == FeedbackSubmission.user_id)
                & (SessionPermission.session_id == Feedback.session_id),
            )
            .where(
                or_(
                    FeedbackSubmission.recipient_id == state["user_id"],
                    and_(
                        FeedbackSubmission.recipient_id.is_(None),
                        SessionPermission.role == SessionRoles.CANDIDATE
                    )
                )
            )
            .where(Feedback.session_id == state["session_id"])
            .where(FeedbackSubmission.deleted_at.is_(None))
            .where(SessionPermission.role.in_(visible_sender_roles))
        )).all()

        grouped: dict[str, list[str]] = {}
        for text, role in rows:
            key = role.value.lower()
            grouped.setdefault(key, []).append(text)

        if not grouped:
            return {
                **state,
                "error": "No feedback found for this user in the given session",
                "error_code": "no_feedback",
            }

        return {**state, "grouped_feedbacks": grouped}
    except Exception as exc:
        return {
            **state,
            "error": f"fetch_and_group_feedbacks failed: {exc}",
            "error_code": "internal_error",
        }


def summarize_feedbacks(state: FeedbackSummaryState) -> FeedbackSummaryState:
    if state.get("error"):
        return state

    grouped: dict[str, list[str]] = state["grouped_feedbacks"]

    feedback_text = "\n\n".join(
        f"[{role.upper()} FEEDBACK]\n" + "\n---\n".join(texts)
        for role, texts in grouped.items()
    )

    client = OpenAI(api_key=env.GROQ_API_KEY, base_url=env.GROQ_BASE_URL)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": feedback_text},
            ],
        )
        raw = (response.choices[0].message.content or "").strip()
        summaries = json.loads(raw)
        return {**state, "summaries": summaries}
    except Exception as exc:
        return {
            **state,
            "error": f"summarize_feedbacks failed: {exc}",
            "error_code": "internal_error",
        }


def handle_error(state: FeedbackSummaryState) -> FeedbackSummaryState:
    return state
