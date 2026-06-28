from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from models.user import User

async def create_user(
    db: AsyncSession,
    username: str,
    display_name: str,
    email: str,
    password: str,
    is_admin: bool = False
) -> User:
    user = User(
        username=username,
        display_name=display_name,
        email=email,
        password=password,
        is_admin=is_admin
    )

    db.add(user)
    await db.commit()
    return user

async def get_user_count(
    db: AsyncSession
) -> int:
    count = await db.scalar(
        select(func.count())
        .select_from(User) # Where clause unecessary. This function will only be used to ensure the first user is admin
    )

    return count #type: ignore

async def get_user_by_credentials(
    db: AsyncSession,
    username_or_email: str,
    password: str
) -> User:
    user = (await db.scalars(
        select(User)
        .where(
            or_(
                User.username == username_or_email,
                User.email == username_or_email
            )
        )
        .where(User.password == password)
        .where(
            User.deleted_at.is_(None)
        )
    )).one()

    return user

async def get_user_by_id(
    db: AsyncSession,
    user_id: int
) -> User:
    user = (await db.scalars(
        select(User)
        .where(
            User.id == user_id
        )
        .where(
            User.deleted_at.is_(None)
        )
    )).one()

    return user
