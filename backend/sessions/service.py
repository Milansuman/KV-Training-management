from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundException

from models.session import Session

from sessions import repository
# from programs import repository as program_repository


async def create_session(
    db: AsyncSession,
    title: str,
    description: str,
    start_datetime,
    end_datetime,
    program_id: int
):

    # try:
    #     await program_repository.get_program_by_id(
    #         db=db,
    #         program_id=program_id
    #     )
    # except NoResultFound:
    #     raise NotFoundException(
    #         "Program not found"
    #     )

    session = Session(
        title=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        program_id=program_id
    )

    return await repository.create_session(
        db=db,
        session=session
    )

#get session by session id that is not deleted
async def get_session(
    db: AsyncSession,
    session_id: int
):

    try:
        return await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        raise NotFoundException(
            "Session not found"
        )

#get all sessions that are not deleted
async def get_sessions(
    db: AsyncSession
):
    return await repository.get_sessions(
        db=db
    )

#get all sessions by program id that is not deleted
async def get_sessions_by_program_id(program_id: int, db: AsyncSession):
    return await repository.get_sessions_by_program_id(
        db=db,
        program_id=program_id
    )

async def update_session(
    db: AsyncSession,
    session_id: int,
    title: str,
    description: str,
    start_datetime,
    end_datetime
):

    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        raise NotFoundException(
            "Session not found"
        )

    session.title = title
    session.description = description

    session.start_datetime = start_datetime
    session.end_datetime = end_datetime

    return await repository.update_session(
        db=db,
        session=session
    )


async def delete_session(
    db: AsyncSession,
    session_id: int
):

    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        raise NotFoundException(
            "Session not found"
        )

    await repository.delete_session(
        db=db,
        session=session
    )