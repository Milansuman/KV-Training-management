"""HTTP-level tests for the /assignment-submissions router."""

from datetime import datetime, timezone, timedelta


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _setup_admin(client):
    """Register + login admin, return (user_id, access_token)."""
    user = client.post(
        "/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "display_name": "Admin User",
            "password": "secret",
        },
    ).json()
    token = client.post(
        "/auth/login",
        json={"username_or_email": "admin", "password": "secret"},
    ).cookies.get("access_token")
    return user["id"], token


def _create_session(client, token):
    """Create a session via POST /sessions and return its id."""
    start = datetime.now(timezone.utc)
    response = client.post(
        "/sessions",
        json={
            "title": "Session for Submissions",
            "description": "Test session",
            "start_datetime": start.isoformat(),
            "end_datetime": (start + timedelta(hours=2)).isoformat(),
            "program_id": 1,
        },
        cookies={"access_token": token},
    )
    return response.json()["id"]


def _create_assignment(client, token, session_id):
    """Create an assignment and return its id."""
    response = client.post(
        "/assignments",
        json={
            "title": "Build a REST API",
            "description": "Create a RESTful API using FastAPI",
            "session_id": session_id,
            "due_at": "2099-07-15T23:59:59",
        },
    )
    return response.json()["id"]


def _setup_data(client):
    """Register admin, create a session and an assignment.

    Returns (user_id, access_token, assignment_id).
    """
    user_id, token = _setup_admin(client)
    session_id = _create_session(client, token)
    assignment_id = _create_assignment(client, token, session_id)
    return user_id, token, assignment_id


SUBMISSION_PAYLOAD = {
    "url": "https://github.com/user/assignment-submission",
}


# ---------------------------------------------------------------------------
# POST /assignment-submissions
# ---------------------------------------------------------------------------

def test_create_submission_returns_submission(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    response = client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["url"] == SUBMISSION_PAYLOAD["url"]
    assert body["user_id"] == user_id
    assert body["assignment_id"] == assignment_id
    assert "id" in body
    assert "created_at" in body


def test_create_submission_unauthenticated_fails(client) -> None:
    response = client.post(
        "/assignment-submissions",
        json={
            "url": "https://example.com/submit",
            "user_id": 1,
            "assignment_id": 1,
        },
    )

    assert response.status_code == 401


def test_create_submission_missing_fields_returns_422(client) -> None:
    user_id, token, _ = _setup_data(client)

    response = client.post(
        "/assignment-submissions",
        json={"user_id": user_id},
        cookies={"access_token": token},
    )

    assert response.status_code == 422


def test_create_submission_missing_user_returns_404(client) -> None:
    _, token, assignment_id = _setup_data(client)

    response = client.post(
        "/assignment-submissions",
        json={
            "url": "https://example.com/submit",
            "user_id": 99999,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )

    assert response.status_code == 404


def test_create_submission_missing_assignment_returns_404(client) -> None:
    user_id, token, _ = _setup_data(client)

    response = client.post(
        "/assignment-submissions",
        json={
            "url": "https://example.com/submit",
            "user_id": user_id,
            "assignment_id": 99999,
        },
        cookies={"access_token": token},
    )

    assert response.status_code == 404


def test_create_submission_duplicate_returns_409(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    payload = {
        **SUBMISSION_PAYLOAD,
        "user_id": user_id,
        "assignment_id": assignment_id,
    }

    client.post(
        "/assignment-submissions",
        json=payload,
        cookies={"access_token": token},
    )

    response = client.post(
        "/assignment-submissions",
        json=payload,
        cookies={"access_token": token},
    )

    assert response.status_code == 409


# ---------------------------------------------------------------------------
# GET /assignment-submissions/{submission_id}
# ---------------------------------------------------------------------------

def test_get_submission_by_id_returns_submission(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    create_resp = client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )
    submission_id = create_resp.json()["id"]

    response = client.get(f"/assignment-submissions/{submission_id}")

    assert response.status_code == 200
    assert response.json()["id"] == submission_id
    assert response.json()["url"] == SUBMISSION_PAYLOAD["url"]


def test_get_submission_by_id_returns_404_for_missing(client) -> None:
    response = client.get("/assignment-submissions/99999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /assignment-submissions/assignment/{assignment_id}
# ---------------------------------------------------------------------------

def test_get_submissions_by_assignment_returns_list(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )

    # Register a second user and create another submission
    second_user = client.post(
        "/auth/register",
        json={
            "username": "second",
            "email": "second@example.com",
            "display_name": "Second",
            "password": "secret",
        },
    ).json()
    second_token = client.post(
        "/auth/login",
        json={"username_or_email": "second", "password": "secret"},
    ).cookies.get("access_token")

    client.post(
        "/assignment-submissions",
        json={
            "url": "https://github.com/second/submission",
            "user_id": second_user["id"],
            "assignment_id": assignment_id,
        },
        cookies={"access_token": second_token},
    )

    response = client.get(f"/assignment-submissions/assignment/{assignment_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(s["assignment_id"] == assignment_id for s in data)


def test_get_submissions_by_assignment_empty_returns_empty_list(client) -> None:
    _, token, assignment_id = _setup_data(client)

    response = client.get(f"/assignment-submissions/assignment/{assignment_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_get_submissions_by_assignment_missing_returns_404(client) -> None:
    response = client.get("/assignment-submissions/assignment/99999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# GET /assignment-submissions/user/{user_id}
# ---------------------------------------------------------------------------

def test_get_submissions_by_user_returns_list(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )

    response = client.get(f"/assignment-submissions/user/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user_id


def test_get_submissions_by_user_empty_returns_empty_list(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    # No submissions created for user
    response = client.get(f"/assignment-submissions/user/{user_id}")

    assert response.status_code == 200
    assert response.json() == []


def test_get_submissions_by_user_missing_returns_404(client) -> None:
    response = client.get("/assignment-submissions/user/99999")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# PATCH /assignment-submissions/{submission_id}
# ---------------------------------------------------------------------------

def test_patch_submission_updates_url(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    create_resp = client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )
    submission_id = create_resp.json()["id"]

    response = client.patch(
        f"/assignment-submissions/{submission_id}",
        json={"url": "https://github.com/user/updated-submission"},
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    assert response.json()["url"] == "https://github.com/user/updated-submission"


def test_patch_submission_missing_returns_404(client) -> None:
    _, token, _ = _setup_data(client)

    response = client.patch(
        "/assignment-submissions/99999",
        json={"url": "https://example.com/new-url"},
        cookies={"access_token": token},
    )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /assignment-submissions/{submission_id}
# ---------------------------------------------------------------------------

def test_delete_submission_returns_message(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    create_resp = client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )
    submission_id = create_resp.json()["id"]

    response = client.delete(
        f"/assignment-submissions/{submission_id}",
        cookies={"access_token": token},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Submission deleted successfully"


def test_delete_submission_makes_submission_unavailable(client) -> None:
    user_id, token, assignment_id = _setup_data(client)

    create_resp = client.post(
        "/assignment-submissions",
        json={
            **SUBMISSION_PAYLOAD,
            "user_id": user_id,
            "assignment_id": assignment_id,
        },
        cookies={"access_token": token},
    )
    submission_id = create_resp.json()["id"]

    client.delete(
        f"/assignment-submissions/{submission_id}",
        cookies={"access_token": token},
    )

    response = client.get(f"/assignment-submissions/{submission_id}")
    assert response.status_code == 404


def test_delete_submission_nonexistent_returns_404(client) -> None:
    _, token, _ = _setup_data(client)

    response = client.delete(
        "/assignment-submissions/99999",
        cookies={"access_token": token},
    )

    assert response.status_code == 404
