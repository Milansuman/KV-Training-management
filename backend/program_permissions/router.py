from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_db
from program_permissions.schema import AddPersonRequest, ProgramPermissionResponse, UserInProgramResponse
from program_permissions.service import add_person_to_program, delete_permission, is_user_in_program

router = APIRouter(prefix="/program-permissions", tags=["program-permissions"])


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
