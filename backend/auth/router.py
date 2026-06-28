from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from auth import google_auth as google_auth_service
from auth import login as login_service
from auth import refresh as refresh_service
from auth import register_user
from auth.utils import ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_MINUTES
from auth.schema import GoogleAuthRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from config import env
from exceptions import UnauthorizedException
from db.connection import get_db

router = APIRouter(prefix="/auth", tags=["auth"])

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
COOKIE_PATH = "/"
ACCESS_MAX_AGE = ACCESS_TOKEN_EXPIRES_MINUTES * 60
REFRESH_MAX_AGE = REFRESH_TOKEN_EXPIRES_MINUTES * 60


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = env.ENV != "dev"
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        max_age=ACCESS_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path=COOKIE_PATH,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="lax",
        path=COOKIE_PATH,
    )


@router.post("/register", response_model=UserResponse)
async def register(
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await register_user(
        db=db,
        username=payload.username,
        email=payload.email,
        display_name=payload.display_name,
        password=payload.password,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    tokens = await login_service(
        db=db,
        username_or_email=payload.username_or_email,
        password=payload.password,
    )
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return tokens


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    payload: GoogleAuthRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    tokens = await google_auth_service(db=db, id_token=payload.id_token)
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
):
    if refresh_token is None:
        raise UnauthorizedException("Refresh token cookie is required")

    tokens = await refresh_service(db=db, refresh_token=refresh_token)
    _set_auth_cookies(response, tokens["access_token"], tokens["refresh_token"])
    return tokens
