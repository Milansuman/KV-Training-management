import pytest
from datetime import datetime, timezone, timedelta

from sessions import service
from exceptions import NotFoundException


@pytest.mark.asyncio
async def test_create_session_returns_session(db_session) -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=1)

    created = await service.create_session(
        db=db_session,
        title="Kubernetes Basics",
        description="Introduction to Kubernetes.",
        start_datetime=start,
        end_datetime=end,
        program_id=5,
    )

    assert created.id is not None
    assert created.title == "Kubernetes Basics"
    assert created.program_id == 5


@pytest.mark.asyncio
async def test_get_session_returns_existing_session(db_session) -> None:
    start = datetime.now(timezone.utc)
    end = start + timedelta(hours=2)

    created = await service.create_session(
        db=db_session,
        title="Deployment",
        description="Deployment methods.",
        start_datetime=start,
        end_datetime=end,
        program_id=6,
    )

    result = await service.get_session(db=db_session, session_id=created.id)

    assert result.id == created.id
    assert result.title == "Deployment"


@pytest.mark.asyncio
async def test_get_session_raises_not_found_for_missing(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.get_session(db=db_session, session_id=999)


@pytest.mark.asyncio
async def test_get_sessions_returns_all(db_session) -> None:
    now = datetime.now(timezone.utc)
    await service.create_session(
        db=db_session,
        title="Session A",
        description="A.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=1,
    )
    await service.create_session(
        db=db_session,
        title="Session B",
        description="B.",
        start_datetime=now + timedelta(days=1),
        end_datetime=now + timedelta(days=1, hours=1),
        program_id=1,
    )

    sessions = await service.get_sessions(db=db_session)

    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_get_sessions_by_program_id_returns_only_matching_program(db_session) -> None:
    now = datetime.now(timezone.utc)
    await service.create_session(
        db=db_session,
        title="Program 10 A",
        description="A.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=10,
    )
    await service.create_session(
        db=db_session,
        title="Program 20 A",
        description="B.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=20,
    )

    sessions = await service.get_sessions_by_program_id(db=db_session, program_id=10)

    assert len(sessions) == 1
    assert sessions[0].program_id == 10


@pytest.mark.asyncio
async def test_update_session_persists_changes(db_session) -> None:
    now = datetime.now(timezone.utc)
    created = await service.create_session(
        db=db_session,
        title="Initial",
        description="Initial desc.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=7,
    )

    new_start = now + timedelta(days=1)
    updated = await service.update_session(
        db=db_session,
        session_id=created.id,
        title="Updated",
        description="Updated desc.",
        start_datetime=new_start,
        end_datetime=new_start + timedelta(hours=2),
    )

    assert updated.title == "Updated"
    assert updated.description == "Updated desc."
    assert updated.id == created.id


@pytest.mark.asyncio
async def test_update_session_raises_not_found_for_missing(db_session) -> None:
    now = datetime.now(timezone.utc)
    with pytest.raises(NotFoundException):
        await service.update_session(
            db=db_session,
            session_id=999,
            title="X",
            description="X.",
            start_datetime=now,
            end_datetime=now + timedelta(hours=1),
        )


@pytest.mark.asyncio
async def test_delete_session_removes_session(db_session) -> None:
    now = datetime.now(timezone.utc)
    created = await service.create_session(
        db=db_session,
        title="Delete Me",
        description="Delete test.",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=8,
    )

    await service.delete_session(db=db_session, session_id=created.id)

    with pytest.raises(NotFoundException):
        await service.get_session(db=db_session, session_id=created.id)


@pytest.mark.asyncio
async def test_delete_session_raises_not_found_for_missing(db_session) -> None:
    with pytest.raises(NotFoundException):
        await service.delete_session(db=db_session, session_id=999)
