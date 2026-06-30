from io import BytesIO
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exceptions import BadRequestException, NotFoundException
from config import env
from models.training_material import TrainingMaterial
from storage.minio import client,delete_object
from training_materials.constants import MaterialType
from training_materials import repository
import logging

logger = logging.getLogger(__name__)

async def upload_material(
    db: AsyncSession,
    title: str,
    session_id: int,
    user_id: int,
    file: UploadFile
):
    object_name = f"{uuid4()}-{file.filename}"

    data = await file.read()

    client.put_object(
        bucket_name=env.MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type=file.content_type
    )

    url = (
        f"http://{env.MINIO_ENDPOINT}/"
        f"{env.MINIO_BUCKET}/{object_name}"
    )

    material = TrainingMaterial(
        title=title,
        url=url,
        material_type=MaterialType.FILE.value,
        session_id=session_id,
        user_id=user_id
    )

    return await repository.create_material(
        db=db,
        material=material
    )

async def create_material_from_url(
    db: AsyncSession,
    title: str,
    url: str,
    session_id: int,
    user_id: int,
):
    material = TrainingMaterial(
        title=title,
        url=url,
        material_type=MaterialType.URL.value,
        session_id=session_id,
        user_id=user_id,
    )

    return await repository.create_material(
        db=db,
        material=material,
    )

async def get_materials(
    db: AsyncSession
):
    return await repository.get_materials(db=db)


async def get_material(
    db: AsyncSession,
    session_id: int
):
    material =  await repository.get_material_by_id(
        db=db,
        session_id=session_id
    )
    if material is None or material == []:
        logger.exception(f"Material for Session {session_id} not found...")
        raise NotFoundException(
            "Training material not found"
        )
    return material

async def update_material(
    db: AsyncSession,
    material_id: int,
    title: str,
    file: UploadFile | None = None,
    url: str | None = None
):
    material = await repository.get_material_by_material_id(
        db=db,
        material_id=material_id
    )

    if material is None:
        logger.exception(f"Material with ID {material_id} not found...")
        raise NotFoundException(
            "Training material not found"
        )

    if file and url:
        logger.exception(f"Both file and url provided for material with ID {material_id}...")
        raise BadRequestException(
            "Provide either file or url"
        )

    if not file and not url:
        logger.exception(f"No file or url provided for material with ID {material_id}...")
        raise BadRequestException(
            "File or url is required"
        )

    material.title = title

    if file:

        if material.material_type == MaterialType.FILE.value:
            object_name = material.url.split("/")[-1]

            delete_object(object_name)

        data = await file.read()

        object_name = (
            f"{uuid4()}-{file.filename}"
        )

        client.put_object(
            bucket_name=env.MINIO_BUCKET,
            object_name=object_name,
            data=BytesIO(data),
            length=len(data),
            content_type=file.content_type
        )

        material.url = (
            f"http://{env.MINIO_ENDPOINT}/"
            f"{env.MINIO_BUCKET}/{object_name}"
        )

        material.material_type = MaterialType.FILE.value

    else:

        if material.material_type == MaterialType.FILE.value:
            object_name = material.url.split("/")[-1]

            delete_object(object_name)

        material.url = url
        material.material_type = MaterialType.URL.value

    return await repository.update_material(
        db=db,
        material=material
    )

async def delete_material(
    db: AsyncSession,
    material_id: int
):
    material = await repository.get_material_by_material_id(
        db=db,
        material_id=material_id
    )

    if material is None:
        logger.exception(f"Material with ID {material_id} not found...")
        raise NotFoundException(
            "Training material not found"
        )

    if material.material_type == MaterialType.FILE.value:
        object_name = material.url.split("/")[-1]

        delete_object(object_name)

    await repository.delete_material(
        db=db,
        material=material
    )