import logging
from sqlalchemy.ext.asyncio import AsyncSession

from user import repository as user_repo

from .schema import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


async def create_user(db: AsyncSession, body: UserCreate):
    try:
        user = await user_repo.create_user(db, body)
        return user
    except Exception as exc:
        logger.exception("Error creating user...")
        raise


async def get_all_users(db: AsyncSession):

    users = await user_repo.get_all_users(db)

    return users


async def get_user_by_id(id: int, db: AsyncSession):
    try:
        user = await user_repo.get_user_by_id(id, db)
        return user
    except Exception as exc:
        logger.exception("User not found...")
        raise


async def patch_user(id: int, body: UserUpdate, db: AsyncSession):
    try:
        user = await user_repo.patch_user(id, body, db)
        return user
    except Exception as exc:
        logger.exception("Error updating user...")
        raise


async def delete_user(id: int, db: AsyncSession):
    try:
        user = await user_repo.delete_user(id, db)
        return user
    except Exception as exc:
        logger.exception("Error deleting user...")
        raise
