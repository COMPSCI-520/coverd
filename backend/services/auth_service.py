from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import jwt
from passlib.context import CryptContext
from pymongo.database import Database

from config import settings
from models.user import User
from repositories.user_repository import UserRepository

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def create_access_token(data: dict) -> str:
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def authenticate(email: str, password: str, db: Database) -> User:
    user = UserRepository(db).find_by_email(email)

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
