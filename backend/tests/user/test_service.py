import pytest

from user import service as user_service
from user.schema import UserCreate, UserUpdate
from exceptions import ConflictException, NotFoundException


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
async def test_get_user_by_id_not_found_raises_not_found(db_session) -> None:
    with pytest.raises(NotFoundException):
        await user_service.get_user_by_id(9999, db_session)
