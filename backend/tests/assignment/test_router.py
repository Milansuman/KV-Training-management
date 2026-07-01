"""HTTP-level tests for the /assignments router."""

from datetime import datetime, timezone, timedelta

import pytest

from models.session_permission import SessionPermission, SessionRoles


ASSIGNMENT_PAYLOAD = {
    "title": "Build a REST API",
    "description": "Create a RESTful API using FastAPI",
    "due_at": "2099-07-15T23:59:59",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _register_admin(client):
    """Register the first user (auto-promoted to admin) and return the body."""
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
    """Login as admin and return the access_token cookie."""
    response = client.post(
        "/auth/login",
        json={"username_or_email": "admin", "password": "secret"},
    )
    return response.cookies.get("access_token")


def _setup_admin(client):
    """Register + login admin, return (user_id, access_token, session_id)."""
    admin = _register_admin(client)
    token = _login_admin(client)
    return admin["id"], token


def _create_session(client, token):
    """Create a session via POST /sessions and return its id."""
    start = datetime.now(timezone.utc)
    response = client.post(
        "/sessions",
        json={
            "title": "Session for Assignments",
            "description": "Test session",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=2)).isoformat(),
            "program_id": 1,
        },
        cookies={"access_token": token},
    )
    return response.json()["id"]


def _create_assignment(client, token, session_id, payload=None):
    """Helper to create an assignment."""
    body = dict(ASSIGNMENT_PAYLOAD)
    if payload:
        body.update(payload)
    body["session_id"] = session_id
    return client.post(
        "/assignments",
        json=body,
        cookies={"access_token": token},
    )



# ---------------------------------------------------------------------------
# POST /assignments
# ---------------------------------------------------------------------------

def test_create_assignment_admin_returns_201(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)

    response = _create_assignment(client, token, session_id)

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == ASSIGNMENT_PAYLOAD["title"]
    assert body["description"] == ASSIGNMENT_PAYLOAD["description"]
    assert body["session_id"] == session_id
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body

def test_create_submission_missing_user_returns_404(client):
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    response = client.post(
        "/assignment-submissions",
        json={
            "url": "https://example.com/submission.pdf",
            "user_id": 99999,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found 99999"

@pytest.mark.asyncio
async def test_create_assignment_trainer_returns_201(client, db_session) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)

    trainer = client.post(
        "/auth/register",
        json={
            "username": "trainer",
            "email": "trainer@example.com",
            "display_name": "Trainer User",
            "password": "secret",
        },
    ).json()
    trainer_token = client.post(
        "/auth/login",
        json={"username_or_email": "trainer", "password": "secret"},
    ).cookies.get("access_token")

    db_session.add(
        SessionPermission(
            user_id=trainer["id"],
            session_id=session_id,
            role=SessionRoles.TRAINER,
        )
    )
    await db_session.commit()

    response = _create_assignment(client, trainer_token, session_id, {"title": "Trainer Assignment"})

    assert response.status_code == 200
    assert response.json()["title"] == "Trainer Assignment"
    assert response.json()["session_id"] == session_id

@pytest.mark.asyncio
async def test_create_assignment_nontrainer_returns_401(client, db_session) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)

    trainer = client.post(
        "/auth/register",
        json={
            "username": "trainer",
            "email": "trainer@example.com",
            "display_name": "Trainer User",
            "password": "secret",
        },
    ).json()
    trainer_token = client.post(
        "/auth/login",
        json={"username_or_email": "trainer", "password": "secret"},
    ).cookies.get("access_token")

    db_session.add(
        SessionPermission(
            user_id=trainer["id"],
            session_id=session_id,
            role=SessionRoles.CANDIDATE,
        )
    )
    await db_session.commit()

    response = _create_assignment(client, trainer_token, session_id, {"title": "Trainer Assignment"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_assignment_trainee_cannot_create_assignment(
    client,
    db_session,
):
    _, admin_token = _setup_admin(client)
    session_id = _create_session(client, admin_token)

    trainee = client.post(
        "/auth/register",
        json={
            "username": "trainee",
            "email": "trainee@example.com",
            "display_name": "Trainee User"})

def test_create_assignment_non_admin_returns_401(client) -> None:
    # First user (admin) is created internally
    _setup_admin(client)

    # Register a second user (non-admin)
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

    response = client.post(
        "/assignments",
        json={
            "title": "Hack",
            "description": "Should fail",
            "session_id": 1,
            "due_at": "2099-07-15T23:59:59",
        },
        cookies={"access_token": member_token},
    )

    assert response.status_code == 401


def test_create_assignment_unauthenticated_returns_401(client) -> None:
    response = client.post(
        "/assignments",
        json={
            "title": "No Auth",
            "description": "Should fail",
            "session_id": 1,
            "due_at": "2099-07-15T23:59:59",
        },
    )

    assert response.status_code == 401


def test_create_assignment_missing_session_returns_404(client) -> None:
    _, token = _setup_admin(client)

    response = _create_assignment(client, token, session_id=99999)

    assert response.status_code == 404


def test_create_assignment_missing_fields_returns_422(client) -> None:
    _, token = _setup_admin(client)

    response = client.post(
        "/assignments",
        json={"title": "Incomplete"},
        cookies={"access_token": token},
    )

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /assignments
# ---------------------------------------------------------------------------

def test_get_assignments_empty_list_initially(client) -> None:
    response = client.get("/assignments")

    assert response.status_code == 200
    assert response.json() == []


def test_get_assignments_returns_list(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    _create_assignment(client, token, session_id)
    _create_assignment(client, token, session_id, {"title": "Second Assignment"})

    response = client.get("/assignments")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


# ---------------------------------------------------------------------------
# GET /assignments/{assignment_id}
# ---------------------------------------------------------------------------

def test_get_assignment_by_id_returns_assignment(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    create_resp = _create_assignment(client, token, session_id)
    assignment_id = create_resp.json()["id"]

    response = client.get(f"/assignments/{assignment_id}")

    assert response.status_code == 200
    assert response.json()["id"] == assignment_id
    assert response.json()["title"] == ASSIGNMENT_PAYLOAD["title"]


def test_get_assignment_by_id_returns_404_for_missing(client) -> None:
    response = client.get("/assignments/99999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /assignments/session/{session_id}
# ---------------------------------------------------------------------------

def test_get_assignments_by_session_returns_matching(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    _create_assignment(client, token, session_id)

    response = client.get(f"/assignments/session/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["session_id"] == session_id


def test_get_assignments_by_session_empty_when_no_assignments(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)

    response = client.get(f"/assignments/session/{session_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_get_assignments_by_session_returns_404_for_missing_session(client) -> None:
    response = client.get("/assignments/session/99999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /assignments/{assignment_id}
# ---------------------------------------------------------------------------

def test_patch_assignment_admin_updates_title(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    response = client.patch(
        f"/assignments/{assignment_id}",
        json={"title": "Updated Title"},
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_patch_assignment_partial_keeps_other_fields(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    response = client.patch(
        f"/assignments/{assignment_id}",
        json={"description": "New description"},
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "New description"
    assert body["title"] == ASSIGNMENT_PAYLOAD["title"]


def test_patch_assignment_non_admin_returns_401(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    # Register a non-admin
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

    response = client.patch(
        f"/assignments/{assignment_id}",
        json={"title": "Hacked"},
        cookies={"access_token": member_token},
    )

    assert response.status_code == 401


def test_patch_assignment_missing_returns_404(client) -> None:
    _, token = _setup_admin(client)

    response = client.patch(
        "/assignments/99999",
        json={"title": "Ghost"},
        cookies={"access_token": token},
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /assignments/{assignment_id}
# ---------------------------------------------------------------------------

def test_delete_assignment_returns_message(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    response = client.delete(
        f"/assignments/{assignment_id}",
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Assignment deleted successfully"


def test_delete_assignment_non_admin_returns_401(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

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

    response = client.delete(
        f"/assignments/{assignment_id}",
        cookies={"access_token": member_token},
    )

    assert response.status_code == 401


def test_delete_assignment_makes_assignment_unavailable(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    client.delete(
        f"/assignments/{assignment_id}",
        cookies={"access_token": token},
    )

    response = client.get(f"/assignments/{assignment_id}")
    assert response.status_code == 404


def test_delete_assignment_nonexistent_returns_404(client) -> None:
    _, token = _setup_admin(client)

    response = client.delete(
        "/assignments/99999",
        cookies={"access_token": token},
    )

    assert response.status_code == 404


def test_deleted_assignment_excluded_from_list(client) -> None:
    _, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id).json()["id"]

    client.delete(
        f"/assignments/{assignment_id}",
        cookies={"access_token": token},
    )

    response = client.get("/assignments")
    ids = [a["id"] for a in response.json()]
    assert assignment_id not in ids
