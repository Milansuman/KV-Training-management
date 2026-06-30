from datetime import date, datetime, UTC

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.program import Program
from models.program_permission import ProgramPermission, ProgramRoles
from models.session import Session
from models.user import User


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    user = (await db.scalars(
        select(User)
        .where(User.id == user_id)
        .where(User.deleted_at.is_(None))
    )).one()
    return user


async def create_program(
    db: AsyncSession,
    title: str,
    description: str,
    start_date: date,
    end_date: date,
) -> Program:
    program = Program(
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
    )
    db.add(program)
    await db.commit()
    return program


async def get_programs_by_user_id(db: AsyncSession, user_id: int) -> list[Program]:
    programs = (await db.scalars(
        select(Program)
        .join(ProgramPermission, ProgramPermission.program_id == Program.id)
        .where(ProgramPermission.user_id == user_id)
        .where(ProgramPermission.deleted_at.is_(None))
        .where(Program.deleted_at.is_(None))
    )).all()
    return list(programs)


async def get_session_counts_for_program(
    db: AsyncSession,
    program_id: int,
) -> tuple[int, int]:
    now = datetime.now(UTC)
    total = await db.scalar(
        select(func.count())
        .select_from(Session)
        .where(Session.program_id == program_id)
        .where(Session.deleted_at.is_(None))
    )
    completed = await db.scalar(
        select(func.count())
        .select_from(Session)
        .where(Session.program_id == program_id)
        .where(Session.deleted_at.is_(None))
        .where(Session.end_datetime <= now)
    )
    return (total or 0, completed or 0)


async def get_program_by_id(db: AsyncSession, program_id: int) -> Program:
    program = (await db.scalars(
        select(Program)
        .where(Program.id == program_id)
        .where(Program.deleted_at.is_(None))
    )).one()
    return program


async def soft_delete_program(db: AsyncSession, program: Program) -> None:
    program.deleted_at = datetime.now(UTC)
    await db.commit()


async def update_program(
    db: AsyncSession,
    program: Program,
    title: str | None,
    description: str | None,
    start_date: date | None,
    end_date: date | None,
) -> Program:
    if title is not None:
        program.title = title
    if description is not None:
        program.description = description
    if start_date is not None:
        program.start_date = start_date
    if end_date is not None:
        program.end_date = end_date
    program.updated_at = datetime.now(UTC)
    await db.commit()
    return program


async def create_program_permission(
    db: AsyncSession,
    user_id: int,
    program_id: int,
    role: ProgramRoles = ProgramRoles.STAFF,
) -> ProgramPermission:
    permission = ProgramPermission(
        user_id=user_id,
        program_id=program_id,
        role=role,
    )
    db.add(permission)
    await db.commit()
    return permission
