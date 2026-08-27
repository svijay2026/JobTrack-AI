import pytest
from datetime import timedelta
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)


def test_password_hashing_and_verification():
    """Verify that bcrypt hashes passwords securely with salt and verifies correctly."""
    plain_password = "my_secure_password_123"
    hashed = get_password_hash(plain_password)

    # Hash should not equal plain password
    assert hashed != plain_password
    # Hash should start with bcrypt identifier
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    # Correct password should verify to True
    assert verify_password(plain_password, hashed) is True

    # Incorrect password should verify to False
    assert verify_password("wrong_password", hashed) is False


def test_jwt_token_creation_and_decoding():
    """Verify that JWT access tokens are created, signed, and decoded with valid claims."""
    user_id = 42
    token = create_access_token(subject=user_id)
    assert isinstance(token, str)

    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    assert "iat" in payload


def test_jwt_token_expiration():
    """Verify that an expired JWT token returns None when decoded."""
    user_id = 99
    # Create token that expired 5 minutes ago
    expired_token = create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=-5),
    )

    payload = decode_access_token(expired_token)
    assert payload is None


def test_invalid_jwt_token():
    """Verify that a malformed or tampered token returns None."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature"
    payload = decode_access_token(invalid_token)
    assert payload is None
