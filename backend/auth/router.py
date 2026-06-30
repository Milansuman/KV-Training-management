from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from fastapi.responses import RedirectResponse

from auth import google_auth as google_auth_service
from auth import google_handshake as google_handshake_service
from auth import login as login_service
from auth import refresh as refresh_service
from auth import register_user
from auth.utils import ACCESS_TOKEN_EXPIRES_MINUTES, REFRESH_TOKEN_EXPIRES_MINUTES
from auth.schema import GoogleHandshakeRequest, LoginRequest, RegisterRequest, TokenResponse, UserResponse
from config import env
from exceptions import UnauthorizedException
from db.connection import get_db

from authlib.integrations.starlette_client import OAuth

# Configure OAuth client for Google
oauth = OAuth()
oauth.register(
    name="google",
    client_id=env.GOOGLE_CLIENT_ID,
    client_secret=env.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)

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


@router.get("/google/login")
async def google_login(request: Request):
    """Start the OAuth redirect flow to Google's authorization endpoint."""
    # Build callback URL for this application
    redirect_uri = str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle the OAuth callback from Google, generate a one-time nonce for the
    user, and redirect the browser to the frontend verification page with that
    nonce as a query parameter.  The frontend then POSTs the nonce to
    /auth/google/handshake to receive the real auth cookies."""
    token = await oauth.google.authorize_access_token(request)

    id_token = token.get("id_token")

    nonce = await google_auth_service(db=db, id_token=id_token)

    redirect_to = f"{env.FRONTEND_URL}/verify/google?nonce={nonce}"
    return RedirectResponse(url=redirect_to)


@router.post("/google/handshake", response_model=TokenResponse)
async def google_handshake(
    payload: GoogleHandshakeRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Complete the Google OAuth handshake.  The frontend submits the one-time
    nonce it received via the redirect URL.  If valid, auth cookies are set and
    the token pair is returned; the nonce is immediately invalidated."""
    tokens = await google_handshake_service(db=db, nonce=payload.nonce)
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
