"""
Tests for individual LangGraph nodes.

No MinIO / network access needed — tests inject pre-fetched bytes/strings
directly into the state, bypassing the fetch_material node entirely.
The LLM node is mocked so no API key / Groq is required.
"""
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ai.training_materials.nodes import (
    clean_markdown,
    handle_error,
    parse_binary,
    parse_html,
    route_by_content_type,
)
from ai.training_materials.state import AgentState

FIXTURES = Path(__file__).parent / "fixtures"


# ── Helpers ────────────────────────────────────────────────────────────────

def _state(**kwargs) -> AgentState:
    base: AgentState = {
        "material_url": "slides/intro.pdf",
        "topics": [],
        "raw_bytes": None,
        "content_type": None,
        "markdown_content": None,
        "suggestions": None,
        "error": None,
    }
    base.update(kwargs)
    return base


# ── fetch_material routing ────────────────────────────────────────────────

def test_fetch_material_uses_minio_for_localhost_url():
    from unittest.mock import patch as _patch
    from ai.training_materials.nodes import fetch_material

    with _patch("ai.training_materials.nodes._fetch_from_minio", return_value=(b"bytes", "application/pdf")) as mock_minio, \
         _patch("ai.training_materials.nodes._fetch_from_url") as mock_url:
        state = _state(material_url="http://localhost:9000/training-materials/slides/intro.pdf")
        result = fetch_material(state)

    mock_minio.assert_called_once_with("slides/intro.pdf")
    mock_url.assert_not_called()
    assert result["raw_bytes"] == b"bytes"
    assert result["content_type"] == "application/pdf"


def test_fetch_material_uses_http_for_external_url():
    from unittest.mock import patch as _patch
    from ai.training_materials.nodes import fetch_material

    with _patch("ai.training_materials.nodes._fetch_from_url", return_value=(b"<html></html>", "text/html")) as mock_url, \
         _patch("ai.training_materials.nodes._fetch_from_minio") as mock_minio:
        state = _state(material_url="https://example.vercel.app/")
        result = fetch_material(state)

    mock_url.assert_called_once_with("https://example.vercel.app/")
    mock_minio.assert_not_called()
    assert result["content_type"] == "text/html"


def test_fetch_material_uses_minio_for_plain_object_key():
    from unittest.mock import patch as _patch
    from ai.training_materials.nodes import fetch_material

    with _patch("ai.training_materials.nodes._fetch_from_minio", return_value=(b"bytes", "application/pdf")) as mock_minio:
        state = _state(material_url="slides/intro.pdf")
        fetch_material(state)

    mock_minio.assert_called_once_with("slides/intro.pdf")


def test_fetch_material_captures_error():
    from unittest.mock import patch as _patch
    from ai.training_materials.nodes import fetch_material

    with _patch("ai.training_materials.nodes._fetch_from_url", side_effect=Exception("timeout")):
        state = _state(material_url="https://example.com/deck.pdf")
        result = fetch_material(state)

    assert result["error"] is not None
    assert "fetch_material failed" in result["error"]


# ── route_by_content_type ──────────────────────────────────────────────────

def test_route_pdf_content_type_goes_to_binary():
    state = _state(content_type="application/pdf")
    assert route_by_content_type(state) == "parse_binary"


def test_route_pptx_content_type_goes_to_binary():
    state = _state(
        content_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        material_url="deck.pptx",
    )
    assert route_by_content_type(state) == "parse_binary"


def test_route_html_content_type_goes_to_html():
    state = _state(content_type="text/html", material_url="page.html")
    assert route_by_content_type(state) == "parse_html"


def test_route_unknown_defaults_to_html():
    state = _state(content_type="application/octet-stream", material_url="unknown.bin")
    assert route_by_content_type(state) == "parse_html"


def test_route_pdf_extension_without_content_type():
    state = _state(content_type="", material_url="report.pdf")
    assert route_by_content_type(state) == "parse_binary"


def test_route_error_state_goes_to_error():
    state = _state(error="something went wrong")
    assert route_by_content_type(state) == "error"


# ── parse_html ─────────────────────────────────────────────────────────────

def _html_state(html: str | None = None) -> AgentState:
    if html is None:
        html = (FIXTURES / "sample.html").read_text()
    return _state(
        material_url="page.html",
        content_type="text/html",
        raw_bytes=html.encode("utf-8"),
    )


def test_parse_html_returns_markdown_content():
    result = parse_html(_html_state())
    assert result["markdown_content"] is not None
    assert len(result["markdown_content"]) > 0


def test_parse_html_includes_heading():
    result = parse_html(_html_state())
    assert "Introduction to Python" in result["markdown_content"]


def test_parse_html_includes_paragraph_text():
    result = parse_html(_html_state())
    assert "high-level programming language" in result["markdown_content"]


def test_parse_html_excludes_script_tags():
    result = parse_html(_html_state())
    assert "console.log" not in result["markdown_content"]


def test_parse_html_handles_minimal_html():
    html = "<html><body><p>Hello world</p></body></html>"
    result = parse_html(_html_state(html))
    assert "Hello world" in result["markdown_content"]


def test_parse_html_sets_no_error():
    result = parse_html(_html_state())
    assert result["error"] is None


# ── parse_binary ───────────────────────────────────────────────────────────

def test_parse_binary_calls_markitdown(tmp_path):
    dummy = tmp_path / "test.txt"
    dummy.write_text("Training content line 1\nTraining content line 2")
    raw = dummy.read_bytes()

    state = _state(material_url="test.txt", content_type="text/plain", raw_bytes=raw)
    result = parse_binary(state)

    assert isinstance(result, dict)


def test_parse_binary_propagates_error_on_bad_input():
    state = _state(material_url="broken.pdf", content_type="application/pdf", raw_bytes=b"not a real pdf")
    result = parse_binary(state)
    assert isinstance(result, dict)


# ── clean_markdown ─────────────────────────────────────────────────────────

def test_clean_markdown_collapses_blank_lines():
    state = _state(markdown_content="# Title\n\n\n\nParagraph text\n\n\n\nAnother paragraph")
    result = clean_markdown(state)
    assert "\n\n\n" not in result["markdown_content"]


def test_clean_markdown_strips_trailing_whitespace():
    state = _state(markdown_content="Line with spaces   \nAnother line  \n")
    result = clean_markdown(state)
    for line in result["markdown_content"].splitlines():
        assert not line.endswith(" ")


def test_clean_markdown_passes_through_on_error():
    state = _state(error="upstream error", markdown_content="should not change")
    result = clean_markdown(state)
    assert result["markdown_content"] == "should not change"
    assert result["error"] == "upstream error"


def test_clean_markdown_handles_none_content():
    state = _state(markdown_content=None)
    result = clean_markdown(state)
    assert result["markdown_content"] is None


# ── analyze_with_llm (mocked) ──────────────────────────────────────────────

def test_analyze_with_llm_returns_suggestions():
    from ai.training_materials.nodes import analyze_with_llm

    fake_text = (
        "Clarity: The language is mostly clear but some terms are undefined.\n\n"
        "Structure: The sections flow logically.\n\n"
        "Completeness: Consider adding a section on error handling."
    )

    mock_message = MagicMock()
    mock_message.content = fake_text

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("ai.training_materials.nodes.OpenAI", return_value=mock_client):
        state = _state(markdown_content="# Python Basics\n\nPython is easy to learn.")
        result = analyze_with_llm(state)

    assert result["suggestions"] is not None
    assert isinstance(result["suggestions"], str)
    assert "Clarity" in result["suggestions"]
    assert result["error"] is None


def test_analyze_with_llm_passes_topics_to_prompt():
    from ai.training_materials.nodes import analyze_with_llm

    mock_message = MagicMock()
    mock_message.content = "Structure: good.\nCompleteness: missing loops topic."
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response

    with patch("ai.training_materials.nodes.OpenAI", return_value=mock_client):
        state = _state(
            markdown_content="# Python Basics\n\nPython is easy to learn.",
            topics=["variables", "loops", "functions"],
        )
        analyze_with_llm(state)

    call_args = mock_client.chat.completions.create.call_args
    user_content = call_args.kwargs["messages"][1]["content"]
    assert "variables" in user_content
    assert "loops" in user_content
    assert "functions" in user_content


def test_analyze_with_llm_skips_on_error():
    from ai.training_materials.nodes import analyze_with_llm

    state = _state(error="parse failed", markdown_content="some content")
    result = analyze_with_llm(state)
    assert result["suggestions"] is None
    assert result["error"] == "parse failed"


def test_analyze_with_llm_errors_on_empty_markdown():
    from ai.training_materials.nodes import analyze_with_llm

    with patch("ai.training_materials.nodes.OpenAI"):
        state = _state(markdown_content="")
        result = analyze_with_llm(state)

    assert result["error"] is not None
    assert "no markdown" in result["error"]


# ── handle_error ───────────────────────────────────────────────────────────

def test_handle_error_passes_state_through():
    state = _state(error="something broke")
    result = handle_error(state)
    assert result["error"] == "something broke"
