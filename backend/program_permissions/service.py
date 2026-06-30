from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import BadRequestException, ConflictException, NotFoundException
from models.program_permission import ProgramPermission, ProgramRoles
from program_permissions import repository


async def add_person_to_program(
    db: AsyncSession,
    user_id: int,
    program_id: int,
    role: ProgramRoles,
) -> ProgramPermission:
    try:
        await repository.get_user_by_id(db=db, user_id=user_id)
    except NoResultFound as exc:
        raise NotFoundException("User not found") from exc

    try:
        await repository.get_program_by_id(db=db, program_id=program_id)
    except NoResultFound as exc:
        raise NotFoundException("Program not found") from exc

    existing = await repository.get_existing_permission(
        db=db, user_id=user_id, program_id=program_id
    )
    if existing:
        raise ConflictException("User already has a role in this program")

    try:
        return await repository.create_permission(
            db=db,
            user_id=user_id,
            program_id=program_id,
            role=role,
        )
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to add person to program") from exc


async def is_user_in_program(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> bool:
    return await repository.is_user_in_program(db=db, user_id=user_id, program_id=program_id)


async def get_program_permissions(
    db: AsyncSession,
    program_id: int,
) -> list[dict]:
    permissions = await repository.get_permissions_by_program_id(
        db=db, program_id=program_id
    )
    result = []
    for perm in permissions:
        result.append({
            "permission_id": perm.id,
            "user_id": perm.user_id,
            "username": perm.user.username,
            "display_name": perm.user.display_name,
            "role": perm.role,
        })
    return result


async def delete_permission(
    db: AsyncSession,
    permission_id: int,
) -> None:
    try:
        permission = await repository.get_permission_by_id(db=db, permission_id=permission_id)
    except NoResultFound as exc:
        raise NotFoundException("Permission not found") from exc

    try:
        await repository.soft_delete_permission(db=db, permission=permission)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to delete permission") from exc
