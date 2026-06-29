from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.connection import get_db

from topics import service

from topics.schemas import TopicCreateRequest,TopicResponse,TopicUpdateRequest

router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)
@router.post("",response_model=TopicResponse)
async def create_topic(
    payload: TopicCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    return await service.create_topic(
        db=db,
        title=payload.title
    )


@router.get(
    "",
    response_model=list[TopicResponse]
)
async def get_topics(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_topics(
        db=db
    )

@router.get(
    "/{topic_id}",
    response_model=TopicResponse
)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_topic(
        db=db,
        topic_id=topic_id
    )

@router.patch(
    "/{topic_id}",
    response_model=TopicResponse
)
async def update_topic(
    topic_id: int,
    payload: TopicUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    return await service.update_topic(
        db=db,
        topic_id=topic_id,
        title=payload.title
    )

@router.delete(
    "/{topic_id}"
)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db)
):
    await service.delete_topic(
        db=db,
        topic_id=topic_id
    )

    return {
        "message": "Topic deleted successfully"
    }