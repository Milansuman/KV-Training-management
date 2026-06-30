from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_db
from session_permissions.schema import AddSessionPermissionRequest, SessionPermissionResponse, SessionResponse, SessionUserResponse, SessionWithRoleResponse, UpdateSessionPermissionRequest
from session_permissions.service import add_session_permission, delete_session_permission, get_session_permissions_by_program, get_session_users, get_sessions_by_program, update_session_permission

router = APIRouter(prefix="/session-permissions", tags=["session-permissions"])


@router.get("/program/{program_id}", response_model=list[SessionResponse])
async def get_sessions(
    program_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_sessions_by_program(db=db, program_id=program_id)


@router.get("/program/{program_id}/user/{user_id}", response_model=list[SessionWithRoleResponse])
async def get_sessions_with_role(
    program_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_session_permissions_by_program(db=db, user_id=user_id, program_id=program_id)


@router.delete("/{permission_id}", status_code=204)
async def delete_permission(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_session_permission(db=db, permission_id=permission_id)


@router.patch("/{permission_id}", response_model=SessionPermissionResponse)
async def update_permission(
    permission_id: int,
    payload: UpdateSessionPermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    return await update_session_permission(db=db, permission_id=permission_id, role=payload.role)


@router.get("/session/{session_id}", response_model=list[SessionUserResponse])
async def get_users(
    session_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_session_users(db=db, session_id=session_id)


@router.post("", response_model=SessionPermissionResponse, status_code=201)
async def add_permission(
    payload: AddSessionPermissionRequest,
    db: AsyncSession = Depends(get_db),
):
    return await add_session_permission(
        db=db,
        user_id=payload.user_id,
        session_id=payload.session_id,
        role=payload.role,
    )
