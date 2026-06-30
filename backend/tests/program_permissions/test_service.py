"""Service-level tests for the program_permissions module."""

import pytest
from datetime import date

from auth.service import register_user
from exceptions import ConflictException, NotFoundException
from models.program_permission import ProgramRoles
from program_permissions.service import add_person_to_program, delete_permission, is_user_in_program
from programs.service import create_program


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
        display_name="Member", password="secret",
    )


async def _make_program(db, user_id):
    return await create_program(
        db=db, user_id=user_id, title="Test Program", description="desc",
        start_date=date(2025, 1, 1), end_date=date(2025, 12, 31),
    )


# ---------------------------------------------------------------------------
# add_person_to_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_add_staff_role_succeeds(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    permission = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.STAFF
    )

    assert permission.id is not None
    assert permission.role == ProgramRoles.STAFF
    assert permission.user_id == member.id
    assert permission.program_id == program.id


@pytest.mark.asyncio
async def test_add_candidate_role_succeeds(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    permission = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )

    assert permission.role == ProgramRoles.CANDIDATE


@pytest.mark.asyncio
async def test_add_unknown_user_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    with pytest.raises(NotFoundException):
        await add_person_to_program(
            db=db_session, user_id=99999, program_id=program.id, role=ProgramRoles.CANDIDATE
        )


@pytest.mark.asyncio
async def test_add_unknown_program_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)

    with pytest.raises(NotFoundException):
        await add_person_to_program(
            db=db_session, user_id=admin.id, program_id=99999, role=ProgramRoles.STAFF
        )


@pytest.mark.asyncio
async def test_add_duplicate_raises_conflict(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )

    with pytest.raises(ConflictException):
        await add_person_to_program(
            db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
        )


# ---------------------------------------------------------------------------
# is_user_in_program
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_is_user_in_program_returns_true_for_member(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    result = await is_user_in_program(db=db_session, user_id=admin.id, program_id=program.id)

    assert result is True


@pytest.mark.asyncio
async def test_is_user_in_program_returns_false_for_non_member(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    other = await _make_user(db_session)

    result = await is_user_in_program(db=db_session, user_id=other.id, program_id=program.id)

    assert result is False


@pytest.mark.asyncio
async def test_is_user_in_program_returns_false_after_deletion(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    permission = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )
    await delete_permission(db=db_session, permission_id=permission.id)

    result = await is_user_in_program(db=db_session, user_id=member.id, program_id=program.id)
    assert result is False


@pytest.mark.asyncio
async def test_is_user_in_program_returns_false_for_unknown_user(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    result = await is_user_in_program(db=db_session, user_id=99999, program_id=program.id)

    assert result is False


# ---------------------------------------------------------------------------
# delete_permission
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_permission_sets_deleted_at(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    permission = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )
    await delete_permission(db=db_session, permission_id=permission.id)

    assert permission.deleted_at is not None


@pytest.mark.asyncio
async def test_delete_permission_unknown_id_raises_not_found(db_session) -> None:
    with pytest.raises(NotFoundException):
        await delete_permission(db=db_session, permission_id=99999)


@pytest.mark.asyncio
async def test_delete_permission_twice_raises_not_found(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    permission = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )
    await delete_permission(db=db_session, permission_id=permission.id)

    with pytest.raises(NotFoundException):
        await delete_permission(db=db_session, permission_id=permission.id)
