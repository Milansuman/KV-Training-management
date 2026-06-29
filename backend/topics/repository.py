from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.topic import Topic
from datetime import UTC, datetime


async def create_topic(
    db: AsyncSession,
    title: str
) -> Topic:

    topic = Topic(
        title=title
    )

    db.add(topic)

    await db.commit()
    await db.refresh(topic)

    return topic


async def get_topic_by_id(
    db: AsyncSession,
    topic_id: int
) -> Topic:

    topic = (
        await db.scalars(
            select(Topic)
            .where(Topic.id == topic_id)
            .where(Topic.deleted_at.is_(None))
        )
    ).one()

    return topic


async def get_all_topics(
    db: AsyncSession
) -> list[Topic]:

    topics = (
        await db.scalars(
            select(Topic)
            .where(Topic.deleted_at.is_(None))
            .order_by(Topic.title)
        )
    ).all()

    return list(topics)


async def update_topic(
    db: AsyncSession,
    topic: Topic,
    title: str
) -> Topic:

    topic.title = title

    await db.commit()
    await db.refresh(topic)

    return topic


async def delete_topic(
    db: AsyncSession,
    topic: Topic
) -> None:

    topic.deleted_at = datetime.now(tz=UTC)
    await db.commit()
    await db.refresh(topic)