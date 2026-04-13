from fastapi import APIRouter, Depends
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.user import User
from schemas.user import LoginRequest, TokenResponse, UserResponse
from services.auth_service import authenticate, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Database = Depends(get_db)):
    user = authenticate(body.email, body.password, db)
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(
        access_token=token,
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        full_name=current_user.full_name,
    )
