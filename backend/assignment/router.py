from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from db.connection import get_db
from exceptions.exceptions import UnauthorizedException

from assignment import service
from assignment.schema import (
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
    AssignmentResponse
)

router = APIRouter(
    prefix="/assignments",
    tags=["Assignments"]
)


@router.post(
    "",
    response_model=AssignmentResponse
)
async def create_assignment(
    body: AssignmentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    return await service.create_assignment(
        body=body,
        db=db
    )


@router.get(
    "",
    response_model=list[AssignmentResponse]
)
async def get_all_assignments(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_all_assignments(
        db=db
    )


@router.get(
    "/{assignment_id}",
    response_model=AssignmentResponse
)
async def get_assignment_by_id(
    assignment_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_assignment_by_id(
        assignment_id=assignment_id,
        db=db
    )


@router.get(
    "/session/{session_id}",
    response_model=list[AssignmentResponse]
)
async def get_assignments_by_session_id(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_assignments_by_session_id(
        session_id=session_id,
        db=db
    )


@router.patch(
    "/{assignment_id}",
    response_model=AssignmentResponse
)
async def patch_assignment(
    assignment_id: int,
    body: AssignmentUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    return await service.patch_assignment(
        assignment_id=assignment_id,
        body=body,
        db=db
    )


@router.delete(
    "/{assignment_id}"
)
async def delete_assignment(
    assignment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    await service.delete_assignment(
        assignment_id=assignment_id,
        db=db
    )

    return {
        "message": "Assignment deleted successfully"
    }