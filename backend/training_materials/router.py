from fastapi import APIRouter
from fastapi import Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_db

from training_materials import service
from training_materials.schemas import (
    TrainingMaterialResponse,TrainingMaterialUrlCreateRequest
)

router = APIRouter(
    prefix="/training-materials",
    tags=["Training Materials"]
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
    db: AsyncSession = Depends(get_db)
):
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
    url: str = Form(...),
    session_id: int = Form(...),
    user_id: int = Form(...),
    db: AsyncSession = Depends(get_db)
):
    return await service.create_material_from_url(
        db=db,
        title=title,
        url=url,
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
    url: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    return await service.update_material(
        db=db,
        material_id=material_id,
        title=title,
        file=file,
        url=url
    )

@router.delete(
    "/{material_id}"
)
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db)
):
    await service.delete_material(
        db=db,
        material_id=material_id
    )

    return {
        "detail": "Training material deleted"
    }