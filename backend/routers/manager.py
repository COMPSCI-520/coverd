from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.user import User
from repositories.manager_repository import ManagerRepository
from schemas.manager import RequestsListResponse, ReviewResponse, StaffScheduleResponse
from services.manager_service import get_staff_schedule, list_requests, review_request

router = APIRouter(prefix="/manager", tags=["Manager"])


def require_manager(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager access required",
        )
    return current_user


@router.get("/requests", response_model=RequestsListResponse)
def get_all_requests(
    status: Optional[str] = None,
    current_user: User = Depends(require_manager),
    db: Database = Depends(get_db),
):
    repo = ManagerRepository(db)
    return list_requests(repo, status_filter=status)


@router.get("/staff-schedule", response_model=StaffScheduleResponse)
def read_staff_schedule(
    week_start: Optional[str] = Query(default=None),
    location: Optional[str] = Query(default=None),
    student: Optional[str] = Query(default=None),
    current_user: User = Depends(require_manager),
    db: Database = Depends(get_db),
):
    repo = ManagerRepository(db)
    return get_staff_schedule(
        repo,
        week_start=week_start,
        location=location,
        student=student,
    )


@router.post("/requests/{request_id}/approve", response_model=ReviewResponse)
def approve_request(
    request_id: str,
    current_user: User = Depends(require_manager),
    db: Database = Depends(get_db),
):
    repo = ManagerRepository(db)
    return review_request(request_id, "approve", current_user, repo)


@router.post("/requests/{request_id}/deny", response_model=ReviewResponse)
def deny_request(
    request_id: str,
    current_user: User = Depends(require_manager),
    db: Database = Depends(get_db),
):
    repo = ManagerRepository(db)
    return review_request(request_id, "deny", current_user, repo)