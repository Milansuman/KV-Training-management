from uuid import uuid4

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
            extra_claims={
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "is_admin": user.is_admin,
                "nonce": uuid4().hex
            }
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
            extra_claims={
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "is_admin": user.is_admin,
                "nonce": uuid4().hex
            }
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
