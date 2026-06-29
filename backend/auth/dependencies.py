from fastapi import Cookie
from exceptions import UnauthorizedException
from auth.schema import TokenPayload
from auth.utils import decode_token

def get_current_user(
    access_token: str | None = Cookie(default=None),
) -> TokenPayload:

    if access_token is None:
        raise UnauthorizedException(
            "Access token missing"
        )

    try:
        payload = decode_token(access_token)

        if payload.get("type") != "access":
            raise UnauthorizedException(
                "Invalid token type"
            )

        return TokenPayload(**payload)

    except Exception as exc:
        raise UnauthorizedException(
            "Invalid or expired token"
        ) from exc