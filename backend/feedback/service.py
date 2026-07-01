from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission
from models.session_permission import SessionPermission, SessionRoles
from feedback import repository


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

    # Fetch all session permissions to determine roles
    result = await db.scalars(
        select(SessionPermission)
        .where(SessionPermission.session_id == session_id)
        .where(SessionPermission.deleted_at.is_(None))
    )
    session_permissions = list(result.all())

    user_role_map = {p.user_id: p.role for p in session_permissions}
    current_role = user_role_map.get(current_user_id)

    # Admins and moderators see all feedback
    if is_admin or current_role == SessionRoles.MODERATOR:
        return submissions

    candidate_ids = {
        p.user_id for p in session_permissions
        if p.role == SessionRoles.CANDIDATE
    }

    # Trainers: general feedback + submissions involving candidates + their own/received
    if current_role == SessionRoles.TRAINER:
        return [
            s for s in submissions
            if s.recipient_id is None
            or s.user_id == current_user_id
            or s.recipient_id == current_user_id
            or s.user_id in candidate_ids
            or (s.recipient_id is not None and s.recipient_id in candidate_ids)
        ]

    # Candidates / no role: only general, their own, or addressed to them
    return [
        s for s in submissions
        if s.recipient_id is None
        or s.user_id == current_user_id
        or s.recipient_id == current_user_id
    ]
