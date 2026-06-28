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


@pytest.mark.asyncio
async def test_google_auth_creates_user_without_password(db_session, monkeypatch) -> None:
    async def fake_verify_google_id_token(id_token: str) -> dict[str, str | bool]:
        return {
            "sub": "google-sub-1",
            "email": "google@example.com",
            "name": "Google User",
            "email_verified": True,
        }

    monkeypatch.setattr(service, "verify_google_id_token", fake_verify_google_id_token)

    tokens = await service.google_auth(db=db_session, id_token="google-token")
    user = await service.repository.get_user_by_email(db=db_session, email="google@example.com")

    assert set(tokens) == {"access_token", "refresh_token"}
    assert user.google_sub == "google-sub-1"
    assert user.password is None


@pytest.mark.asyncio
async def test_google_auth_links_existing_email_user(db_session, monkeypatch) -> None:
    await service.register_user(
        db=db_session,
        username="admin",
        email="admin@example.com",
        display_name="Admin User",
        password="secret",
    )

    async def fake_verify_google_id_token(id_token: str) -> dict[str, str | bool]:
        return {
            "sub": "google-sub-2",
            "email": "admin@example.com",
            "name": "Admin User",
            "email_verified": True,
        }

    monkeypatch.setattr(service, "verify_google_id_token", fake_verify_google_id_token)
    await service.google_auth(db=db_session, id_token="google-token")

    user = await service.repository.get_user_by_email(db=db_session, email="admin@example.com")
    assert user.google_sub == "google-sub-2"


@pytest.mark.asyncio
async def test_google_auth_rejects_unverified_email(db_session, monkeypatch) -> None:
    async def fake_verify_google_id_token(id_token: str) -> dict[str, str | bool]:
        return {
            "sub": "google-sub-3",
            "email": "google@example.com",
            "name": "Google User",
            "email_verified": False,
        }

    monkeypatch.setattr(service, "verify_google_id_token", fake_verify_google_id_token)

    with pytest.raises(UnauthorizedException):
        await service.google_auth(db=db_session, id_token="google-token")
