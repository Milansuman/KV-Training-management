from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.program_permission import ProgramPermission, ProgramRoles
from models.user import User
from models.program import Program


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    return (await db.scalars(
        select(User)
        .where(User.id == user_id)
        .where(User.deleted_at.is_(None))
    )).one()


async def get_program_by_id(db: AsyncSession, program_id: int) -> Program:
    return (await db.scalars(
        select(Program)
        .where(Program.id == program_id)
        .where(Program.deleted_at.is_(None))
    )).one()


async def get_existing_permission(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> ProgramPermission | None:
    return (await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.user_id == user_id)
        .where(ProgramPermission.program_id == program_id)
    )).first()


async def is_user_in_program(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> bool:
    permission = (await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.user_id == user_id)
        .where(ProgramPermission.program_id == program_id)
        .where(ProgramPermission.deleted_at.is_(None))
    )).first()
    return permission is not None


async def get_permission_by_id(
    db: AsyncSession,
    permission_id: int,
) -> ProgramPermission:
    return (await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.id == permission_id)
        .where(ProgramPermission.deleted_at.is_(None))
    )).one()


async def soft_delete_permission(
    db: AsyncSession,
    permission: ProgramPermission,
) -> None:
    permission.deleted_at = datetime.now(UTC)
    await db.commit()


async def create_permission(
    db: AsyncSession,
    user_id: int,
    program_id: int,
    role: ProgramRoles,
) -> ProgramPermission:
    permission = ProgramPermission(
        user_id=user_id,
        program_id=program_id,
        role=role,
    )
    db.add(permission)
    await db.commit()
    return permission


async def get_permissions_by_program_id(
    db: AsyncSession,
    program_id: int,
) -> list[ProgramPermission]:
    result = await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.program_id == program_id)
        .where(ProgramPermission.deleted_at.is_(None))
    )
    return list(result.all())


async def update_permission_role(
    db: AsyncSession,
    permission: ProgramPermission,
    role: ProgramRoles,
) -> ProgramPermission:
    permission.role = role
    await db.commit()
    return permission
