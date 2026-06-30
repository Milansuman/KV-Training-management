from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from assignment_submission import repository
import user.repository as user_repository
from exceptions import NotFoundException
from .schemas import (
    AssignmentSubmissionCreateRequest,
    AssignmentSubmissionUpdateRequest,
)
from exceptions import ConflictException
from assignment import repository as assignment_repository

async def create_submission(
    body: AssignmentSubmissionCreateRequest,
    db: AsyncSession,
):
    user = await user_repository.get_user_by_id(
        db=db,
        id=body.user_id,
    )

    assignment = await assignment_repository.get_assignment_by_id(
        assignment_id=body.assignment_id,
        db=db)

    if user is None:
        raise NotFoundException(detail="User not found.")

    if assignment is None:
        raise NotFoundException(detail="Assignment not found.")

    try:
        return await repository.create_submission(
            db=db,
            body=body,
        )
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="You have already submitted this assignment."
        )


async def get_submission_by_id(
    submission_id: int,
    db: AsyncSession
):
    return await repository.get_submission_by_id(
        submission_id=submission_id,
        db=db
    )


async def get_submissions_by_assignment_id(
    assignment_id: int,
    db: AsyncSession
):
    assignment = await assignment_repository.get_assignment_by_id(
        assignment_id=assignment_id,
        db=db
    )  
    if assignment is None:
        raise NotFoundException(detail="Assignment not found.")
    return await repository.get_submissions_by_assignment_id(
        assignment_id=assignment_id,
        db=db
    )


async def get_submissions_by_user_id(
    user_id: int,
    db: AsyncSession
):
    user = await user_repository.get_user_by_id(
        db=db,
        id=user_id,
    )

    if user is None:
        raise NotFoundException(detail="User not found.")

    return await repository.get_submissions_by_user_id(
        user_id=user_id,
        db=db,
    )


async def patch_submission(
    submission_id: int,
    body: AssignmentSubmissionUpdateRequest,
    db: AsyncSession
):
    return await repository.patch_submission(
        submission_id=submission_id,
        body=body,
        db=db
    )


async def delete_submission(
    submission_id: int,
    db: AsyncSession
):
    return await repository.delete_submission(
        submission_id=submission_id,
        db=db
    )