from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.session_permission import SessionPermission
from models.session import Session, session_topic
from models.topic import Topic
from sqlalchemy.orm import selectinload, with_loader_criteria
from exceptions.exceptions import NotFoundException
from feedback import service as feedback_service
from models.program import Program
from models.program_permission import ProgramPermission
from models.session import Session

async def create_session(
    db: AsyncSession,
    session: Session
) -> Session:

    db.add(session)

    await db.commit()
    await db.refresh(session)

    return session

#get session by session id that is not deleted
async def get_session_by_id(
    db: AsyncSession,
    session_id: int
) -> Session:

    session = (
        await db.scalars(
            select(Session)
            .options(selectinload(Session.topics),with_loader_criteria(
                Topic,
                Topic.deleted_at.is_(None)
            ))
            .where(Session.id == session_id)
            .where(Session.deleted_at.is_(None))
        )
    ).one()

    return session

#get all sessions that are not deleted
async def get_sessions(
    db: AsyncSession
) -> list[Session]:

    sessions = (
        await db.scalars(
            select(Session)
            .where(Session.deleted_at.is_(None))
        )
    ).all()

    return list(sessions)

#get all sessions by program id that is not deleted
async def get_sessions_by_program_id(program_id: int, db: AsyncSession) -> list[Session]:

    sessions = (
        await db.scalars(
            select(Session)
            .where(Session.program_id == program_id)
            .where(Session.deleted_at.is_(None))
            .options(selectinload(Session.topics),with_loader_criteria(
                Topic,
                Topic.deleted_at.is_(None)
            ))

        )
    ).all()

    return list(sessions)


async def update_session(
    db: AsyncSession,
    session: Session
) -> Session:

    await db.commit()
    await db.refresh(session)

    return session


async def delete_session(
    db: AsyncSession,
    session: Session
) -> None:

    session.deleted_at = datetime.now(tz=UTC)
    try:
        await feedback_service.delete_feedback_by_session_id(
            db=db,
            session_id=session.id
        )
    except NotFoundException:
        pass

    await db.commit()



async def assign_topic_to_session(
    db: AsyncSession,
    session: Session,
    topic: Topic
) -> Session:

    if topic not in session.topics:
        session.topics.append(topic)

    await db.commit()
    await db.refresh(session)

    return session

async def remove_topic_from_session(
    db: AsyncSession,
    session: Session,
    topic: Topic
) -> Session:

    if topic in session.topics:
        session.topics.remove(topic)

    await db.commit()
    await db.refresh(session)

    return session

async def session_topic_exists(
    db: AsyncSession,
    session_id: int,
    topic_id: int
) -> bool:

    result = await db.execute(
        select(session_topic)
        .where(session_topic.c.session_id == session_id)
        .where(session_topic.c.topic_id == topic_id)
    )

    return result.first() is not None



async def get_today_sessions_for_user(
    db: AsyncSession,
    user_id: int
):
    
    result = await db.execute(
        select(
            Session.id.label("session_id"),
            Session.title.label("session_name"),
            Program.title.label("program_name"),
            Session.start_datetime,
            Session.end_datetime,
        )
        .join(
            Program,
            Session.program_id == Program.id
        )
        .join(
            ProgramPermission,
            (ProgramPermission.program_id == Program.id)
        )
        .join(
            SessionPermission,
            (SessionPermission.session_id == Session.id)
        )
        .where(ProgramPermission.user_id == user_id)
        .where(SessionPermission.user_id == user_id)
        .where(Program.deleted_at.is_(None))
        .where(Session.deleted_at.is_(None))
        .where(ProgramPermission.deleted_at.is_(None))
        .where(SessionPermission.deleted_at.is_(None))
        .where(Session.start_datetime >= datetime.now(tz=ZoneInfo("Asia/Kolkata")).replace(hour=0, minute=0, second=0, microsecond=0))
    )

    return result.all()


async def get_sessions_for_user(
    db: AsyncSession,
    user_id: int
):
    result = await db.execute(
        select(
            Session.id.label("session_id"),
            Session.title.label("session_name"),
            Program.title.label("program_name"),
            Session.start_datetime,
            Session.end_datetime,
        )
        .join(
            Program,
            Session.program_id == Program.id
        )
        .join(
            ProgramPermission,
            (ProgramPermission.program_id == Program.id)
        )
        .join(
            SessionPermission,
            (SessionPermission.session_id == Session.id)
        )
        .where(ProgramPermission.user_id == user_id)
        .where(SessionPermission.user_id == user_id)
        .where(Program.deleted_at.is_(None))
        .where(Session.deleted_at.is_(None))
        .where(ProgramPermission.deleted_at.is_(None))
        .where(SessionPermission.deleted_at.is_(None))
    )

    return result.all()

