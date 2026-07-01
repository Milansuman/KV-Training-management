import io
import re
from urllib.parse import unquote, urlparse
from typing import Literal

import httpx
from bs4 import BeautifulSoup
from markitdown import MarkItDown
from minio import Minio
from openai import OpenAI

from config import env

from .state import AgentState

_minio = Minio(
    env.MINIO_ENDPOINT,
    access_key=env.MINIO_ACCESS_KEY,
    secret_key=env.MINIO_SECRET_KEY,
    secure=env.MINIO_SECURE,
)

_md_converter = MarkItDown()

_BINARY_TYPES = {
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
}

_BINARY_EXTENSIONS = {".pdf", ".ppt", ".pptx", ".doc", ".docx"}


def _is_minio_url(url: str) -> bool:
    """Return True if the URL points to the configured MinIO endpoint."""
    parsed = urlparse(url)
    return parsed.netloc == env.MINIO_ENDPOINT


def _ext_from_url(url: str) -> str:
    path = urlparse(url).path if url.startswith("http") else url
    return "." + path.rsplit(".", 1)[-1].lower() if "." in path.rsplit("/", 1)[-1] else ""


def _normalise_content_type(content_type: str, url: str) -> str:
    """Fill in content-type from file extension when server returns octet-stream or nothing."""
    if content_type and content_type != "application/octet-stream":
        return content_type
    ext = _ext_from_url(url)
    if ext == ".pdf":
        return "application/pdf"
    if ext in {".ppt", ".pptx"}:
        return "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    if ext in {".doc", ".docx"}:
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    if ext in {".html", ".htm"}:
        return "text/html"
    return content_type


def _fetch_from_minio(object_key: str) -> tuple[bytes, str]:
    """Fetch an object from the configured MinIO bucket."""
    decoded_key = unquote(object_key)
    response = _minio.get_object(env.MINIO_BUCKET, decoded_key)
    raw_bytes = response.read()
    content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
    response.close()
    response.release_conn()
    return raw_bytes, content_type


def _fetch_from_url(url: str) -> tuple[bytes, str]:
    """Fetch a remote URL and return its bytes and content-type."""
    resp = httpx.get(url, follow_redirects=True, timeout=30)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "").split(";")[0].strip()
    return resp.content, content_type


def fetch_material(state: AgentState) -> AgentState:
    """Fetch training material — from MinIO if localhost:9000, otherwise from the URL directly."""
    url = state["material_url"]
    try:
        if _is_minio_url(url):
            # Strip scheme + host + bucket prefix, keep just the object key
            path = urlparse(url).path.lstrip("/")
            bucket_prefix = env.MINIO_BUCKET + "/"
            object_key = path[len(bucket_prefix):] if path.startswith(bucket_prefix) else path
            raw_bytes, content_type = _fetch_from_minio(object_key)
        elif url.startswith("http://") or url.startswith("https://"):
            raw_bytes, content_type = _fetch_from_url(url)
        else:
            # Plain object key (no scheme) — treat as MinIO path directly
            raw_bytes, content_type = _fetch_from_minio(url)

        content_type = _normalise_content_type(content_type, url)
        return {**state, "raw_bytes": raw_bytes, "content_type": content_type}
    except Exception as exc:
        return {**state, "error": f"fetch_material failed: {exc}"}


def route_by_content_type(state: AgentState) -> Literal["parse_binary", "parse_html", "error"]:
    """Conditional edge: decide which parser to send the document to."""
    if state.get("error"):
        return "error"

    ct = state.get("content_type", "")
    ext = "." + state["material_url"].rsplit(".", 1)[-1].lower() if "." in state["material_url"] else ""

    return "parse_binary"


def parse_binary(state: AgentState) -> AgentState:
    """Convert binary document (PDF, PPT, DOCX) to Markdown via markitdown."""
    try:
        file_obj = io.BytesIO(state["raw_bytes"])
        filename = state["material_url"].rsplit("/", 1)[-1]
        result = _md_converter.convert_stream(file_obj, file_extension=f".{filename.rsplit('.', 1)[-1].lower()}")
        return {**state, "markdown_content": result.text_content}
    except Exception as exc:
        return {**state, "error": f"parse_binary failed: {exc}"}


def parse_html(state: AgentState) -> AgentState:
    """Extract readable text from HTML using BeautifulSoup, return as Markdown."""
    try:
        html = state["raw_bytes"].decode("utf-8", errors="replace")
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        main = soup.find("main") or soup.find("article") or soup.find("body") or soup

        lines = []
        for el in main.descendants:
            if el.name in {"h1", "h2", "h3", "h4", "h5", "h6"}:
                level = int(el.name[1])
                lines.append(f"\n{'#' * level} {el.get_text(strip=True)}\n")
            elif el.name == "p":
                text = el.get_text(strip=True)
                if text:
                    lines.append(text + "\n")
            elif el.name == "li":
                text = el.get_text(strip=True)
                if text:
                    lines.append(f"- {text}")
            elif el.name == "code":
                lines.append(f"`{el.get_text(strip=True)}`")
            elif el.name == "pre":
                lines.append(f"\n```\n{el.get_text()}\n```\n")

        markdown = "\n".join(lines)
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return {**state, "markdown_content": markdown}
    except Exception as exc:
        return {**state, "error": f"parse_html failed: {exc}"}


def clean_markdown(state: AgentState) -> AgentState:
    """Light cleanup: strip excessive whitespace, deduplicate blank lines."""
    if state.get("error") or not state.get("markdown_content"):
        return state

    text = state["markdown_content"]
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return {**state, "markdown_content": text.strip()}
_SYSTEM_PROMPT = """\
You are an expert instructional designer reviewing training material content.
Analyse the provided Markdown and give feedback on three areas only:

1. **Clarity** — is the language clear and easy to follow?
2. **Structure** — is the content well-organised and logically ordered?
3. **Completeness** — the user has provided an expected list of topics. Check whether each topic is adequately covered in the material. Call out any topics that are missing or insufficiently explained.

Be concise and specific ,1-2 sentences are enough. If the material is already good in all three areas, respond with exactly:
"Your material is good to go."

Do not use JSON, bullet lists with icons, or any other structured format — just plain text paragraphs, one per area (or the single sign-off line if everything is fine).
"""


def analyze_with_llm(state: AgentState) -> AgentState:
    """Send normalized Markdown to GPT-4o-mini via LiteLLM and return plain-text improvement suggestions."""
    if state.get("error"):
        return state

    content = state.get("markdown_content", "").strip()
    if not content:
        return {**state, "error": "analyze_with_llm: no markdown content to analyze"}

    topics = state.get("topics") or []
    topics_section = (
        "Expected topics to verify:\n" + "\n".join(f"- {t}" for t in topics)
        if topics
        else "No specific topics were provided."
    )

    client = OpenAI(
        api_key=env.GROQ_API_KEY,
        base_url=env.GROQ_BASE_URL,
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"{topics_section}\n\n"
                    f"Training material:\n\n{content}"
                ),
            },
        ],
    )

    suggestions = (response.choices[0].message.content or "").strip()
    return {**state, "suggestions": suggestions}


def handle_error(state: AgentState) -> AgentState:
    """Terminal error node — passes state through unchanged for inspection."""
    return state
