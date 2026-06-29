from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.utils import hash_password
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