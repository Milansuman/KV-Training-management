from datetime import datetime, timezone, timedelta

def session_payload(program_id: int = 1):
    start = datetime.now(timezone.utc)
    return {
        "title": "Launch Plan",
        "description": "Launch planning session.",
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=2)).isoformat(),
        "program_id": program_id,
    }


def authenticate_admin(client) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "admin99999999",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username_or_email": "admin99999999",
            "password": "secret",
        },
    )

    assert response.status_code == 200


def authenticate_non_admin(client) -> None:
    # First user registered gets admin, so register that one first
    client.post(
        "/auth/register",
        json={
            "username": "admin99999999",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
        },
    )

    # Second user registered gets non-admin
    client.post(
        "/auth/register",
        json={
            "username": "nonadmin",
            "display_name": "Non-Admin User",
            "email": "nonadmin@example.com",
            "password": "secret",
        },
    )

    # Login as the non-admin user
    response = client.post(
        "/auth/login",
        json={
            "username_or_email": "nonadmin",
            "password": "secret",
        },
    )

    assert response.status_code == 200


def test_create_session_returns_session(client) -> None:
    authenticate_admin(client)
    response = client.post("/sessions", json=session_payload())

    assert response.status_code == 200
    assert response.json()["title"] == "Launch Plan"
    assert response.json()["program_id"] == 1
    assert response.json()["id"] is not None


def test_create_session_with_valid_date_range_succeeds(client) -> None:
    authenticate_admin(client)
    start = datetime.now(timezone.utc)
    payload = {
        "title": "Valid Session",
        "description": "Valid dates.",
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=2)).isoformat(),
        "program_id": 1,
    }

    response = client.post("/sessions", json=payload)

    # Valid date range should succeed
    assert response.status_code == 200
    assert response.json()["title"] == "Valid Session"


def test_create_session_unauthenticated_fails(client) -> None:
    response = client.post("/sessions", json=session_payload())
    assert response.status_code == 401


def test_create_session_non_admin_fails(client) -> None:
    authenticate_non_admin(client)
    response = client.post("/sessions", json=session_payload())
    assert response.status_code == 401


def test_get_sessions_returns_list(client) -> None:
    authenticate_admin(client)
    client.post("/sessions", json=session_payload(1))
    client.post("/sessions", json=session_payload(2))

    response = client.get("/sessions")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 2


def test_get_sessions_returns_empty_list_initially(client) -> None:
    response = client.get("/sessions")

    assert response.status_code == 200
    assert response.json() == []


def test_get_session_by_id_returns_session(client) -> None:
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json()["id"] == session_id
    assert response.json()["description"] == "Launch planning session."


def test_get_session_by_id_returns_404_for_missing(client) -> None:
    response = client.get("/sessions/999")

    assert response.status_code == 404


def test_get_sessions_by_program_id_returns_matching_sessions(client) -> None:
    authenticate_admin(client)
    client.post("/sessions", json=session_payload(10))
    client.post("/sessions", json=session_payload(20))

    response = client.get("/sessions/program/10")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["program_id"] == 10


def test_update_session_returns_updated_session(client) -> None:
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]
    start = datetime.now(timezone.utc)
    payload = {
        "title": "Updated Launch Plan",
        "description": "Updated description.",
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=3)).isoformat(),
    }

    response = client.put(f"/sessions/{session_id}", json=payload)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Launch Plan"
    assert response.json()["description"] == "Updated description."


def test_update_session_non_admin_fails(client) -> None:
    # First create session as admin
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    # Now login as non-admin
    authenticate_non_admin(client)
    start = datetime.now(timezone.utc)
    payload = {
        "title": "Updated Launch Plan",
        "description": "Updated description.",
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=3)).isoformat(),
    }
    response = client.put(f"/sessions/{session_id}", json=payload)
    assert response.status_code == 401


def test_update_session_returns_404_for_missing(client) -> None:
    authenticate_admin(client)
    start = datetime.now(timezone.utc)
    payload = {
        "title": "Missing",
        "description": "Missing.",
        "start_datetime": start.isoformat(),
        "end_datetime": (start + timedelta(hours=1)).isoformat(),
    }

    response = client.put("/sessions/999", json=payload)

    assert response.status_code == 404


def test_delete_session_returns_message(client) -> None:
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    response = client.delete(f"/sessions/{session_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Session deleted successfully"


def test_delete_session_non_admin_fails(client) -> None:
    # First create session as admin
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    # Now login as non-admin
    authenticate_non_admin(client)
    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 401


def test_delete_session_makes_session_unavailable(client) -> None:
    authenticate_admin(client)
    create_response = client.post("/sessions", json=session_payload())
    session_id = create_response.json()["id"]

    client.delete(f"/sessions/{session_id}")
    response = client.get(f"/sessions/{session_id}")

    assert response.status_code == 404


def test_delete_session_returns_404_for_missing(client) -> None:
    authenticate_admin(client)
    response = client.delete("/sessions/999")

    assert response.status_code == 404
