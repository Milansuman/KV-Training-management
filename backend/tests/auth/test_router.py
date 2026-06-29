def test_register_returns_user(client) -> None:
    response = client.post(
        "/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "display_name": "Admin User",
            "password": "secret",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "admin"
    assert "access_token=" not in response.headers.get("set-cookie", "")


def test_login_sets_access_and_refresh_cookies(client) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "display_name": "Admin User",
            "password": "secret",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin",
            "password": "secret",
        },
    )

    assert response.status_code == 200
    assert "access_token=" in response.headers.get("set-cookie", "")
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert response.json()["access_token"]
    assert response.json()["refresh_token"]


def test_refresh_uses_cookie_and_sets_new_tokens(client) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "display_name": "Admin User",
            "password": "secret",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin",
            "password": "secret",
        },
    )

    refresh_cookie = login_response.cookies.get("refresh_token")
    response = client.post("/auth/refresh", cookies={"refresh_token": refresh_cookie})

    assert response.status_code == 200
    assert "access_token=" in response.headers.get("set-cookie", "")
    assert "refresh_token=" in response.headers.get("set-cookie", "")


def test_refresh_without_cookie_is_unauthorized(client) -> None:
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token cookie is required"


def test_google_callback_redirects_with_nonce(client, monkeypatch) -> None:
    """The callback should NOT set auth cookies; it should redirect to the
    frontend verify page with a ``nonce`` query parameter."""
    async def fake_authorize_access_token(*_, **__) -> dict[str, str]:
        return {"id_token": "google-id-token"}

    async def fake_google_auth_service(*_, **__) -> str:
        return "test-nonce-value"

    monkeypatch.setattr("auth.router.oauth.google.authorize_access_token", fake_authorize_access_token)
    monkeypatch.setattr("auth.router.google_auth_service", fake_google_auth_service)

    response = client.get("/auth/google/callback", follow_redirects=False)

    # Callback should redirect to the frontend verify page.
    assert response.status_code in (302, 307)
    location = response.headers.get("location", "")
    assert "nonce=test-nonce-value" in location
    assert "/verify/google" in location

    # Auth cookies must NOT be set by the callback — only the handshake does that.
    assert "access_token=" not in response.headers.get("set-cookie", "")
    assert "refresh_token=" not in response.headers.get("set-cookie", "")


def test_google_handshake_sets_auth_cookies(client, monkeypatch) -> None:
    """Posting a valid nonce to /google/handshake should set auth cookies."""
    async def fake_google_handshake_service(*_, **__) -> dict[str, str]:
        return {"access_token": "access-token", "refresh_token": "refresh-token"}

    monkeypatch.setattr("auth.router.google_handshake_service", fake_google_handshake_service)

    response = client.post("/auth/google/handshake", json={"nonce": "some-valid-nonce"})

    assert response.status_code == 200
    assert "access_token=" in response.headers.get("set-cookie", "")
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert response.json()["access_token"] == "access-token"
    assert response.json()["refresh_token"] == "refresh-token"


def test_google_handshake_rejects_invalid_nonce(client, monkeypatch) -> None:
    """An invalid or already-used nonce should return 401."""
    from exceptions import UnauthorizedException

    async def fake_google_handshake_service(*_, **__) -> dict[str, str]:
        raise UnauthorizedException("Invalid or expired handshake nonce")

    monkeypatch.setattr("auth.router.google_handshake_service", fake_google_handshake_service)

    response = client.post("/auth/google/handshake", json={"nonce": "bad-nonce"})

    assert response.status_code == 401
