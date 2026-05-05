from fastapi import HTTPException, status

from models.user import User
from repositories.marketplace_repository import MarketplaceRepository
from schemas.shift import ClaimResponse, DropResponse, MarketplaceListResponse, ShiftResponse

INTERNATIONAL_WEEKLY_LIMIT = 20.0


def list_available_shifts(repo: MarketplaceRepository) -> MarketplaceListResponse:
    docs = repo.get_available_shifts()
    shifts = [
        ShiftResponse(
            id=str(doc["_id"]),
            location=doc["location"],
            shift_date=doc["shift_date"],
            start_time=doc["start_time"],
            end_time=doc["end_time"],
            hours=float(doc["hours"]),
            status=doc["status"],
        )
        for doc in docs
    ]
    return MarketplaceListResponse(shifts=shifts, total=len(shifts))


def claim_shift(
    shift_id: str, current_user: User, repo: MarketplaceRepository
) -> ClaimResponse:
    shift = repo.get_shift_by_id(shift_id)

    if shift is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")

    if shift["status"] != "available":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift is no longer available",
        )

    if current_user.is_international:
        existing_hours = repo.get_student_hours_for_shift_week(
            current_user.id, shift["shift_date"]
        )
        new_total = existing_hours + float(shift["hours"])
        if new_total > INTERNATIONAL_WEEKLY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Claiming this shift would bring your total to {new_total:.1f} hrs "
                    f"for that week, exceeding the {INTERNATIONAL_WEEKLY_LIMIT:.0f}-hr limit "
                    f"for international students."
                ),
            )

    claimed = repo.claim_shift(shift_id, current_user.id)
    if not claimed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Shift was claimed by someone else just now. Please refresh.",
        )

    return ClaimResponse(message="Shift claimed successfully", shift_id=shift_id)


def request_drop(
    shift_id: str, current_user: User, repo: MarketplaceRepository
) -> DropResponse:
    shift = repo.get_shift_by_id(shift_id)

    if shift is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shift not found")

    if shift.get("student_id") != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only request to drop your own shifts",
        )

    if shift["status"] != "assigned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only assigned shifts can be dropped",
        )

    if repo.has_pending_drop_request(shift_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A drop request for this shift is already pending",
        )

    request_id = repo.create_drop_request(shift_id, current_user.id)
    return DropResponse(
        message="Drop request submitted for manager review",
        shift_id=shift_id,
        request_id=request_id,
    )
