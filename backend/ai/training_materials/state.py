from typing import Optional
from typing_extensions import TypedDict


class AgentState(TypedDict):
    # Input
    material_url: str          # MinIO object key / path
    topics: list[str]          # Expected topics sent from the UI

    # Set by fetch node
    raw_bytes: Optional[bytes]
    content_type: Optional[str]  # e.g. "application/pdf", "text/html"

    # Set by parser nodes
    markdown_content: Optional[str]

    # Set by LLM node
    suggestions: Optional[str]

    # Error propagation
    error: Optional[str]
