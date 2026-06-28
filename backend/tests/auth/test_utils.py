from datetime import UTC, datetime, timedelta

from auth import utils


def test_hash_password_is_deterministic() -> None:
    assert utils.hash_password("secret") == utils.hash_password("secret")


def test_verify_password_matches_hashed_password() -> None:
    hashed_password = utils.hash_password("secret")

    assert utils.verify_password("secret", hashed_password) is True
    assert utils.verify_password("wrong", hashed_password) is False


def test_create_token_pair_and_decode_refresh_token() -> None:
    tokens = utils.create_token_pair(
        subject="123",
        extra_claims={"username": "milan", "email": "milan@example.com"},
    )

    access_payload = utils.decode_token(tokens["access_token"])
    refresh_payload = utils.decode_token(tokens["refresh_token"])

    assert access_payload["sub"] == "123"
    assert access_payload["type"] == "access"
    assert access_payload["username"] == "milan"
    assert access_payload["email"] == "milan@example.com"

    assert refresh_payload["sub"] == "123"
    assert refresh_payload["type"] == "refresh"
    assert refresh_payload["access_token"] == tokens["access_token"]


def test_decode_token_can_ignore_expiration() -> None:
    expired_token = utils.jwt.encode(
        {
            "sub": "123",
            "type": "access",
            "iat": datetime.now(tz=UTC) - timedelta(days=2),
            "exp": datetime.now(tz=UTC) - timedelta(days=1),
        },
        utils.JWT_SECRET,
        algorithm=utils.JWT_ALGORITHM,
    )

    payload = utils.decode_token(expired_token, verify_exp=False)

    assert payload["sub"] == "123"
