import pytest
from datetime import UTC, datetime

from topics import repository
from models.topic import Topic


@pytest.mark.asyncio
async def test_create_topic_returns_topic_with_id(db_session) -> None:
    topic = await repository.create_topic(
        db=db_session,
        title="Python Basics"
    )

    assert topic.id is not None
    assert topic.title == "Python Basics"
    assert topic.deleted_at is None


@pytest.mark.asyncio
async def test_create_topic_persists_to_database(db_session) -> None:
    await repository.create_topic(
        db=db_session,
        title="Advanced Python"
    )

    topics = await repository.get_all_topics(db=db_session)
    assert len(topics) == 1
    assert topics[0].title == "Advanced Python"


@pytest.mark.asyncio
async def test_get_topic_by_id_returns_topic(db_session) -> None:
    created_topic = await repository.create_topic(
        db=db_session,
        title="Web Development"
    )

    topic = await repository.get_topic_by_id(
        db=db_session,
        topic_id=created_topic.id
    )

    assert topic.id == created_topic.id
    assert topic.title == "Web Development"


@pytest.mark.asyncio
async def test_get_topic_by_id_raises_for_nonexistent_topic(db_session) -> None:
    with pytest.raises(Exception):  # NoResultFound
        await repository.get_topic_by_id(
            db=db_session,
            topic_id=999
        )


@pytest.mark.asyncio
async def test_get_topic_by_id_does_not_return_deleted_topic(db_session) -> None:
    created_topic = await repository.create_topic(
        db=db_session,
        title="Deleted Topic"
    )

    await repository.delete_topic(
        db=db_session,
        topic=created_topic
    )

    with pytest.raises(Exception):  # NoResultFound
        await repository.get_topic_by_id(
            db=db_session,
            topic_id=created_topic.id
        )


@pytest.mark.asyncio
async def test_get_all_topics_returns_all_non_deleted_topics(db_session) -> None:
    topic1 = await repository.create_topic(db=db_session, title="Topic 1")
    topic2 = await repository.create_topic(db=db_session, title="Topic 2")
    topic3 = await repository.create_topic(db=db_session, title="Topic 3")

    topics = await repository.get_all_topics(db=db_session)

    assert len(topics) == 3
    titles = [t.title for t in topics]
    assert "Topic 1" in titles
    assert "Topic 2" in titles
    assert "Topic 3" in titles


@pytest.mark.asyncio
async def test_get_all_topics_excludes_deleted_topics(db_session) -> None:
    topic1 = await repository.create_topic(db=db_session, title="Active Topic")
    topic2 = await repository.create_topic(db=db_session, title="Deleted Topic")

    await repository.delete_topic(db=db_session, topic=topic2)

    topics = await repository.get_all_topics(db=db_session)

    assert len(topics) == 1
    assert topics[0].title == "Active Topic"


@pytest.mark.asyncio
async def test_get_all_topics_returns_sorted_by_title(db_session) -> None:
    await repository.create_topic(db=db_session, title="Zebra")
    await repository.create_topic(db=db_session, title="Apple")
    await repository.create_topic(db=db_session, title="Mango")

    topics = await repository.get_all_topics(db=db_session)

    titles = [t.title for t in topics]
    assert titles == ["Apple", "Mango", "Zebra"]


@pytest.mark.asyncio
async def test_update_topic_modifies_title(db_session) -> None:
    topic = await repository.create_topic(
        db=db_session,
        title="Old Title"
    )

    updated_topic = await repository.update_topic(
        db=db_session,
        topic=topic,
        title="New Title"
    )

    assert updated_topic.title == "New Title"
    assert updated_topic.id == topic.id


@pytest.mark.asyncio
async def test_update_topic_persists_changes(db_session) -> None:
    topic = await repository.create_topic(
        db=db_session,
        title="Original"
    )

    await repository.update_topic(
        db=db_session,
        topic=topic,
        title="Modified"
    )

    updated = await repository.get_topic_by_id(
        db=db_session,
        topic_id=topic.id
    )

    assert updated.title == "Modified"


@pytest.mark.asyncio
async def test_delete_topic_soft_deletes(db_session) -> None:
    topic = await repository.create_topic(
        db=db_session,
        title="To Delete"
    )

    await repository.delete_topic(db=db_session, topic=topic)

    assert topic.deleted_at is not None
    assert isinstance(topic.deleted_at, datetime)


@pytest.mark.asyncio
async def test_delete_topic_makes_topic_unavailable(db_session) -> None:
    topic = await repository.create_topic(
        db=db_session,
        title="Topic to Delete"
    )

    await repository.delete_topic(db=db_session, topic=topic)

    topics = await repository.get_all_topics(db=db_session)
    assert len(topics) == 0
