from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schema import TokenPayload
from db.connection import get_db
from auth.dependencies import get_current_user

from exceptions.exceptions import UnauthorizedException
from sessions import service
from sessions.schemas import SessionCreateRequest, SessionResponse, SessionUpdateRequest


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)

@router.post(
    "",
    response_model=SessionResponse
)
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    return await service.create_session(
        db=db,
        title=payload.title,
        description=payload.description,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime,
        program_id=payload.program_id
    )

@router.get(
    "",
    response_model=list[SessionResponse]
)
async def get_sessions(
    db: AsyncSession = Depends(get_db)
):
    return await service.get_sessions(
        db=db
    )


#get session by session id that is not deleted
@router.get(
    "/{session_id}",
    response_model=SessionResponse
)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await service.get_session(
        db=db,
        session_id=session_id
    )

#get session by program id that is not deleted
@router.get("/program/{program_id}",
    response_model=list[SessionResponse]
)
async def get_sessions_by_program_id(program_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_sessions_by_program_id(
        db=db,
        program_id=program_id
    )


#update session by session id that is not deleted
@router.put(
    "/{session_id}",
    response_model=SessionResponse
)
async def update_session(
    session_id: int,
    payload: SessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)

):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    return await service.update_session(
        db=db,
        session_id=session_id,
        title=payload.title,
        description=payload.description,
        start_datetime=payload.start_datetime,
        end_datetime=payload.end_datetime
    )

@router.delete(
    "/{session_id}"
)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise UnauthorizedException("Action not allowed")

    await service.delete_session(
        db=db,
        session_id=session_id
    )

    return {
        "message": "Session deleted successfully"
    }
