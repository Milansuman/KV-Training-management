"""
Tests for ai/feedback LangGraph nodes.

No database or Groq API access needed — DB queries are mocked and the
LLM node is mocked so no API key is required.
"""
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ai.feedback.nodes import (
    fetch_and_group_feedbacks,
    fetch_user_role,
    handle_error,
    summarize_feedbacks,
)
from ai.feedback.state import FeedbackSummaryState
from models.session_permission import SessionRoles


# ── Helpers ────────────────────────────────────────────────────────────────

def _state(**kwargs) -> FeedbackSummaryState:
    base: FeedbackSummaryState = {
        "user_id": 5,
        "session_id": 1,
        "db": MagicMock(),
        "user_role": None,
        "grouped_feedbacks": None,
        "summaries": None,
        "error": None,
    }
    base.update(kwargs)
    return base


def _mock_permission(role: SessionRoles) -> MagicMock:
    perm = MagicMock()
    perm.role = role
    return perm


# ── fetch_user_role ────────────────────────────────────────────────────────

def _mock_db_scalars(permission):
    """Return a db mock where await db.scalars(...) gives a sync result with .first()."""
    scalars_result = MagicMock()
    scalars_result.first.return_value = permission
    db = MagicMock()
    db.scalars = AsyncMock(return_value=scalars_result)
    return db


def _mock_db_execute(rows):
    """Return a db mock where await db.execute(...) gives a sync result with .all()."""
    execute_result = MagicMock()
    execute_result.all.return_value = rows
    db = MagicMock()
    db.execute = AsyncMock(return_value=execute_result)
    return db


@pytest.mark.asyncio
async def test_fetch_user_role_returns_role_value():
    state = _state(db=_mock_db_scalars(_mock_permission(SessionRoles.CANDIDATE)))
    result = await fetch_user_role(state)

    assert result["user_role"] == "CANDIDATE"
    assert result["error"] is None


@pytest.mark.asyncio
async def test_fetch_user_role_trainer():
    result = await fetch_user_role(_state(db=_mock_db_scalars(_mock_permission(SessionRoles.TRAINER))))
    assert result["user_role"] == "TRAINER"


@pytest.mark.asyncio
async def test_fetch_user_role_moderator():
    result = await fetch_user_role(_state(db=_mock_db_scalars(_mock_permission(SessionRoles.MODERATOR))))
    assert result["user_role"] == "MODERATOR"


@pytest.mark.asyncio
async def test_fetch_user_role_not_found_sets_error():
    result = await fetch_user_role(_state(db=_mock_db_scalars(None)))

    assert result["error"] is not None
    assert "no role" in result["error"]


@pytest.mark.asyncio
async def test_fetch_user_role_db_exception_sets_error():
    db = MagicMock()
    db.scalars = AsyncMock(side_effect=Exception("DB connection lost"))

    result = await fetch_user_role(_state(db=db))

    assert result["error"] is not None
    assert "fetch_user_role failed" in result["error"]


# ── fetch_and_group_feedbacks ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_fetch_and_group_passes_through_on_error():
    state = _state(error="upstream error", user_role="CANDIDATE")
    result = await fetch_and_group_feedbacks(state)
    assert result["error"] == "upstream error"
    assert result["grouped_feedbacks"] is None


@pytest.mark.asyncio
async def test_fetch_and_group_candidate_groups_trainer_and_moderator():
    rows = [("Trainer feedback text", SessionRoles.TRAINER), ("Moderator feedback text", SessionRoles.MODERATOR)]
    result = await fetch_and_group_feedbacks(_state(db=_mock_db_execute(rows), user_role="CANDIDATE"))

    assert result["error"] is None
    assert result["grouped_feedbacks"]["trainer"] == ["Trainer feedback text"]
    assert result["grouped_feedbacks"]["moderator"] == ["Moderator feedback text"]


@pytest.mark.asyncio
async def test_fetch_and_group_trainer_only_gets_moderator_feedback():
    rows = [("Moderator comment", SessionRoles.MODERATOR)]
    result = await fetch_and_group_feedbacks(_state(db=_mock_db_execute(rows), user_role="TRAINER"))

    assert result["error"] is None
    assert "moderator" in result["grouped_feedbacks"]
    assert "trainer" not in result["grouped_feedbacks"]


@pytest.mark.asyncio
async def test_fetch_and_group_moderator_gets_all_roles():
    rows = [
        ("Trainer says good job", SessionRoles.TRAINER),
        ("Candidate says thanks", SessionRoles.CANDIDATE),
        ("Other mod says improve X", SessionRoles.MODERATOR),
    ]
    result = await fetch_and_group_feedbacks(_state(db=_mock_db_execute(rows), user_role="MODERATOR"))

    assert result["error"] is None
    assert set(result["grouped_feedbacks"].keys()) == {"trainer", "candidate", "moderator"}


@pytest.mark.asyncio
async def test_fetch_and_group_multiple_submissions_same_role():
    rows = [("First moderator feedback", SessionRoles.MODERATOR), ("Second moderator feedback", SessionRoles.MODERATOR)]
    result = await fetch_and_group_feedbacks(_state(db=_mock_db_execute(rows), user_role="CANDIDATE"))

    assert len(result["grouped_feedbacks"]["moderator"]) == 2


@pytest.mark.asyncio
async def test_fetch_and_group_no_results_sets_error():
    result = await fetch_and_group_feedbacks(_state(db=_mock_db_execute([]), user_role="CANDIDATE"))

    assert result["error"] is not None
    assert "No feedback found" in result["error"]


@pytest.mark.asyncio
async def test_fetch_and_group_db_exception_sets_error():
    db = MagicMock()
    db.execute = AsyncMock(side_effect=Exception("query failed"))
    result = await fetch_and_group_feedbacks(_state(db=db, user_role="CANDIDATE"))

    assert result["error"] is not None
    assert "fetch_and_group_feedbacks failed" in result["error"]


# ── summarize_feedbacks ────────────────────────────────────────────────────

def _mock_llm_response(payload: dict) -> MagicMock:
    mock_message = MagicMock()
    mock_message.content = json.dumps(payload)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


def test_summarize_passes_through_on_error():
    state = _state(error="fetch failed", grouped_feedbacks=None)
    result = summarize_feedbacks(state)
    assert result["error"] == "fetch failed"
    assert result["summaries"] is None


def test_summarize_returns_parsed_summaries():
    expected = {"trainer": "Great performance.", "moderator": "Needs improvement on time."}
    mock_client = _mock_llm_response(expected)

    with patch("ai.feedback.nodes.OpenAI", return_value=mock_client):
        state = _state(
            user_role="CANDIDATE",
            grouped_feedbacks={
                "trainer": ["Great performance."],
                "moderator": ["Needs improvement on time."],
            },
        )
        result = summarize_feedbacks(state)

    assert result["error"] is None
    assert result["summaries"] == expected


def test_summarize_passes_all_feedback_text_to_llm():
    mock_client = _mock_llm_response({"trainer": "summary"})

    with patch("ai.feedback.nodes.OpenAI", return_value=mock_client):
        state = _state(
            user_role="CANDIDATE",
            grouped_feedbacks={"trainer": ["First comment", "Second comment"]},
        )
        summarize_feedbacks(state)

    call_args = mock_client.chat.completions.create.call_args
    user_content = call_args.kwargs["messages"][1]["content"]
    assert "First comment" in user_content
    assert "Second comment" in user_content


def test_summarize_llm_exception_sets_error():
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API timeout")

    with patch("ai.feedback.nodes.OpenAI", return_value=mock_client):
        state = _state(
            user_role="CANDIDATE",
            grouped_feedbacks={"trainer": ["Some text"]},
        )
        result = summarize_feedbacks(state)

    assert result["error"] is not None
    assert "summarize_feedbacks failed" in result["error"]


def test_summarize_uses_json_object_response_format():
    mock_client = _mock_llm_response({"moderator": "summary"})

    with patch("ai.feedback.nodes.OpenAI", return_value=mock_client):
        state = _state(
            user_role="TRAINER",
            grouped_feedbacks={"moderator": ["Good session structure."]},
        )
        summarize_feedbacks(state)

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["response_format"] == {"type": "json_object"}


# ── handle_error ───────────────────────────────────────────────────────────

def test_handle_error_passes_state_through():
    state = _state(error="something broke")
    result = handle_error(state)
    assert result["error"] == "something broke"
    assert result["summaries"] is None
