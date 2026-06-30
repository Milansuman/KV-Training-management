from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.program_permission import ProgramPermission
from models.session import Session
from models.session_permission import SessionPermission, SessionRoles
from models.user import User


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    return (await db.scalars(
        select(User)
        .where(User.id == user_id)
        .where(User.deleted_at.is_(None))
    )).one()


async def get_session_by_id(db: AsyncSession, session_id: int) -> Session:
    return (await db.scalars(
        select(Session)
        .where(Session.id == session_id)
        .where(Session.deleted_at.is_(None))
    )).one()


async def get_program_permission(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> ProgramPermission | None:
    return (await db.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.user_id == user_id)
        .where(ProgramPermission.program_id == program_id)
        .where(ProgramPermission.deleted_at.is_(None))
    )).first()


async def get_existing_session_permission(
    db: AsyncSession,
    user_id: int,
    session_id: int,
) -> SessionPermission | None:
    return (await db.scalars(
        select(SessionPermission)
        .where(SessionPermission.user_id == user_id)
        .where(SessionPermission.session_id == session_id)
    )).first()


async def get_session_permissions_by_program_id(
    db: AsyncSession,
    user_id: int,
    program_id: int,
) -> list[tuple[Session, SessionRoles | None]]:
    rows = (await db.execute(
        select(Session, SessionPermission.role)
        .outerjoin(
            SessionPermission,
            (SessionPermission.session_id == Session.id) &
            (SessionPermission.user_id == user_id),
        )
        .where(Session.program_id == program_id)
        .where(Session.deleted_at.is_(None))
    )).all()
    return [(row[0], row[1]) for row in rows]


async def get_sessions_by_program_id(
    db: AsyncSession,
    program_id: int,
) -> list[Session]:
    sessions = (await db.scalars(
        select(Session)
        .where(Session.program_id == program_id)
        .where(Session.deleted_at.is_(None))
    )).all()
    return list(sessions)


async def get_session_permission_by_id(
    db: AsyncSession,
    permission_id: int,
) -> SessionPermission:
    return (await db.scalars(
        select(SessionPermission)
        .where(SessionPermission.id == permission_id)
    )).one()


async def soft_delete_session_permission(
    db: AsyncSession,
    permission: SessionPermission,
) -> None:
    permission.deleted_at = datetime.now(UTC)
    await db.commit()


async def update_session_permission_role(
    db: AsyncSession,
    permission: SessionPermission,
    role: SessionRoles,
) -> SessionPermission:
    permission.role = role
    await db.commit()
    return permission


async def create_session_permission(
    db: AsyncSession,
    user_id: int,
    session_id: int,
    role: SessionRoles,
) -> SessionPermission:
    permission = SessionPermission(
        user_id=user_id,
        session_id=session_id,
        role=role,
    )
    db.add(permission)
    await db.commit()
    return permission
