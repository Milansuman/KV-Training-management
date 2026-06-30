from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from db.connection import get_db
from exceptions.exceptions import UnauthorizedException

from assignment_submission import service
from .schemas import (
    AssignmentSubmissionCreateRequest,
    AssignmentSubmissionUpdateRequest,
    AssignmentSubmissionResponse,
)

router = APIRouter(
    prefix="/assignment-submissions",
    tags=["Assignment Submissions"]
)


@router.post(
    "",
    response_model=AssignmentSubmissionResponse
)
async def create_submission(
    body: AssignmentSubmissionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    return await service.create_submission(
        body=body,
        db=db
    )


@router.get(
    "/{submission_id}",
    response_model=AssignmentSubmissionResponse
)
async def get_submission_by_id(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_submission_by_id(
        submission_id=submission_id,
        db=db
    )


@router.get(
    "/assignment/{assignment_id}",
    response_model=list[AssignmentSubmissionResponse]
)
async def get_submissions_by_assignment_id(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_submissions_by_assignment_id(
        assignment_id=assignment_id,
        db=db
    )


@router.get(
    "/user/{user_id}",
    response_model=list[AssignmentSubmissionResponse]
)
async def get_submissions_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_submissions_by_user_id(
        user_id=user_id,
        db=db
    )


@router.patch(
    "/{submission_id}",
    response_model=AssignmentSubmissionResponse
)
async def patch_submission(
    submission_id: int,
    body: AssignmentSubmissionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    return await service.patch_submission(
        submission_id=submission_id,
        body=body,
        db=db
    )


@router.delete(
    "/{submission_id}"
)
async def delete_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    await service.delete_submission(
        submission_id=submission_id,
        db=db
    )

    return {
        "message": "Submission deleted successfully"
    }