from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.exceptions import UnprocessableEntityException
from exceptions import NotFoundException
from topics import repository as topic_repository

from models.session import Session

from sessions import repository
# from programs import repository as program_repository

import logging

logger = logging.getLogger(__name__)
async def create_session(
    db: AsyncSession,
    title: str,
    description: str,
    start_datetime,
    end_datetime,
    program_id: int
):
    if end_datetime <= start_datetime:
        raise UnprocessableEntityException(
            "end_datetime must be after start_datetime"
        )

    session = Session(
        title=title,
        description=description,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        program_id=program_id
    )

    created_session = await repository.create_session(
        db=db,
        session=session
    )

    # Create a feedback entry for this session
    from feedback.service import create_feedback as create_feedback_service
    feedback = await create_feedback_service(
        db=db,
        session_id=created_session.id
    )

    created_session.feedback_id = feedback.id

    return created_session

#get session by session id that is not deleted
async def get_session(
    db: AsyncSession,
    session_id: int
):

    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )

        # Attach feedback_id from the associated feedback record
        from feedback.service import get_feedback_by_session_id
        feedback = await get_feedback_by_session_id(
            db=db,
            session_id=session_id
        )
        if feedback:
            session.feedback_id = feedback.id

        return session
    except NoResultFound:
        logger.exception("Session not found...")
        raise NotFoundException(
            "Session not found"
        )

#get all sessions that are not deleted
async def get_sessions(
    db: AsyncSession
):
    sessions = await repository.get_sessions(
        db=db
    )

    # Attach feedback_id for each session
    from feedback.service import get_feedback_by_session_id
    for session in sessions:
        feedback = await get_feedback_by_session_id(
            db=db,
            session_id=session.id
        )
        if feedback:
            session.feedback_id = feedback.id

    return sessions

#get all sessions by program id that is not deleted
async def get_sessions_by_program_id(program_id: int, db: AsyncSession):
    sessions = await repository.get_sessions_by_program_id(
        db=db,
        program_id=program_id
    )

    # Attach feedback_id for each session
    from feedback.service import get_feedback_by_session_id
    for session in sessions:
        feedback = await get_feedback_by_session_id(
            db=db,
            session_id=session.id
        )
        if feedback:
            session.feedback_id = feedback.id

    return sessions

async def update_session(
    db: AsyncSession,
    session_id: int,
    title: str,
    description: str,
    start_datetime,
    end_datetime
):
    if end_datetime <= start_datetime:
        raise UnprocessableEntityException(
            "end_datetime must be after start_datetime"
        )

    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        logger.exception("Session not found during update...")
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
        logger.exception("Session not found during delete...")
        raise NotFoundException(
            "Session not found"
        )

    await repository.delete_session(
        db=db,
        session=session
    )

async def assign_topic_to_session(
    db: AsyncSession,
    session_id: int,
    topic_id: int
):
    exists = await repository.session_topic_exists(
        db=db,
        session_id=session_id,
        topic_id=topic_id
    )

    if exists:
        raise UnprocessableEntityException(
            "Topic already attached to session"
        )
    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        logger.exception("Session not found during attach topic to session...")
        raise NotFoundException(
            "Session not found"
        )
    try:
        topic = await topic_repository.get_topic_by_id(
            db=db,
            topic_id=topic_id
        )
    except NoResultFound:
        logger.exception("Topic not found during attach topic to session...")
        raise NotFoundException(
            "Topic not found"
        )

    return await repository.assign_topic_to_session(
        db=db,
        session=session,
        topic=topic
    )

async def remove_topic_from_session(
    db: AsyncSession,
    session_id: int,
    topic_id: int
):
    exists = await repository.session_topic_exists(
        db=db,
        session_id=session_id,
        topic_id=topic_id
    )

    if not exists:
        raise NotFoundException(
            "Topic is not attached to this session"
        )
    try:
        session = await repository.get_session_by_id(
            db=db,
            session_id=session_id
        )
    except NoResultFound:
        logger.exception("Session not found during detach topic from session...")
        raise NotFoundException(
            "Session not found"
        )
    try:
        topic = await topic_repository.get_topic_by_id(
            db=db,
            topic_id=topic_id
        )
    except NoResultFound:
        logger.exception("Topic not found during detach topic from session...")
        raise NotFoundException(
            "Topic not found"
        )

    return await repository.remove_topic_from_session(
        db=db,
        session=session,
        topic=topic
    )

async def get_sessions_for_user(
    db: AsyncSession,
    user_id: int
):
    rows = await repository.get_sessions_for_user(
        db=db,
        user_id=user_id
    )

    return [
        {
            "session_id": row.session_id,
            "session_name": row.session_name,
            "program_name": row.program_name,
            "start_datetime": row.start_datetime,
            "end_datetime": row.end_datetime,
        }
        for row in rows
    ]


async def get_today_sessions_for_user(
    db: AsyncSession,
    user_id: int
):
    rows = await repository.get_today_sessions_for_user(
        db=db,
        user_id=user_id
    )

    return [
        {
            "session_id": row.session_id,
            "session_name": row.session_name,
            "program_name": row.program_name,
            "start_datetime": row.start_datetime,
            "end_datetime": row.end_datetime,
        }
        for row in rows
    ]