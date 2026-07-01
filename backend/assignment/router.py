from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from db.connection import get_db
from exceptions.exceptions import UnauthorizedException
from models.session_permission import SessionPermission, SessionRoles

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


async def _can_manage_assignment(
    db: AsyncSession,
    current_user: TokenPayload,
    session_id: int,
) -> bool:
    if current_user.is_admin:
        return True

    result = await db.execute(
        select(SessionPermission).where(
            SessionPermission.user_id == int(current_user.sub),
            SessionPermission.session_id == session_id,
            SessionPermission.deleted_at.is_(None),
            SessionPermission.role == SessionRoles.TRAINER,
        )
    )
    return result.scalar_one_or_none() is not None


@router.post(
    "",
    response_model=AssignmentResponse
)
async def create_assignment(
    body: AssignmentCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not await _can_manage_assignment(db, current_user, body.session_id):
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
    assignment = await service.get_assignment_by_id(
        assignment_id=assignment_id,
        db=db
    )

    if not await _can_manage_assignment(db, current_user, assignment.session_id):
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
    assignment = await service.get_assignment_by_id(
        assignment_id=assignment_id,
        db=db
    )

    if not await _can_manage_assignment(db, current_user, assignment.session_id):
        raise UnauthorizedException("Action not allowed")

    await service.delete_assignment(
        assignment_id=assignment_id,
        db=db
    )

    return {
        "message": "Assignment deleted successfully"
    }