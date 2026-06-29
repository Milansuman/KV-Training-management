"""Service-layer tests for the programs module."""

import pytest
from datetime import UTC, datetime, timedelta

from models.session import Session
from programs import repository
from programs.service import (
    create_program,
    delete_program,
    get_program_progress,
    update_program,
)
from auth.service import register_user
from exceptions import BadRequestException, ForbiddenException, NotFoundException


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_admin(db):
    return await register_user(
        db=db,
        username="admin",
        email="admin@example.com",
        display_name="Admin",
        password="secret",
    )


async def _make_user(db, username="member", email="member@example.com"):
    return await register_user(
        db=db,
        username=username,
        email=email,
        display_name="Member",
        password="secret",
    )


async def _make_program(db, user_id):
    return await create_program(
        db=db,
        user_id=user_id,
        title="Freshers Training",
        description="Training for new joiners",
        start_date=datetime(2025, 1, 1).date(),
        end_date=datetime(2025, 6, 30).date(),
    )


async def _add_session(db, program_id, *, hours_until_end=1):
    """Create a session whose end_datetime is `hours_until_end` hours from now.
    Negative values produce an already-completed session."""
    now = datetime.now(UTC)
    session = Session(
        title="Session",
        description="desc",
        start_datetime=now - timedelta(hours=2),
        end_datetime=now + timedelta(hours=hours_until_end),
        program_id=program_id,
    )
    db.add(session)
    await db.commit()
    return session


# ---------------------------------------------------------------------------
# create_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_program_admin_succeeds(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    assert program.id is not None
    assert program.title == "Freshers Training"


@pytest.mark.asyncio
async def test_create_program_non_admin_raises_forbidden(db_session) -> None:
    await _make_admin(db_session)
    member = await _make_user(db_session)

    with pytest.raises(ForbiddenException):
        await _make_program(db_session, member.id)


@pytest.mark.asyncio
async def test_create_program_unknown_user_raises_not_found(db_session) -> None:
    with pytest.raises(NotFoundException):
        await _make_program(db_session, user_id=99999)


@pytest.mark.asyncio
async def test_create_program_creates_staff_permission(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    from sqlalchemy import select
    from models.program_permission import ProgramPermission, ProgramRoles

    permission = (await db_session.scalars(
        select(ProgramPermission)
        .where(ProgramPermission.user_id == admin.id)
        .where(ProgramPermission.program_id == program.id)
    )).one()

    assert permission.role == ProgramRoles.STAFF


# ---------------------------------------------------------------------------
# get_program_progress
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_program_progress_empty_for_new_user(db_session) -> None:
    admin = await _make_admin(db_session)
    result = await get_program_progress(db=db_session, user_id=admin.id)

    assert result == []


@pytest.mark.asyncio
async def test_get_program_progress_returns_program(db_session) -> None:
    admin = await _make_admin(db_session)
    await _make_program(db_session, admin.id)

    result = await get_program_progress(db=db_session, user_id=admin.id)

    assert len(result) == 1
    assert result[0].title == "Freshers Training"


@pytest.mark.asyncio
async def test_get_program_progress_counts_total_sessions(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    await _add_session(db_session, program.id, hours_until_end=2)
    await _add_session(db_session, program.id, hours_until_end=4)

    result = await get_program_progress(db=db_session, user_id=admin.id)

    assert result[0].total_sessions == 2


@pytest.mark.asyncio
async def test_get_program_progress_counts_completed_sessions(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    await _add_session(db_session, program.id, hours_until_end=-1)  # past → completed
    await _add_session(db_session, program.id, hours_until_end=-2)  # past → completed
    await _add_session(db_session, program.id, hours_until_end=5)   # future → not completed

    result = await get_program_progress(db=db_session, user_id=admin.id)

    assert result[0].total_sessions == 3
    assert result[0].completed_sessions == 2


@pytest.mark.asyncio
async def test_get_program_progress_excludes_deleted_programs(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    await delete_program(db=db_session, program_id=program.id)

    result = await get_program_progress(db=db_session, user_id=admin.id)
    assert result == []


@pytest.mark.asyncio
async def test_get_program_progress_does_not_include_other_users_programs(db_session) -> None:
    admin = await _make_admin(db_session)
    await _make_program(db_session, admin.id)

    member = await _make_user(db_session)
    result = await get_program_progress(db=db_session, user_id=member.id)

    assert result == []


@pytest.mark.asyncio
async def test_get_program_progress_carries_program_timestamps(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    result = await get_program_progress(db=db_session, user_id=admin.id)

    assert result[0].created_at == program.created_at
    assert result[0].updated_at == program.updated_at


# ---------------------------------------------------------------------------
# update_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_program_changes_title(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    updated = await update_program(
        db=db_session,
        program_id=program.id,
        title="New Title",
        description=None,
        start_date=None,
        end_date=None,
    )

    assert updated.title == "New Title"
    assert updated.description == program.description


@pytest.mark.asyncio
async def test_update_program_ignores_none_fields(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    original_description = program.description

    await update_program(
        db=db_session,
        program_id=program.id,
        title="Changed",
        description=None,
        start_date=None,
        end_date=None,
    )

    fresh = await repository.get_program_by_id(db=db_session, program_id=program.id)
    assert fresh.description == original_description


@pytest.mark.asyncio
async def test_update_program_all_fields(db_session) -> None:
    from datetime import date

    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    updated = await update_program(
        db=db_session,
        program_id=program.id,
        title="New Title",
        description="New desc",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 12, 31),
    )

    assert updated.title == "New Title"
    assert updated.description == "New desc"
    assert updated.start_date == date(2026, 1, 1)
    assert updated.end_date == date(2026, 12, 31)


@pytest.mark.asyncio
async def test_update_program_raises_not_found_for_missing(db_session) -> None:
    with pytest.raises(NotFoundException):
        await update_program(
            db=db_session,
            program_id=99999,
            title="x",
            description=None,
            start_date=None,
            end_date=None,
        )


@pytest.mark.asyncio
async def test_update_deleted_program_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    await delete_program(db=db_session, program_id=program.id)

    with pytest.raises(NotFoundException):
        await update_program(
            db=db_session,
            program_id=program.id,
            title="x",
            description=None,
            start_date=None,
            end_date=None,
        )


# ---------------------------------------------------------------------------
# delete_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_program_sets_deleted_at(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    await delete_program(db=db_session, program_id=program.id)

    assert program.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_program_raises_not_found_for_missing(db_session) -> None:
    with pytest.raises(NotFoundException):
        await delete_program(db=db_session, program_id=99999)


@pytest.mark.asyncio
async def test_delete_program_raises_not_found_if_already_deleted(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    await delete_program(db=db_session, program_id=program.id)

    with pytest.raises(NotFoundException):
        await delete_program(db=db_session, program_id=program.id)
