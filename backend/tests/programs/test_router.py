"""HTTP-level tests for the /programs router."""

PROGRAM_PAYLOAD = {
    "title": "Freshers Training",
    "description": "Training for new joiners",
    "start_date": "2025-01-01",
    "end_date": "2025-06-30",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_admin(client):
    """Register the first user (auto-promoted to admin) and return the response body."""
    return client.post(
        "/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "display_name": "Admin User",
            "password": "secret",
        },
    ).json()


def _login_admin(client):
    """Login as admin and return the access_token cookie value."""
    response = client.post(
        "/auth/login",
        json={"username_or_email": "admin", "password": "secret"},
    )
    return response.cookies.get("access_token")


def _setup_admin(client):
    """Register + login admin, return (user_id, access_token)."""
    user = _register_admin(client)
    token = _login_admin(client)
    return user["id"], token


def _create_program(client, access_token, payload=None):
    return client.post(
        "/programs",
        json=payload or PROGRAM_PAYLOAD,
        cookies={"access_token": access_token},
    )


# ---------------------------------------------------------------------------
# POST /programs
# ---------------------------------------------------------------------------

def test_create_program_admin_returns_201(client) -> None:
    _, token = _setup_admin(client)
    response = _create_program(client, token)

    assert response.status_code == 201


def test_create_program_returns_correct_fields(client) -> None:
    _, token = _setup_admin(client)
    response = _create_program(client, token)
    body = response.json()

    assert body["title"] == PROGRAM_PAYLOAD["title"]
    assert body["description"] == PROGRAM_PAYLOAD["description"]
    assert body["start_date"] == PROGRAM_PAYLOAD["start_date"]
    assert body["end_date"] == PROGRAM_PAYLOAD["end_date"]
    assert "id" in body
    assert "created_at" in body


def test_create_program_without_auth_returns_401(client) -> None:
    response = client.post("/programs", json=PROGRAM_PAYLOAD)

    assert response.status_code == 401


def test_create_program_non_admin_returns_403(client) -> None:
    # First user is admin; second user is not.
    _setup_admin(client)
    client.post(
        "/auth/register",
        json={
            "username": "member",
            "email": "member@example.com",
            "display_name": "Member",
            "password": "secret",
        },
    )
    member_token = client.post(
        "/auth/login",
        json={"username_or_email": "member", "password": "secret"},
    ).cookies.get("access_token")

    response = _create_program(client, member_token)

    assert response.status_code == 403


def test_create_program_missing_fields_returns_422(client) -> None:
    _, token = _setup_admin(client)
    response = client.post(
        "/programs",
        json={"title": "Incomplete"},
        cookies={"access_token": token},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /programs/progress/{user_id}
# ---------------------------------------------------------------------------

def test_get_progress_empty_for_user_with_no_programs(client) -> None:
    user = _register_admin(client)
    response = client.get(f"/programs/progress/{user['id']}")

    assert response.status_code == 200
    assert response.json() == []


def test_get_progress_returns_program_for_user(client) -> None:
    user_id, token = _setup_admin(client)
    _create_program(client, token)

    response = client.get(f"/programs/progress/{user_id}")
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 1
    assert body[0]["title"] == PROGRAM_PAYLOAD["title"]
    assert body[0]["description"] == PROGRAM_PAYLOAD["description"]
    assert "total_sessions" in body[0]
    assert "completed_sessions" in body[0]
    assert "created_at" in body[0]
    assert "updated_at" in body[0]


def test_get_progress_session_counts_default_to_zero(client) -> None:
    user_id, token = _setup_admin(client)
    _create_program(client, token)

    body = client.get(f"/programs/progress/{user_id}").json()

    assert body[0]["total_sessions"] == 0
    assert body[0]["completed_sessions"] == 0


def test_get_progress_excludes_deleted_programs(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    client.delete(f"/programs/{program_id}")

    body = client.get(f"/programs/progress/{user_id}").json()
    assert body == []


def test_get_progress_returns_only_programs_for_given_user(client) -> None:
    # Admin creates a program — only admin should see it.
    user_id, token = _setup_admin(client)
    _create_program(client, token)

    other_user = client.post(
        "/auth/register",
        json={
            "username": "other",
            "email": "other@example.com",
            "display_name": "Other",
            "password": "secret",
        },
    ).json()

    body = client.get(f"/programs/progress/{other_user['id']}").json()
    assert body == []

    body = client.get(f"/programs/progress/{user_id}").json()
    assert len(body) == 1


# ---------------------------------------------------------------------------
# PATCH /programs/{program_id}
# ---------------------------------------------------------------------------

def test_update_program_returns_200_with_updated_title(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    response = client.patch(
        f"/programs/{program_id}",
        json={"title": "Updated Title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_program_partial_only_changes_sent_fields(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    response = client.patch(
        f"/programs/{program_id}",
        json={"description": "New description"},
    )
    body = response.json()

    assert body["description"] == "New description"
    assert body["title"] == PROGRAM_PAYLOAD["title"]
    assert body["start_date"] == PROGRAM_PAYLOAD["start_date"]
    assert body["end_date"] == PROGRAM_PAYLOAD["end_date"]


def test_update_program_all_fields(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    response = client.patch(
        f"/programs/{program_id}",
        json={
            "title": "New Title",
            "description": "New desc",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        },
    )
    body = response.json()

    assert body["title"] == "New Title"
    assert body["description"] == "New desc"
    assert body["start_date"] == "2026-01-01"
    assert body["end_date"] == "2026-12-31"


def test_update_program_nonexistent_returns_404(client) -> None:
    response = client.patch("/programs/99999", json={"title": "X"})

    assert response.status_code == 404


def test_update_deleted_program_returns_404(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]
    client.delete(f"/programs/{program_id}")

    response = client.patch(f"/programs/{program_id}", json={"title": "X"})

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /programs/{program_id}
# ---------------------------------------------------------------------------

def test_delete_program_returns_204(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    response = client.delete(f"/programs/{program_id}")

    assert response.status_code == 204


def test_delete_program_nonexistent_returns_404(client) -> None:
    response = client.delete("/programs/99999")

    assert response.status_code == 404


def test_delete_program_twice_returns_404(client) -> None:
    _, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]
    client.delete(f"/programs/{program_id}")

    response = client.delete(f"/programs/{program_id}")

    assert response.status_code == 404


def test_deleted_program_no_longer_appears_in_progress(client) -> None:
    user_id, token = _setup_admin(client)
    program_id = _create_program(client, token).json()["id"]

    client.delete(f"/programs/{program_id}")

    body = client.get(f"/programs/progress/{user_id}").json()
    assert body == []
