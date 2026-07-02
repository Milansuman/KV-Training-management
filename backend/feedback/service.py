from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission
from models.session_permission import SessionPermission, SessionRoles
from feedback import repository
from sqlalchemy.exc import NoResultFound

from exceptions.exceptions import NotFoundException

async def create_feedback(
    db: AsyncSession,
    session_id: int,
    type: FeedbackType = FeedbackType.TEXT,
    url: Optional[str] = None
) -> Feedback:

    feedback = Feedback(
        session_id=session_id,
        type=type,
        url=url
    )

    return await repository.create_feedback(
        db=db,
        feedback=feedback
    )


async def get_feedback_by_session_id(
    db: AsyncSession,
    session_id: int
) -> Feedback | None:

    return await repository.get_feedback_by_session_id(
        db=db,
        session_id=session_id
    )


async def get_submissions_by_session_id(
    db: AsyncSession,
    session_id: int,
    current_user_id: int,
    is_admin: bool
) -> list[FeedbackSubmission]:

    submissions = await repository.get_submissions_by_session_id(
        db=db,
        session_id=session_id
    )

    # Admins see all feedback
    if is_admin:
        return submissions

    # Fetch all session permissions to determine roles
    result = await db.scalars(
        select(SessionPermission)
        .where(SessionPermission.session_id == session_id)
        .where(SessionPermission.deleted_at.is_(None))
    )
    session_permissions = list(result.all())

    user_role_map = {p.user_id: p.role for p in session_permissions}
    current_role = user_role_map.get(current_user_id)

    # Same visibility rules as ai/feedback/nodes.py
    _VISIBLE_ROLES: dict[SessionRoles, list[SessionRoles]] = {
        SessionRoles.TRAINER: [SessionRoles.MODERATOR],
        SessionRoles.CANDIDATE: [SessionRoles.TRAINER, SessionRoles.MODERATOR],
        SessionRoles.MODERATOR: [SessionRoles.TRAINER, SessionRoles.CANDIDATE, SessionRoles.MODERATOR],
    }

    # Users with no role see only general feedback (not addressed to anyone specific)
    if current_role is None:
        return [s for s in submissions if s.recipient_id is None]

    visible_sender_roles = _VISIBLE_ROLES[current_role]

    # Build set of user_ids whose role is visible to the current user
    visible_sender_ids = {
        p.user_id for p in session_permissions
        if p.role in visible_sender_roles
    }

    return [
        s for s in submissions
        if s.recipient_id is None  # General feedback is visible to all
        or s.user_id in visible_sender_ids  # Feedback from visible senders
    ]

async def delete_feedback_by_session_id(
    db: AsyncSession,
    session_id: int
):
    feedback = await get_feedback_by_session_id(
        db=db,
        session_id=session_id
    )

    if feedback is None:
        raise NotFoundException(
            "Feedback not found"
        )

    await repository.delete_feedback(
        db=db,
        feedback=feedback
    )
