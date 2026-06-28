from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
from typing import Any

import jwt

from config import env

JWT_ALGORITHM = "HS256"
JWT_SECRET = env.JWT_SECRET
ACCESS_TOKEN_EXPIRES_MINUTES = 15
REFRESH_TOKEN_EXPIRES_MINUTES = 7 * 24 * 60

def hash_password(password: str) -> str:
    hash = pbkdf2_hmac(
        password=password.encode("utf-8"),
        salt=env.SALT.encode("utf-8"),
        hash_name="sha256",
        iterations=500_000
    )
    return hash.hex()

def verify_password(password: str, stored_password: str) -> bool:
    hash = pbkdf2_hmac(
        password=password.encode("utf-8"),
        salt=env.SALT.encode("utf-8"),
        hash_name="sha256",
        iterations=500_000
    )

    return hash.hex() == stored_password


def create_access_token(
    subject: str,
    extra_claims: dict[str, Any] | None = None
) -> str:
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES),
    }

    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(subject: str, access_token: str) -> str:
    now = datetime.now(tz=UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "refresh",
        "access_token": access_token,
        "iat": now,
        "exp": now + timedelta(minutes=REFRESH_TOKEN_EXPIRES_MINUTES),
    }

    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str, verify_exp: bool = True) -> dict[str, Any]:
    return jwt.decode(
        token,
        JWT_SECRET,
        algorithms=[JWT_ALGORITHM],
        options={"verify_exp": verify_exp},
    )


def create_token_pair(
    subject: str,
    extra_claims: dict[str, Any] | None = None
) -> dict[str, str]:
    access_token = create_access_token(subject=subject, extra_claims=extra_claims)
    refresh_token = create_refresh_token(subject=subject, access_token=access_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }
