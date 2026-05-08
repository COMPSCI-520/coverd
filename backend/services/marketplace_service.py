from fastapi import HTTPException, status

from models.user import User
from repositories.marketplace_repository import MarketplaceRepository
from schemas.shift import ClaimResponse, DropResponse, MarketplaceListResponse, ShiftResponse

INTERNATIONAL_WEEKLY_LIMIT = 20.0


def _display_name(full_name: str | None) -> str:
    if not full_name:
        return "Student"

    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0]

    return f"{parts[0]} {parts[-1][0]}."


def list_available_shifts(
    current_user: User,
    repo: MarketplaceRepository,
) -> MarketplaceListResponse:
    docs = repo.get_marketplace_shifts()

    hours_this_week = 0.0
    weekly_limit = INTERNATIONAL_WEEKLY_LIMIT if current_user.is_international else None
    remaining_capacity = None

    if docs:
        # Use the first marketplace shift week for the capacity message.
        # The backend still checks the exact target shift week during claim.
        hours_this_week = repo.get_student_hours_for_shift_week(
            current_user.id,
            docs[0]["shift_date"],
        )

    if current_user.is_international:
        remaining_capacity = round(max(INTERNATIONAL_WEEKLY_LIMIT - hours_this_week, 0), 2)

    shifts: list[ShiftResponse] = []

    for doc in docs:
        shift_hours = float(doc["hours"])
        existing_hours_for_that_week = repo.get_student_hours_for_shift_week(
            current_user.id,
            doc["shift_date"],
        )
        projected = round(existing_hours_for_that_week + shift_hours, 2)

        would_exceed = bool(
            current_user.is_international and projected > INTERNATIONAL_WEEKLY_LIMIT
        )

        can_claim = doc["status"] == "available" and not would_exceed
        claim_block_reason = None

        if doc["status"] != "available":
            claim_block_reason = "This shift is pending manager approval."
        elif would_exceed:
            claim_block_reason = (
                f"{doc['location']} shift ({shift_hours:g} hrs) would bring your weekly "
                f"total to {projected:g} hrs, exceeding the 20-hr limit for "
                f"international students."
            )

        shifts.append(
            ShiftResponse(
                id=str(doc["_id"]),
                location=doc["location"],
                shift_date=doc["shift_date"],
                start_time=doc["start_time"],
                end_time=doc["end_time"],
                hours=shift_hours,
                status=doc["status"],
                posted_by=_display_name(doc.get("posted_by_name")),
                can_claim=can_claim,
                claim_block_reason=claim_block_reason,
                projected_weekly_hours=projected,
                would_exceed_limit=would_exceed,
            )
        )

    return MarketplaceListResponse(
        shifts=shifts,
        total=len(shifts),
        hours_this_week=hours_this_week,
        weekly_limit=weekly_limit,
        remaining_capacity=remaining_capacity,
    )


def claim_shift(
    shift_id: str,
    current_user: User,
    repo: MarketplaceRepository,
) -> ClaimResponse:
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can claim marketplace shifts",
        )

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
            current_user.id,
            shift["shift_date"],
        )
        new_total = existing_hours + float(shift["hours"])

        if new_total > INTERNATIONAL_WEEKLY_LIMIT:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Claiming this shift would bring your total to {new_total:.1f} hrs "
                    f"for that week, exceeding the {INTERNATIONAL_WEEKLY_LIMIT:.0f}-hr "
                    f"limit for international students."
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
    shift_id: str,
    current_user: User,
    repo: MarketplaceRepository,
) -> DropResponse:
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can request to drop shifts",
        )

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