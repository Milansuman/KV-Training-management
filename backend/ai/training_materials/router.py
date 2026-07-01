from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.dependencies import get_current_user

from .graph import agent

router = APIRouter(prefix="/ai/training-materials", tags=["AI - Training Materials"])


class AnalyzeRequest(BaseModel):
    material_url: str        # MinIO object key, e.g. "slides/intro.pdf"
    topics: list[str] = []   # Expected topics to verify completeness against


class AnalyzeResponse(BaseModel):
    material_url: str
    suggestions: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_training_material(
    payload: AnalyzeRequest,
    current_user=Depends(get_current_user),
) -> AnalyzeResponse:
    initial_state = {
        "material_url": payload.material_url,
        "topics": payload.topics,
        "raw_bytes": None,
        "content_type": None,
        "markdown_content": None,
        "suggestions": None,
        "error": None,
    }

    result = await agent.ainvoke(initial_state)

    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["error"])

    return AnalyzeResponse(
        material_url=result["material_url"],
        suggestions=result.get("suggestions") or "",
    )
