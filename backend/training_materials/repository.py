from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.training_material import TrainingMaterial


async def create_material(
    db: AsyncSession,
    material: TrainingMaterial
) -> TrainingMaterial:

    db.add(material)

    await db.commit()
    await db.refresh(material)

    return material


async def get_material_by_id(
    db: AsyncSession,
    session_id: int
) -> TrainingMaterial:

    material = (
        await db.scalars(
            select(TrainingMaterial)
            .where(TrainingMaterial.session_id == session_id)
            .where(TrainingMaterial.deleted_at.is_(None))
        )
    ).all()

    return material


async def get_materials(
    db: AsyncSession
) -> list[TrainingMaterial]:

    materials = (
        await db.scalars(
            select(TrainingMaterial)
            .where(TrainingMaterial.deleted_at.is_(None))
        )
    ).all()

    return list(materials)

async def get_material_by_material_id(
    db: AsyncSession,
    material_id: int
) -> TrainingMaterial | None:

    return await db.scalar(
        select(TrainingMaterial)
        .where(TrainingMaterial.id == material_id)
        .where(TrainingMaterial.deleted_at.is_(None))
    )

async def update_material(
    db: AsyncSession,
    material: TrainingMaterial
) -> TrainingMaterial:

    await db.commit()
    await db.refresh(material)

    return material

async def delete_material(
    db: AsyncSession,
    material: TrainingMaterial
) -> None:

    material.deleted_at = datetime.now(UTC)

    await db.commit()