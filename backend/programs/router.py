from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from db.connection import get_db
from programs.service import create_program as create_program_service
from programs.service import delete_program as delete_program_service
from programs.service import get_program_progress as get_program_progress_service
from programs.service import update_program as update_program_service
from programs.schema import CreateProgramRequest, ProgramProgressItem, ProgramResponse, UpdateProgramRequest

router = APIRouter(prefix="/programs", tags=["programs"])


@router.get("/progress/{user_id}", response_model=list[ProgramProgressItem])
async def get_program_progress(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    return await get_program_progress_service(db=db, user_id=user_id)


@router.patch("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    payload: UpdateProgramRequest,
    db: AsyncSession = Depends(get_db),
):
    return await update_program_service(
        db=db,
        program_id=program_id,
        title=payload.title,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )


@router.delete("/{program_id}", status_code=204)
async def delete_program(
    program_id: int,
    db: AsyncSession = Depends(get_db),
):
    await delete_program_service(db=db, program_id=program_id)


@router.post("", response_model=ProgramResponse, status_code=201)
async def create_program(
    payload: CreateProgramRequest,
    current_user: TokenPayload = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await create_program_service(
        db=db,
        user_id=int(current_user.sub),
        title=payload.title,
        description=payload.description,
        start_date=payload.start_date,
        end_date=payload.end_date,
    )
