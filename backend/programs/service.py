from datetime import date

from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import BadRequestException, ForbiddenException, NotFoundException
from models.program import Program
from models.program_permission import ProgramRoles
from programs import repository
from programs.schema import ProgramProgressItem


async def create_program(
    db: AsyncSession,
    user_id: int,
    title: str,
    description: str,
    start_date: date,
    end_date: date,
) -> Program:
    try:
        user = await repository.get_user_by_id(db=db, user_id=user_id)
    except NoResultFound as exc:
        raise NotFoundException("User not found") from exc

    if not user.is_admin:
        raise ForbiddenException("Only admins can create programs")

    try:
        program = await repository.create_program(
            db=db,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )

        await repository.create_program_permission(
            db=db,
            user_id=user_id,
            program_id=program.id,
            role=ProgramRoles.STAFF,
        )
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to create program") from exc

    return program


async def get_program_progress(
    db: AsyncSession,
    user_id: int,
) -> list[ProgramProgressItem]:
    try:
        programs = await repository.get_programs_by_user_id(db=db, user_id=user_id)
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to fetch programs") from exc

    result = []
    for program in programs:
        total, completed = await repository.get_session_counts_for_program(
            db=db,
            program_id=program.id,
        )
        result.append(ProgramProgressItem(
            id=program.id,
            title=program.title,
            description=program.description,
            total_sessions=total,
            completed_sessions=completed,
            created_at=program.created_at,
            updated_at=program.updated_at,
        ))

    return result


async def update_program(
    db: AsyncSession,
    program_id: int,
    title: str | None,
    description: str | None,
    start_date: date | None,
    end_date: date | None,
) -> Program:
    try:
        program = await repository.get_program_by_id(db=db, program_id=program_id)
    except NoResultFound as exc:
        raise NotFoundException("Program not found") from exc

    try:
        return await repository.update_program(
            db=db,
            program=program,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to update program") from exc


async def delete_program(db: AsyncSession, program_id: int) -> None:
    try:
        program = await repository.get_program_by_id(db=db, program_id=program_id)
    except NoResultFound as exc:
        raise NotFoundException("Program not found") from exc

    try:
        await repository.soft_delete_program(db=db, program=program)
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to delete program") from exc
