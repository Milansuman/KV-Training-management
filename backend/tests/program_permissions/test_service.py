"""Service-level tests for the program_permissions module."""

import pytest
from datetime import date

from auth.service import register_user
from exceptions import ConflictException, NotFoundException
from models.program_permission import ProgramRoles
from program_permissions.service import (
    add_person_to_program,
    delete_permission,
    get_program_permissions,
    is_user_in_program,
)
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
# get_program_permissions
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_program_permissions_returns_members(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session, "member1", "m1@example.com")
    member2 = await _make_user(db_session, "member2", "m2@example.com")

    await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )
    await add_person_to_program(
        db=db_session, user_id=member2.id, program_id=program.id, role=ProgramRoles.STAFF
    )

    permissions = await get_program_permissions(db=db_session, program_id=program.id)

    # admin is auto-added by create_program, plus member + member2
    assert len(permissions) == 3

    permission_map = {p["user_id"]: p for p in permissions}
    assert permission_map[member.id]["username"] == "member1"
    assert permission_map[member.id]["role"] == ProgramRoles.CANDIDATE
    assert permission_map[member2.id]["role"] == ProgramRoles.STAFF
    assert permission_map[admin.id]["role"] == ProgramRoles.STAFF


@pytest.mark.asyncio
async def test_get_program_permissions_empty_program(db_session) -> None:
    """A program with no explicit permissions (other than the creator's) should
    still return at least the creator's permission."""
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    permissions = await get_program_permissions(db=db_session, program_id=program.id)

    assert len(permissions) == 1
    assert permissions[0]["user_id"] == admin.id


@pytest.mark.asyncio
async def test_get_program_permissions_excludes_deleted(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)
    member = await _make_user(db_session)

    perm = await add_person_to_program(
        db=db_session, user_id=member.id, program_id=program.id, role=ProgramRoles.CANDIDATE
    )
    await delete_permission(db=db_session, permission_id=perm.id)

    permissions = await get_program_permissions(db=db_session, program_id=program.id)

    assert len(permissions) == 1  # only the creator remains
    assert permissions[0]["user_id"] == admin.id


@pytest.mark.asyncio
async def test_get_program_permissions_returns_user_info(db_session) -> None:
    admin = await _make_admin(db_session)
    program = await _make_program(db_session, admin.id)

    permissions = await get_program_permissions(db=db_session, program_id=program.id)

    perm = permissions[0]
    assert "permission_id" in perm
    assert "user_id" in perm
    assert "username" in perm
    assert "display_name" in perm
    assert "role" in perm


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
