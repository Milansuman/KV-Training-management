from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from models.user import User

async def create_user(
    db: AsyncSession,
    username: str,
    display_name: str,
    email: str,
    password: str | None = None,
    google_sub: str | None = None,
    is_admin: bool = False
) -> User:
    user = User(
        username=username,
        display_name=display_name,
        email=email,
        password=password,
        google_sub=google_sub,
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


async def get_user_by_email(
    db: AsyncSession,
    email: str
) -> User:
    user = (await db.scalars(
        select(User)
        .where(User.email == email)
        .where(User.deleted_at.is_(None))
    )).one()

    return user


async def get_user_by_google_sub(
    db: AsyncSession,
    google_sub: str
) -> User:
    user = (await db.scalars(
        select(User)
        .where(User.google_sub == google_sub)
        .where(User.deleted_at.is_(None))
    )).one()

    return user


async def link_google_sub(
    db: AsyncSession,
    user: User,
    google_sub: str
) -> User:
    user.google_sub = google_sub
    await db.commit()
    return user


async def set_nonce(
    db: AsyncSession,
    user: User,
    nonce: str | None
) -> User:
    user.nonce = nonce
    await db.commit()
    return user


async def get_user_by_nonce(
    db: AsyncSession,
    nonce: str
) -> User:
    user = (await db.scalars(
        select(User)
        .where(User.nonce == nonce)
        .where(User.deleted_at.is_(None))
    )).one()

    return user
