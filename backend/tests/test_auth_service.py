from jose import jwt

from config import settings
from services.auth_service import create_access_token, hash_password, verify_password


def test_hash_password_does_not_store_plain_text():
    password = "student123"

    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_accepts_correct_password():
    password = "student123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_rejects_incorrect_password():
    password = "student123"
    hashed = hash_password(password)

    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_contains_subject_and_role():
    token = create_access_token({"sub": "student-1", "role": "student"})

    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    assert payload["sub"] == "student-1"
    assert payload["role"] == "student"
    assert "exp" in payload