from fastapi import APIRouter, Depends
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.user import User
from repositories.marketplace_repository import MarketplaceRepository
from schemas.shift import ClaimResponse, DropResponse, MarketplaceListResponse
from services.marketplace_service import claim_shift, list_available_shifts, request_drop

router = APIRouter(prefix="/marketplace", tags=["Marketplace"])


@router.get("/shifts", response_model=MarketplaceListResponse)
def get_marketplace_shifts(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    repo = MarketplaceRepository(db)
    return list_available_shifts(repo)


@router.post("/shifts/{shift_id}/claim", response_model=ClaimResponse)
def claim_marketplace_shift(
    shift_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    repo = MarketplaceRepository(db)
    return claim_shift(shift_id, current_user, repo)


@router.post("/shifts/{shift_id}/drop", response_model=DropResponse)
def drop_shift(
    shift_id: str,
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    repo = MarketplaceRepository(db)
    return request_drop(shift_id, current_user, repo)
