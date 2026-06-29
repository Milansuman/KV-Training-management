from sqlalchemy.ext.asyncio import AsyncSession

from user import repository as user_repo

from .schema import (
    UserCreate,
    UserUpdate
)



async def create_user(
    db: AsyncSession,
    body: UserCreate
):

    user = await user_repo.create_user(
        db,
        body
    )

    return user



async def get_all_users(
    db: AsyncSession
):

    users = await user_repo.get_all_users(
        db
    )

    return users



async def get_user_by_id(
    id: int,
    db: AsyncSession
):

    user = await user_repo.get_user_by_id(
        id,
        db
    )

    return user



async def patch_user(
    id: int,
    body: UserUpdate,
    db: AsyncSession
):

    user = await user_repo.patch_user(
        id,
        body,
        db
    )

    return user


async def delete_user(
    id: int,
    db: AsyncSession
):

    user = await user_repo.delete_user(
        id,
        db
    )

    return user