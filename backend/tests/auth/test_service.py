import pytest

from auth import service
from exceptions import ConflictException, NotFoundException, UnauthorizedException


@pytest.mark.asyncio
async def test_register_user_creates_admin_for_first_user(db_session) -> None:
    user = await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    assert user.id is not None
    assert user.is_admin is True


@pytest.mark.asyncio
async def test_register_user_marks_second_user_non_admin(db_session) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    user = await service.register_user(
        db=db_session,
        username="member",
        email="member@example.com",
        display_name="Member User",
        password="secret",
    )

    assert user.is_admin is False


@pytest.mark.asyncio
async def test_register_user_raises_conflict_for_duplicate_email(db_session) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    with pytest.raises(ConflictException):
        await service.register_user(
            db=db_session,
            username="another",
            email="admin@example.com",
            display_name="Another User",
            password="secret",
        )


@pytest.mark.asyncio
async def test_login_returns_access_and_refresh_tokens(db_session) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    tokens = await service.login(
        db=db_session,
        username_or_email="admin",
        password="secret",
    )

    assert set(tokens) == {"access_token", "refresh_token"}


@pytest.mark.asyncio
async def test_login_rejects_invalid_password(db_session) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    with pytest.raises(UnauthorizedException):
        await service.login(
            db=db_session,
            username_or_email="admin",
            password="wrong",
        )


@pytest.mark.asyncio
async def test_refresh_returns_new_token_pair(db_session) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    tokens = await service.login(
        db=db_session,
        username_or_email="admin",
        password="secret",
    )

    refreshed = await service.refresh(db=db_session, refresh_token=tokens["refresh_token"])

    assert set(refreshed) == {"access_token", "refresh_token"}
    assert refreshed["refresh_token"] != tokens["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_rejects_token_for_missing_user(db_session) -> None:
    token_pair = service.utils.create_token_pair(subject="999")

    with pytest.raises(NotFoundException):
        await service.refresh(db=db_session, refresh_token=token_pair["refresh_token"])
