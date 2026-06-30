import logging
from sqlalchemy.ext.asyncio import AsyncSession

from user import repository as user_repo

from .schema import UserCreate, UserUpdate, UserProgramStatusResponse, SessionRoleInfo

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


async def get_user_program_status(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> UserProgramStatusResponse:
    user = await user_repo.get_user_by_id(user_id, db)

    program_permission = await user_repo.get_user_program_permission(
        db, user_id, program_id
    )

    session_rows = await user_repo.get_user_session_roles_for_program(
        db, user_id, program_id
    )

    session_roles = [
        SessionRoleInfo(
            session_id=session.id,
            session_title=session.title,
            role=role,
        )
        for session, role in session_rows
    ]

    return UserProgramStatusResponse(
        is_admin=user.is_admin,
        program_role=program_permission.role if program_permission else None,
        session_roles=session_roles,
    )
