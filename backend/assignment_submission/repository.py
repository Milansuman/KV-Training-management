from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundException
from models.assignment_submission import AssignmentSubmission
from .schemas import (
    AssignmentSubmissionCreateRequest,
    AssignmentSubmissionUpdateRequest,
)


async def create_submission(
    db: AsyncSession,
    body: AssignmentSubmissionCreateRequest
):

    db_submission = AssignmentSubmission(
        url=body.url.strip(),
        user_id=body.user_id,
        assignment_id=body.assignment_id
    )

    db.add(db_submission)

    await db.commit()
    await db.refresh(db_submission)

    return db_submission


async def get_submission_by_id(
    submission_id: int,
    db: AsyncSession
):

    stmt = (
        select(AssignmentSubmission)
        .where(AssignmentSubmission.deleted_at.is_(None))
        .where(AssignmentSubmission.id == submission_id)
    )

    result = await db.scalars(stmt)

    submission = result.first()

    if not submission:
        raise NotFoundException(
            detail="Submission not found"
        )

    return submission


async def get_submissions_by_assignment_id(
    assignment_id: int,
    db: AsyncSession
):

    stmt = (
        select(AssignmentSubmission)
        .where(AssignmentSubmission.deleted_at.is_(None))
        .where(AssignmentSubmission.assignment_id == assignment_id)
        .order_by(AssignmentSubmission.created_at)
    )

    result = await db.scalars(stmt)

    return result.all()


async def get_submissions_by_user_id(
    user_id: int,
    db: AsyncSession
):

    stmt = (
        select(AssignmentSubmission)
        .where(AssignmentSubmission.deleted_at.is_(None))
        .where(AssignmentSubmission.user_id == user_id)
        .order_by(AssignmentSubmission.created_at)
    )

    result = await db.scalars(stmt)

    return result.all()


async def patch_submission(
    submission_id: int,
    body: AssignmentSubmissionUpdateRequest,
    db: AsyncSession
):

    submission = await get_submission_by_id(
        submission_id,
        db
    )

    update_data = body.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        if isinstance(value, str):
            value = value.strip()
        setattr(submission, field, value)

    submission.updated_at = datetime.now(tz=UTC)

    await db.commit()
    await db.refresh(submission)

    return submission


async def delete_submission(
    submission_id: int,
    db: AsyncSession
):

    submission = await get_submission_by_id(
        submission_id,
        db
    )

    submission.deleted_at = datetime.now(tz=UTC)

    await db.commit()
    await db.refresh(submission)

    return submission