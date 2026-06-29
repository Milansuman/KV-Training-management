from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user
from auth.schema import TokenPayload
from db.connection import get_db
from user import service as user_service

from .schema import (
    UserCreate,
    UserUpdate,
    UserResponse
)


router = APIRouter(
    prefix="/user",
    tags=["Users"]
)



@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse
)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):

    user = await user_service.create_user(
        db,
        body
    )

    return user



@router.get(
    "",
    response_model=list[UserResponse]
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):

    users = await user_service.get_all_users(
        db
    )

    return users



@router.get(
    "/{id}",
    response_model=UserResponse
)
async def get_user_by_id(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):

    user = await user_service.get_user_by_id(
        id,
        db
    )

    return user



@router.patch(
    "/{id}",
    response_model=UserResponse
)
async def patch_user(
    id: int,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):

    user = await user_service.patch_user(
        id,
        body,
        db
    )

    return user


@router.delete(
    "/{id}",
    response_model=UserResponse
)
async def delete_user(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(get_current_user),
):

    user = await user_service.delete_user(
        id,
        db
    )

    return user