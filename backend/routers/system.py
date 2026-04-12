from fastapi import APIRouter

router = APIRouter(prefix="/system", tags=["System"])


@router.get("/ping")
def ping():
    return {"message": "pong"}