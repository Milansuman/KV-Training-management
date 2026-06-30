def authenticate(client) -> None:
    client.post(
        "/auth/register",
        json={
            "username": "admin99999999",
            "display_name": "Admin User",
            "email": "admin@example.com",
            "password": "secret",
        },
    )
    client.post(
        "/auth/login",
        json={"username_or_email": "admin99999999", "password": "secret"},
    )


def submission_payload(
    user_id: int = 1,
    feedback_id: int = 1,
    recipient_id: int | None = 2,
    text: str = "Good feedback.",
) -> dict:
    return {
        "user_id": user_id,
        "recipient_id": recipient_id,
        "feedback_id": feedback_id,
        "text": text,
    }


def test_create_feedback_submission_returns_201(client) -> None:
    authenticate(client)

    response = client.post("/feedback-submissions", json=submission_payload())

    assert response.status_code == 200
    data = response.json()
    assert data["id"] is not None
    assert data["user_id"] == 1
    assert data["feedback_id"] == 1
    assert data["text"] == "Good feedback."


def test_create_feedback_submission_without_recipient(client) -> None:
    authenticate(client)

    response = client.post("/feedback-submissions", json=submission_payload(recipient_id=None))

    assert response.status_code == 200
    assert response.json()["recipient_id"] is None


def test_create_feedback_submission_unauthenticated_fails(client) -> None:
    response = client.post("/feedback-submissions", json=submission_payload())

    assert response.status_code == 401


def test_create_feedback_submission_missing_text_fails(client) -> None:
    authenticate(client)
    payload = {"user_id": 1, "feedback_id": 1}

    response = client.post("/feedback-submissions", json=payload)

    assert response.status_code == 422


def test_create_feedback_submission_missing_user_id_fails(client) -> None:
    authenticate(client)
    payload = {"feedback_id": 1, "text": "Missing user."}

    response = client.post("/feedback-submissions", json=payload)

    assert response.status_code == 422


def test_create_feedback_submission_missing_feedback_id_fails(client) -> None:
    authenticate(client)
    payload = {"user_id": 1, "text": "Missing feedback id."}

    response = client.post("/feedback-submissions", json=payload)

    assert response.status_code == 422


def test_create_feedback_submission_response_has_submitted_at(client) -> None:
    authenticate(client)

    response = client.post("/feedback-submissions", json=submission_payload())

    assert response.status_code == 200
    assert response.json()["submitted_at"] is not None
