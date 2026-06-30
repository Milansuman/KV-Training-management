from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession


from auth.utils import hash_password
from models.program_permission import ProgramPermission
from models.session import Session
from models.session_permission import SessionPermission, SessionRoles
from models.user import User
from .schema import UserCreate, UserUpdate
from exceptions import ConflictException, NotFoundException


async def create_user(
    db: AsyncSession,
    body: UserCreate
):

    db_user = User(
        username=body.username.strip(),
        display_name=body.display_name.strip(),
        email=body.email.strip(),
        password=hash_password(body.password),
        is_admin=body.is_admin
    )
    db.add(db_user)
    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail=f"Email '{body.email}' is already in use"
        )

    await db.refresh(db_user)
    return db_user



async def get_all_users(
    db: AsyncSession
):
    stmt = (
        select(User).where(User.deleted_at.is_(None))
    )
    result = await db.scalars(stmt)
    return result.all()



async def get_user_by_id(
    id: int,
    db: AsyncSession
):

    stmt = (
        select(User)
        .where(User.deleted_at.is_(None))
        .where(User.id == id)
    )
    result = await db.scalars(stmt)
    user = result.first()
    if not user:
        raise NotFoundException(
            detail=f"User not found {id}"
        )
    return user



async def patch_user(
    id: int,
    body: UserUpdate,
    db: AsyncSession
):

    stmt = (
        select(User)
        .where(User.deleted_at.is_(None))
        .where(User.id == id)
    )

    result = await db.scalars(stmt)
    db_user = result.first()
    if not db_user:
        raise NotFoundException(
            detail="User not found"
        )


    update_data = body.model_dump(
        exclude_unset=True
    )

    if "password" in update_data and update_data["password"] is not None:
        update_data["password"] = hash_password(update_data["password"])

    for field, value in update_data.items():
        setattr(db_user, field, value)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise ConflictException(
            detail="Email already exists"
        )


    await db.refresh(db_user)

    return db_user


async def delete_user(
    id: int,
    db: AsyncSession
):
    stmt = (
        select(User)
        .where(User.deleted_at.is_(None))
        .where(User.id == id)
    )

    result = await db.scalars(stmt)
    db_user = result.first()
    if not db_user:
        raise NotFoundException(
            detail="User not found"
        )

    db_user.deleted_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_program_permission(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> ProgramPermission | None:
    result = await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.user_id == user_id)
        .where(ProgramPermission.program_id == program_id)
        .where(ProgramPermission.deleted_at.is_(None))
    )
    return result.first()


async def get_user_session_roles_for_program(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> list[tuple[Session, SessionRoles | None]]:
    rows = await db.execute(
        select(Session, SessionPermission.role)
        .outerjoin(
            SessionPermission,
            (SessionPermission.session_id == Session.id) &
            (SessionPermission.user_id == user_id) &
            (SessionPermission.deleted_at.is_(None)),
        )
        .where(Session.program_id == program_id)
        .where(Session.deleted_at.is_(None))
    )
    return [(row[0], row[1]) for row in rows.all()]