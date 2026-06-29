import pytest
from datetime import datetime, timezone, timedelta

from sessions import repository
from models.session import Session


@pytest.mark.asyncio
async def test_create_session_returns_session(db_session) -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)
    session = Session(
        title="Design Patterns",
        description="A session on design patterns.",
        start_datetime=start,
        end_datetime=end,
        program_id=1,
    )

    created = await repository.create_session(db=db_session, session=session)

    assert created.id is not None
    assert created.title == "Design Patterns"
    assert created.description == "A session on design patterns."
    assert created.program_id == 1


@pytest.mark.asyncio
async def test_get_session_by_id_returns_session(db_session) -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)
    session = Session(
        title="Async Python",
        description="Async programming deep dive.",
        start_datetime=start,
        end_datetime=end,
        program_id=2,
    )

    created = await repository.create_session(db=db_session, session=session)
    result = await repository.get_session_by_id(db=db_session, session_id=created.id)

    assert result.id == created.id
    assert result.title == "Async Python"
    assert result.program_id == 2


@pytest.mark.asyncio
async def test_get_session_by_id_raises_for_nonexistent(db_session) -> None:
    with pytest.raises(Exception):
        await repository.get_session_by_id(db=db_session, session_id=999)


@pytest.mark.asyncio
async def test_get_sessions_returns_all_non_deleted(db_session) -> None:
    now = datetime.now(timezone.utc)
    await repository.create_session(
        db=db_session,
        session=Session(
            title="Session One",
            description="One.",
            start_datetime=now,
            end_datetime=now + timedelta(hours=1),
            program_id=1,
        ),
    )
    await repository.create_session(
        db=db_session,
        session=Session(
            title="Session Two",
            description="Two.",
            start_datetime=now + timedelta(days=1),
            end_datetime=now + timedelta(days=1, hours=1),
            program_id=1,
        ),
    )

    sessions = await repository.get_sessions(db=db_session)

    assert len(sessions) == 2
    assert {s.title for s in sessions} == {"Session One", "Session Two"}


@pytest.mark.asyncio
async def test_get_sessions_by_program_id_filters(db_session) -> None:
    now = datetime.now(timezone.utc)
    await repository.create_session(
        db=db_session,
        session=Session(
            title="Program 1 Session",
            description="Program 1.",
            start_datetime=now,
            end_datetime=now + timedelta(hours=1),
            program_id=1,
        ),
    )
    await repository.create_session(
        db=db_session,
        session=Session(
            title="Program 2 Session",
            description="Program 2.",
            start_datetime=now,
            end_datetime=now + timedelta(hours=1),
            program_id=2,
        ),
    )

    sessions = await repository.get_sessions_by_program_id(db=db_session, program_id=1)

    assert len(sessions) == 1
    assert sessions[0].program_id == 1
    assert sessions[0].title == "Program 1 Session"


@pytest.mark.asyncio
async def test_update_session_persists_changes(db_session) -> None:
    now = datetime.now(timezone.utc)
    session = Session(
        title="Initial Title",
        description="Initial.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=3,
    )

    created = await repository.create_session(db=db_session, session=session)
    created.title = "Updated Title"
    created.description = "Updated description."
    created.start_datetime = now + timedelta(days=1)
    created.end_datetime = now + timedelta(days=1, hours=2)

    updated = await repository.update_session(db=db_session, session=created)

    assert updated.title == "Updated Title"
    assert updated.description == "Updated description."
    assert updated.start_datetime == created.start_datetime


@pytest.mark.asyncio
async def test_delete_session_soft_deletes(db_session) -> None:
    now = datetime.now(timezone.utc)
    session = await repository.create_session(
        db=db_session,
        session=Session(
            title="Delete Me",
            description="Delete test.",
            start_datetime=now,
            end_datetime=now + timedelta(hours=1),
            program_id=4,
        ),
    )

    await repository.delete_session(db=db_session, session=session)

    assert session.deleted_at is not None

    with pytest.raises(Exception):
        await repository.get_session_by_id(db=db_session, session_id=session.id)
