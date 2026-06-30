"""Service-level tests for the session_permissions module."""

import pytest
from datetime import UTC, date, datetime, timedelta

from auth.service import register_user
from exceptions import ConflictException, ForbiddenException, NotFoundException
from models.program_permission import ProgramRoles
from models.session import Session
from models.session_permission import SessionRoles
from program_permissions.service import add_person_to_program
from programs.service import create_program
from session_permissions.service import (
    add_session_permission,
    delete_session_permission,
    get_session_permissions_by_program,
    get_sessions_by_program,
    update_session_permission,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _make_admin(db):
    return await register_user(
        db=db, username="admin", email="admin@example.com",
        display_name="Admin", password="secret",
    )


async def _make_user(db, username="member", email="member@example.com"):
    return await register_user(
        db=db, username=username, email=email,
        display_name=username, password="secret",
    )


async def _make_program(db, user_id):
    return await create_program(
        db=db, user_id=user_id, title="Test Program", description="desc",
        start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
    )


async def _add_to_program(db, user_id, program_id, role=ProgramRoles.STAFF):
    return await add_person_to_program(
        db=db, user_id=user_id, program_id=program_id, role=role
    )


async def _make_session(db, program_id, title="Session 1"):
    now = datetime.now(UTC)
    session = Session(
        title=title,
        description="desc",
        start_datetime=now,
        end_datetime=now + timedelta(hours=1),
        program_id=program_id,
    )
    db.add(session)
    await db.commit()
    return session


# ---------------------------------------------------------------------------
# add_session_permission
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_staff_can_be_added_as_trainer(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)

    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
    )

    assert permission.role == SessionRoles.TRAINER


@pytest.mark.asyncio
async def test_staff_can_be_added_as_moderator(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)

    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.MODERATOR
    )

    assert permission.role == SessionRoles.MODERATOR


@pytest.mark.asyncio
async def test_staff_can_be_added_as_candidate(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)

    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.CANDIDATE
    )

    assert permission.role == SessionRoles.CANDIDATE


@pytest.mark.asyncio
async def test_candidate_can_be_added_as_candidate(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    session = await _make_session(db_session, program.id)

    permission = await add_session_permission(
        db=db_session, user_id=member.id, session_id=session.id, role=SessionRoles.CANDIDATE
    )

    assert permission.role == SessionRoles.CANDIDATE


@pytest.mark.asyncio
async def test_candidate_cannot_be_added_as_trainer(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    session = await _make_session(db_session, program.id)

    with pytest.raises(ForbiddenException):
        await add_session_permission(
            db=db_session, user_id=member.id, session_id=session.id, role=SessionRoles.TRAINER
        )


@pytest.mark.asyncio
async def test_candidate_cannot_be_added_as_moderator(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    session = await _make_session(db_session, program.id)

    with pytest.raises(ForbiddenException):
        await add_session_permission(
            db=db_session, user_id=member.id, session_id=session.id, role=SessionRoles.MODERATOR
        )


@pytest.mark.asyncio
async def test_user_not_in_program_raises_forbidden(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    outsider = await _make_user(db_session)
    session = await _make_session(db_session, program.id)

    with pytest.raises(ForbiddenException):
        await add_session_permission(
            db=db_session, user_id=outsider.id, session_id=session.id, role=SessionRoles.CANDIDATE
        )


@pytest.mark.asyncio
async def test_add_unknown_user_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)

    with pytest.raises(NotFoundException):
        await add_session_permission(
            db=db_session, user_id=99999, session_id=session.id, role=SessionRoles.CANDIDATE
        )


@pytest.mark.asyncio
async def test_add_unknown_session_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)

    with pytest.raises(NotFoundException):
        await add_session_permission(
            db=db_session, user_id=admin.id, session_id=99999, role=SessionRoles.CANDIDATE
        )


@pytest.mark.asyncio
async def test_add_duplicate_raises_conflict(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)

    await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
    )

    with pytest.raises(ConflictException):
        await add_session_permission(
            db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
        )


# ---------------------------------------------------------------------------
# update_session_permission
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_staff_can_update_to_moderator(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)
    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
    )

    updated = await update_session_permission(
        db=db_session, permission_id=permission.id, role=SessionRoles.MODERATOR
    )

    assert updated.role == SessionRoles.MODERATOR


@pytest.mark.asyncio
async def test_staff_can_update_to_trainer(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)
    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.MODERATOR
    )

    updated = await update_session_permission(
        db=db_session, permission_id=permission.id, role=SessionRoles.TRAINER
    )

    assert updated.role == SessionRoles.TRAINER


@pytest.mark.asyncio
async def test_candidate_can_update_to_candidate(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    session = await _make_session(db_session, program.id)
    permission = await add_session_permission(
        db=db_session, user_id=member.id, session_id=session.id, role=SessionRoles.CANDIDATE
    )

    updated = await update_session_permission(
        db=db_session, permission_id=permission.id, role=SessionRoles.CANDIDATE
    )

    assert updated.role == SessionRoles.CANDIDATE


@pytest.mark.asyncio
async def test_candidate_cannot_update_to_trainer(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    session = await _make_session(db_session, program.id)
    permission = await add_session_permission(
        db=db_session, user_id=member.id, session_id=session.id, role=SessionRoles.CANDIDATE
    )

    with pytest.raises(ForbiddenException):
        await update_session_permission(
            db=db_session, permission_id=permission.id, role=SessionRoles.TRAINER
        )


@pytest.mark.asyncio
async def test_update_nonexistent_permission_raises_not_found(db_session) -> None:
    with pytest.raises(NotFoundException):
        await update_session_permission(
            db=db_session, permission_id=99999, role=SessionRoles.CANDIDATE
        )


# ---------------------------------------------------------------------------
# delete_session_permission
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_sets_deleted_at(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)
    permission = await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
    )

    await delete_session_permission(db=db_session, permission_id=permission.id)

    assert permission.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_nonexistent_raises_not_found(db_session) -> None:
    with pytest.raises(NotFoundException):
        await delete_session_permission(db=db_session, permission_id=99999)


# ---------------------------------------------------------------------------
# get_sessions_by_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_sessions_returns_all_sessions(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    await _make_session(db_session, program.id, "Session A")
    await _make_session(db_session, program.id, "Session B")

    sessions = await get_sessions_by_program(db=db_session, program_id=program.id)

    assert len(sessions) == 2
    titles = {s.title for s in sessions}
    assert titles == {"Session A", "Session B"}


@pytest.mark.asyncio
async def test_get_sessions_returns_empty_for_unknown_program(db_session) -> None:
    sessions = await get_sessions_by_program(db=db_session, program_id=99999)

    assert sessions == []


# ---------------------------------------------------------------------------
# get_session_permissions_by_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_with_role_shows_role_when_permitted(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session = await _make_session(db_session, program.id)
    await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session.id, role=SessionRoles.TRAINER
    )

    result = await get_session_permissions_by_program(
        db=db_session, user_id=admin.id, program_id=program.id
    )

    assert len(result) == 1
    assert result[0].role == SessionRoles.TRAINER


@pytest.mark.asyncio
async def test_get_with_role_shows_none_when_not_permitted(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)
    await _add_to_program(db_session, member.id, program.id, ProgramRoles.CANDIDATE)
    await _make_session(db_session, program.id)

    result = await get_session_permissions_by_program(
        db=db_session, user_id=member.id, program_id=program.id
    )

    assert len(result) == 1
    assert result[0].role is None


@pytest.mark.asyncio
async def test_get_with_role_mixed_sessions(db_session) -> None:
    """User has permission for one session but not the other."""
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    session_a = await _make_session(db_session, program.id, "Session A")
    await _make_session(db_session, program.id, "Session B")
    await add_session_permission(
        db=db_session, user_id=admin.id, session_id=session_a.id, role=SessionRoles.TRAINER
    )

    result = await get_session_permissions_by_program(
        db=db_session, user_id=admin.id, program_id=program.id
    )

    roles = {r.title: r.role for r in result}
    assert roles["Session A"] == SessionRoles.TRAINER
    assert roles["Session B"] is None
