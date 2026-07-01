from fastapi import APIRouter
from fastapi import Depends, File, Form, UploadFile
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from exceptions.exceptions import ForbiddenException, UnauthorizedException
from models.session_permission import SessionRoles
from db.connection import get_db

from training_materials import service,repository
from training_materials.schemas import (
    TrainingMaterialResponse,TrainingMaterialUrlCreateRequest
)

router = APIRouter(
    prefix="/training-materials",
    tags=["Training Materials"]
)

async def verify_trainer_role_for_session(
    db: AsyncSession,
    user_id: int,
    session_id: int,
) -> None:
    """
    Verify that a user has trainer role for a specific session.
    Raises ForbiddenException if user doesn't have trainer role.
    """
    from session_permissions import repository
    
    permission = await repository.get_existing_session_permission(
        db=db,
        user_id=user_id,
        session_id=session_id,
    )
    
    if permission is None or permission.role != SessionRoles.TRAINER:
        raise ForbiddenException(
            "Only trainers and admins can perform this action"
        )

@router.post(
    "",
    response_model=TrainingMaterialResponse
)
async def upload_material(
    title: str = Form(...),
    session_id: int = Form(...),
    user_id: int = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)

):
    if not current_user.is_admin:
        await verify_trainer_role_for_session(
            db=db,
            user_id=int(current_user.sub),
            session_id=session_id,
        )
    return await service.upload_material(
        db=db,
        title=title,
        session_id=session_id,
        user_id=user_id,
        file=file
    )

@router.post(
    "/url",
    response_model=TrainingMaterialResponse,
)
async def create_material_from_url(
    title: str = Form(...),
    url: HttpUrl = Form(...),
    session_id: int = Form(...),
    user_id: int = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)

):
    if not current_user.is_admin:
        await verify_trainer_role_for_session(
            db=db,
            user_id=int(current_user.sub),
            session_id=session_id,
        )
    return await service.create_material_from_url(
        db=db,
        title=title,
        url=str(url) if url else None,
        session_id=session_id,
        user_id=user_id,
    )

@router.get(
    "",
    response_model=list[TrainingMaterialResponse]
)
async def get_materials(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_materials(db=db)


@router.get(
    "/{session_id}",
    response_model=list[TrainingMaterialResponse]
)
async def get_material(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_material(
        db=db,
        session_id=session_id
    )

@router.put(
    "/{material_id}",
    response_model=TrainingMaterialResponse
)
async def update_material(
    material_id: int,
    title: str = Form(...),
    file: UploadFile | None = File(None),
    url: HttpUrl | None = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)

):
    session_id = await repository.get_session_id(db=db, material_id=material_id)
    if session_id is None:
        raise ForbiddenException(
            "Material not found or has been deleted"
        )
    if not current_user.is_admin:
        await verify_trainer_role_for_session(
            db=db,
            user_id=int(current_user.sub),
            session_id=session_id,
        )
    
    
    return await service.update_material(
        db=db,
        material_id=material_id,
        title=title,
        file=file,
        url=str(url) if url else None
    )

@router.delete(
    "/{material_id}"
)
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)

):
    session_id = await repository.get_session_id(db=db, material_id=material_id)
    if session_id is None:
        raise ForbiddenException(
            "Material not found or has been deleted"
        )
    if not current_user.is_admin:
        await verify_trainer_role_for_session(
            db=db,
            user_id=int(current_user.sub),
            session_id=session_id,
        )
    await service.delete_material(
        db=db,
        material_id=material_id
    )

    return {
        "detail": "Training material deleted"
    }