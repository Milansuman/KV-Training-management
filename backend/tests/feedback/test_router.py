from models.feedback import Feedback, FeedbackType
from models.feedback_submission import FeedbackSubmission


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


async def seed_feedback_and_submission(db_session, session_id: int, text: str = "test") -> int:
    feedback = Feedback(session_id=session_id, type=FeedbackType.TEXT)
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)

    submission = FeedbackSubmission(user_id=1, feedback_id=feedback.id, text=text)
    db_session.add(submission)
    await db_session.commit()

    return session_id


def test_get_submissions_by_session_returns_list(client, db_session) -> None:
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        seed_feedback_and_submission(db_session, session_id=100, text="Router test.")
    )
    authenticate(client)

    response = client.get("/feedback/session/100")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["text"] == "Router test."


def test_get_submissions_by_session_returns_empty_list(client) -> None:
    authenticate(client)

    response = client.get("/feedback/session/999")

    assert response.status_code == 200
    assert response.json() == []


def test_get_submissions_by_session_unauthenticated_fails(client) -> None:
    response = client.get("/feedback/session/1")

    assert response.status_code == 401


def test_get_submissions_by_session_response_shape(client, db_session) -> None:
    import asyncio
    asyncio.get_event_loop().run_until_complete(
        seed_feedback_and_submission(db_session, session_id=200, text="Shape check.")
    )
    authenticate(client)

    response = client.get("/feedback/session/200")

    assert response.status_code == 200
    item = response.json()[0]
    assert "id" in item
    assert "user_id" in item
    assert "feedback_id" in item
    assert "text" in item
    assert "submitted_at" in item
