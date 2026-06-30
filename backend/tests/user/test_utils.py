import pytest

from auth.utils import hash_password
from user import repository as user_repo
from user.schema import UserCreate, UserUpdate


@pytest.mark.asyncio
async def test_create_user_hashes_password(db_session) -> None:
    body = UserCreate(
        username="admin",
        display_name="Admin User",
        email="admin@example.com",
        password="secret",
        is_admin=False,
    )

    user = await user_repo.create_user(
        db=db_session,
        body=body,
    )

    assert user.password is not None
    assert user.password != "secret"
    assert user.password == hash_password("secret")


@pytest.mark.asyncio
async def test_patch_user_hashes_new_password(db_session) -> None:
    body = UserCreate(
        username="admin",
        display_name="Admin User",
        email="admin@example.com",
        password="secret",
        is_admin=False,
    )

    user = await user_repo.create_user(
        db=db_session,
        body=body,
    )

    updated = await user_repo.patch_user(
        id=user.id,
        body=UserUpdate(
            password="new-secret",
        ),
        db=db_session,
    )

    assert updated.password is not None
    assert updated.password != "new-secret"
    assert updated.password == hash_password("new-secret")