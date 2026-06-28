import asyncio
from typing import Any, Mapping
from uuid import uuid4
from config import env

from google.auth.exceptions import GoogleAuthError
from google.auth.transport.requests import Request
from google.oauth2 import id_token as google_id_token
from jwt import ExpiredSignatureError, InvalidTokenError
from sqlalchemy.exc import IntegrityError, NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth import repository, utils
from exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from models.user import User


def _build_token_claims(user: User) -> dict[str, Any]:
    return {
        "username": user.username,
        "email": user.email,
        "display_name": user.display_name,
        "is_admin": user.is_admin,
        "nonce": uuid4().hex
    }


def _verify_google_token(id_token: str) -> dict[str, Any]:
    return dict(google_id_token.verify_oauth2_token(
        id_token,
        Request(),
        env.GOOGLE_CLIENT_ID
    ))


async def verify_google_id_token(id_token: str) -> dict[str, Any]:
    try:
        payload = await asyncio.to_thread(_verify_google_token, id_token)
    except ValueError as exc:
        raise UnauthorizedException("Invalid Google token") from exc
    except GoogleAuthError as exc:
        raise UnauthorizedException("Unable to verify Google token") from exc

    return payload


async def register_user(
    db: AsyncSession,
    username: str,
    email: str,
    display_name: str,
    password: str
) -> User:
    try:
        is_first_user = (await repository.get_user_count(db=db)) == 0

        return await repository.create_user(
            db=db,
            username=username,
            email=email,
            display_name=display_name,
            password=utils.hash_password(password),
            is_admin=is_first_user
        )
    except IntegrityError as exc:
        await db.rollback()
        raise ConflictException("User already exists") from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to register user") from exc


async def login(
    db: AsyncSession,
    username_or_email: str,
    password: str
) -> dict[str, str]:
    try:
        user = await repository.get_user_by_credentials(
            db=db,
            username_or_email=username_or_email,
            password=utils.hash_password(password)
        )

        return utils.create_token_pair(
            subject=str(user.id),
            extra_claims=_build_token_claims(user)
        )
    except NoResultFound as exc:
        raise UnauthorizedException("Invalid username/email or password") from exc
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to login") from exc


async def refresh(
    db: AsyncSession,
    refresh_token: str
) -> dict[str, str]:
    try:
        refresh_payload = utils.decode_token(refresh_token)

        if refresh_payload.get("type") != "refresh":
            raise UnauthorizedException("Invalid refresh token")

        access_token = refresh_payload.get("access_token")
        user_id = refresh_payload.get("sub")

        if not isinstance(access_token, str) or not isinstance(user_id, str):
            raise UnauthorizedException("Invalid refresh token")

        access_payload = utils.decode_token(access_token, verify_exp=False)
        if str(access_payload.get("sub")) != user_id:
            raise UnauthorizedException("Refresh token does not match access token")

        user = await repository.get_user_by_id(db=db, user_id=int(user_id))

        return utils.create_token_pair(
            subject=str(user.id),
            extra_claims=_build_token_claims(user)
        )
    except ExpiredSignatureError as exc:
        raise UnauthorizedException("Refresh token expired") from exc
    except InvalidTokenError as exc:
        raise UnauthorizedException("Invalid refresh token") from exc
    except ValueError as exc:
        raise UnauthorizedException("Invalid refresh token") from exc
    except NoResultFound as exc:
        raise NotFoundException("User not found") from exc
    except SQLAlchemyError as exc:
        raise BadRequestException("Unable to refresh token") from exc


async def google_auth(
    db: AsyncSession,
    id_token: str
) -> dict[str, str]:
    payload = await verify_google_id_token(id_token=id_token)
    email = payload.get("email")
    display_name = payload.get("name")
    google_sub = payload.get("sub")
    email_verified = payload.get("email_verified")

    if not isinstance(email, str) or not isinstance(google_sub, str):
        raise UnauthorizedException("Invalid Google token")

    if email_verified not in (True, "true", "True"):
        raise UnauthorizedException("Google email is not verified")

    if not isinstance(display_name, str) or len(display_name.strip()) == 0:
        display_name = email.split("@", maxsplit=1)[0]

    try:
        user = await repository.get_user_by_google_sub(db=db, google_sub=google_sub)
    except NoResultFound:
        try:
            user = await repository.get_user_by_email(db=db, email=email)
            if user.google_sub is None:
                user = await repository.link_google_sub(db=db, user=user, google_sub=google_sub)
        except NoResultFound:
            try:
                is_first_user = (await repository.get_user_count(db=db)) == 0
                user = await repository.create_user(
                    db=db,
                    username=email.split("@", maxsplit=1)[0],
                    email=email,
                    display_name=display_name,
                    password=None,
                    google_sub=google_sub,
                    is_admin=is_first_user
                )
            except IntegrityError as exc:
                await db.rollback()
                raise ConflictException("Unable to create Google user") from exc
            except SQLAlchemyError as exc:
                await db.rollback()
                raise BadRequestException("Unable to create Google user") from exc
    except SQLAlchemyError as exc:
        await db.rollback()
        raise BadRequestException("Unable to login with Google") from exc

    return utils.create_token_pair(
        subject=str(user.id),
        extra_claims=_build_token_claims(user)
    )
