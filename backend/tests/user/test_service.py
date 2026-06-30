import pytest

from user import service as user_service
from user.schema import UserCreate, UserUpdate
from exceptions import ConflictException, NotFoundException
from models.program import Program
from models.program_permission import ProgramPermission, ProgramRoles
from models.session import Session
from models.session_permission import SessionPermission, SessionRoles


@pytest.mark.asyncio
async def test_create_and_get_user(db_session) -> None:
    payload = UserCreate(
        username="admin",
        display_name="Admin User",
        email="admin@example.com",
        password="secret",
        is_admin=False,
    )

    user = await user_service.create_user(db_session, payload)

    assert user.id is not None
    assert user.username == "admin"

    fetched = await user_service.get_user_by_id(user.id, db_session)
    assert fetched.id == user.id
    assert fetched.email == "admin@example.com"


@pytest.mark.asyncio
async def test_get_all_users_returns_users(db_session) -> None:
    await user_service.create_user(
        db_session,
        UserCreate(
            username="admin",
            display_name="Admin User",
            email="admin@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    users = await user_service.get_all_users(db_session)

    assert len(users) == 1
    assert users[0].username == "admin"


@pytest.mark.asyncio
async def test_patch_user_updates_password_and_fields(db_session) -> None:
    user = await user_service.create_user(
        db_session,
        UserCreate(
            username="admin",
            display_name="Admin User",
            email="admin@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    updated = await user_service.patch_user(
        user.id,
        UserUpdate(display_name="Updated Admin", password="new-secret"),
        db_session,
    )

    assert updated.display_name == "Updated Admin"
    assert updated.password != "new-secret"


@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises_conflict(db_session) -> None:
    await user_service.create_user(
        db_session,
        UserCreate(
            username="admin",
            display_name="Admin User",
            email="admin@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    with pytest.raises(ConflictException):
        await user_service.create_user(
            db_session,
            UserCreate(
                username="another",
                display_name="Another User",
                email="admin@example.com",
                password="secret",
                is_admin=False,
            ),
        )


@pytest.mark.asyncio
async def test_delete_user_soft_deletes_user(db_session) -> None:
    user = await user_service.create_user(
        db_session,
        UserCreate(
            username="admin",
            display_name="Admin User",
            email="admin@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    deleted = await user_service.delete_user(user.id, db_session)

    assert deleted.deleted_at is not None

    with pytest.raises(NotFoundException):
        await user_service.get_user_by_id(user.id, db_session)


@pytest.mark.asyncio
async def test_get_user_program_status_with_no_permissions(db_session) -> None:
    """Returns is_admin, None program_role, and empty session_roles when user has no permissions."""
    user = await user_service.create_user(
        db_session,
        UserCreate(
            username="member",
            display_name="Member",
            email="member@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    result = await user_service.get_user_program_status(
        db=db_session,
        user_id=user.id,
        program_id=999,
    )

    assert result.is_admin is False
    assert result.program_role is None
    assert result.session_roles == []


@pytest.mark.asyncio
async def test_get_user_program_status_with_full_data(db_session) -> None:
    """Returns admin status, program role, and session roles when all data is present."""
    from datetime import UTC, datetime, timedelta

    # Create a user
    user = await user_service.create_user(
        db_session,
        UserCreate(
            username="member",
            display_name="Member",
            email="member@example.com",
            password="secret",
            is_admin=False,
        ),
    )

    # Create a program
    program = Program(
        title="Test Program",
        description="A test program",
        start_date=datetime.now(UTC).date(),
        end_date=datetime.now(UTC).date() + timedelta(days=30),
    )
    db_session.add(program)
    await db_session.commit()
    await db_session.refresh(program)

    # Create a program permission (role = STAFF)
    pp = ProgramPermission(
        user_id=user.id,
        program_id=program.id,
        role=ProgramRoles.STAFF,
    )
    db_session.add(pp)
    await db_session.commit()

    # Create two sessions in the program
    session1 = Session(
        title="Session One",
        description="First session",
        start_datetime=datetime.now(UTC),
        end_datetime=datetime.now(UTC) + timedelta(hours=1),
        program_id=program.id,
    )
    db_session.add(session1)
    await db_session.commit()
    await db_session.refresh(session1)

    session2 = Session(
        title="Session Two",
        description="Second session",
        start_datetime=datetime.now(UTC) + timedelta(days=1),
        end_datetime=datetime.now(UTC) + timedelta(days=1, hours=1),
        program_id=program.id,
    )
    db_session.add(session2)
    await db_session.commit()
    await db_session.refresh(session2)

    # Add session permission for session1 only (role = TRAINER)
    sp = SessionPermission(
        user_id=user.id,
        session_id=session1.id,
        role=SessionRoles.TRAINER,
    )
    db_session.add(sp)
    await db_session.commit()

    # Call the service
    result = await user_service.get_user_program_status(
        db=db_session,
        user_id=user.id,
        program_id=program.id,
    )

    assert result.is_admin is False
    assert result.program_role == ProgramRoles.STAFF
    assert len(result.session_roles) == 2

    # session1 should have role = TRAINER
    sr1 = next(r for r in result.session_roles if r.session_id == session1.id)
    assert sr1.session_title == "Session One"
    assert sr1.role == SessionRoles.TRAINER

    # session2 should have role = None (no permission)
    sr2 = next(r for r in result.session_roles if r.session_id == session2.id)
    assert sr2.session_title == "Session Two"
    assert sr2.role is None
