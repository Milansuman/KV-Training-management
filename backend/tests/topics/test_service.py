import pytest

from topics import service
from exceptions import NotFoundException


@pytest.mark.asyncio
async def test_create_topic_returns_topic(db_session) -> None:
    topic = await service.create_topic(
        db=db_session,
        title="Python Fundamentals"
    )

    assert topic.id is not None
    assert topic.title == "Python Fundamentals"


@pytest.mark.asyncio
async def test_create_topic_persists_to_database(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="Database Design"
    )

    retrieved_topic = await service.get_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    assert retrieved_topic.id == created_topic.id
    assert retrieved_topic.title == "Database Design"


@pytest.mark.asyncio
async def test_get_topic_returns_existing_topic(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="API Design"
    )

    topic = await service.get_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    assert topic.id == created_topic.id
    assert topic.title == "API Design"


@pytest.mark.asyncio
async def test_get_topic_raises_not_found_for_nonexistent_topic(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.get_topic(
            db=db_session,
            topic_id=999
        )


@pytest.mark.asyncio
async def test_get_topic_raises_not_found_for_deleted_topic(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="Deleted Topic"
    )

    await service.delete_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    with pytest.raises(NotFoundException):
        await service.get_topic(
            db=db_session,
            topic_id=created_topic.id
        )


@pytest.mark.asyncio
async def test_get_topics_returns_all_topics(db_session) -> None:
    await service.create_topic(db=db_session, title="Topic A")
    await service.create_topic(db=db_session, title="Topic B")
    await service.create_topic(db=db_session, title="Topic C")

    topics = await service.get_topics(db=db_session)

    assert len(topics) == 3


@pytest.mark.asyncio
async def test_get_topics_returns_empty_list_when_no_topics(db_session) -> None:
    topics = await service.get_topics(db=db_session)

    assert topics == []


@pytest.mark.asyncio
async def test_get_topics_excludes_deleted_topics(db_session) -> None:
    topic1 = await service.create_topic(db=db_session, title="Active")
    topic2 = await service.create_topic(db=db_session, title="To Delete")

    await service.delete_topic(db=db_session, topic_id=topic2.id)

    topics = await service.get_topics(db=db_session)

    assert len(topics) == 1
    assert topics[0].title == "Active"


@pytest.mark.asyncio
async def test_update_topic_changes_title(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="Old Title"
    )

    updated_topic = await service.update_topic(
        db=db_session,
        topic_id=created_topic.id,
        title="Updated Title"
    )

    assert updated_topic.title == "Updated Title"
    assert updated_topic.id == created_topic.id


@pytest.mark.asyncio
async def test_update_topic_persists_changes(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="Original"
    )

    await service.update_topic(
        db=db_session,
        topic_id=created_topic.id,
        title="Changed"
    )

    updated_topic = await service.get_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    assert updated_topic.title == "Changed"


@pytest.mark.asyncio
async def test_update_topic_raises_not_found_for_nonexistent_topic(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.update_topic(
            db=db_session,
            topic_id=999,
            title="New Title"
        )


@pytest.mark.asyncio
async def test_update_topic_raises_not_found_for_deleted_topic(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="To Delete"
    )

    await service.delete_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    with pytest.raises(NotFoundException):
        await service.update_topic(
            db=db_session,
            topic_id=created_topic.id,
            title="Updated"
        )


@pytest.mark.asyncio
async def test_delete_topic_removes_topic(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="To Delete"
    )

    await service.delete_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    with pytest.raises(NotFoundException):
        await service.get_topic(
            db=db_session,
            topic_id=created_topic.id
        )


@pytest.mark.asyncio
async def test_delete_topic_raises_not_found_for_nonexistent_topic(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.delete_topic(
            db=db_session,
            topic_id=999
        )


@pytest.mark.asyncio
async def test_delete_topic_raises_not_found_for_already_deleted_topic(db_session) -> None:
    created_topic = await service.create_topic(
        db=db_session,
        title="Topic"
    )

    await service.delete_topic(
        db=db_session,
        topic_id=created_topic.id
    )

    with pytest.raises(NotFoundException):
        await service.delete_topic(
            db=db_session,
            topic_id=created_topic.id
        )
