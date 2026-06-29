from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import NotFoundException
from topics import repository
from models.topic import Topic


async def create_topic(
    db: AsyncSession,
    title: str
) -> Topic:

    return await repository.create_topic(
        db=db,
        title=title
    )


async def get_topic(
    db: AsyncSession,
    topic_id: int
) -> Topic:

    try:
        return await repository.get_topic_by_id(
            db=db,
            topic_id=topic_id
        )
    except NoResultFound as exc:
        raise NotFoundException(
            "Topic not found"
        ) from exc


async def get_topics(
    db: AsyncSession
):
    return await repository.get_all_topics(
        db=db
    )


async def update_topic(
    db: AsyncSession,
    topic_id: int,
    title: str
):

    try:
        topic = await repository.get_topic_by_id(
            db=db,
            topic_id=topic_id
        )

        return await repository.update_topic(
            db=db,
            topic=topic,
            title=title
        )

    except NoResultFound as exc:
        raise NotFoundException(
            "Topic not found"
        ) from exc


async def delete_topic(
    db: AsyncSession,
    topic_id: int
):

    try:
        topic = await repository.get_topic_by_id(
            db=db,
            topic_id=topic_id
        )

        await repository.delete_topic(
            db=db,
            topic=topic
        )

    except NoResultFound as exc:
        raise NotFoundException(
            "Topic not found"
        ) from exc