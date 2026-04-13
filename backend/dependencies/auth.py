# Decodes the JWT from the Authorization header and returns the current user.
from fastapi import Header, HTTPException, status

def get_current_user(authorization: str | None = Header(default=None)):
    """
    Temporary placeholder auth dependency.

    Later this will:
    - read JWT from Authorization header
    - decode token
    - fetch user from database

    For now it only checks that the header exists.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )

    return {
        "user_id": "temp-user-id",
        "role": "student",
        "email": "temp@example.com",
    }