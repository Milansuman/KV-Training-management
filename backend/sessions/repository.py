from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.session import Session, session_topic
from models.topic import Topic
from sqlalchemy.orm import selectinload, with_loader_criteria

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