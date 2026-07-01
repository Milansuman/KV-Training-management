from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_db
from program_permissions.schema import (
    AddPersonRequest,
    ProgramPermissionResponse,
    ProgramPermissionUserResponse,
    UpdatePersonRequest,
    UserInProgramResponse,
)
from program_permissions.service import (
    add_person_to_program,
    delete_permission,
    get_program_permissions,
    is_user_in_program,
    update_permission_role,
)

router = APIRouter(prefix="/program-permissions", tags=["program-permissions"])


@router.get("/program/{program_id}", response_model=list[ProgramPermissionUserResponse])
async def list_program_permissions(
    program_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_program_permissions(db=db, program_id=program_id)


@router.get("/check", response_model=UserInProgramResponse)
async def check_user_in_program(
    user_id: int,
    program_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await is_user_in_program(db=db, user_id=user_id, program_id=program_id)
    return UserInProgramResponse(is_member=result)


@router.delete("/{permission_id}", status_code=204)
async def remove_person(
    permission_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_permission(db=db, permission_id=permission_id)


@router.patch("/{permission_id}", response_model=ProgramPermissionResponse)
async def update_person(
    permission_id: int,
    payload: UpdatePersonRequest,
    db: AsyncSession = Depends(get_db),
):
    return await update_permission_role(
        db=db,
        permission_id=permission_id,
        role=payload.role,
    )


@router.post("", response_model=ProgramPermissionResponse, status_code=201)
async def add_person(
    payload: AddPersonRequest,
    db: AsyncSession = Depends(get_db),
):
    return await add_person_to_program(
        db=db,
        user_id=payload.user_id,
        program_id=payload.program_id,
        role=payload.role,
    )
