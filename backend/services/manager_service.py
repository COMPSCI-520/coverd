from datetime import date, datetime, timedelta

from fastapi import HTTPException, status

from models.user import User
from repositories.manager_repository import ManagerRepository
from schemas.manager import (
    RequestListItem,
    RequestShiftInfo,
    RequestsListResponse,
    ReviewResponse,
    StaffScheduleEmployee,
    StaffScheduleResponse,
    StaffScheduleShift,
)


INTERNATIONAL_WEEKLY_LIMIT = 20


def _get_week_bounds(week_start: str | None) -> tuple[str, str]:
    if week_start:
        start = datetime.strptime(week_start, "%Y-%m-%d").date()
    else:
        today = date.today()
        start = today - timedelta(days=today.weekday())

    end = start + timedelta(days=6)
    return start.isoformat(), end.isoformat()


def list_requests(
    repo: ManagerRepository, status_filter: str | None = None
) -> RequestsListResponse:
    docs = repo.get_requests(status_filter)
    items: list[RequestListItem] = []

    for doc in docs:
        shift_doc = doc.get("shift")
        student_doc = doc.get("student")

        shift = None
        if shift_doc is not None:
            shift = RequestShiftInfo(
                id=str(shift_doc["_id"]),
                location=shift_doc["location"],
                shift_date=shift_doc["shift_date"],
                start_time=shift_doc["start_time"],
                end_time=shift_doc["end_time"],
                hours=float(shift_doc["hours"]),
                status=shift_doc["status"],
            )

        student_name = (
            student_doc.get("full_name", "Unknown") if student_doc else "Unknown"
        )

        items.append(
            RequestListItem(
                id=str(doc["_id"]),
                request_type=doc["request_type"],
                status=doc["status"],
                created_at=doc.get("created_at"),
                student_name=student_name,
                student_id=doc.get("requested_by", ""),
                shift=shift,
                reviewed_by=doc.get("reviewed_by"),
                reviewed_at=doc.get("reviewed_at"),
            )
        )

    return RequestsListResponse(requests=items, total=len(items))


def review_request(
    request_id: str,
    action: str,
    current_user: User,
    repo: ManagerRepository,
) -> ReviewResponse:
    req = repo.get_request_by_id(request_id)

    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if req["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request has already been {req['status']}",
        )

    if action == "approve":
        success = repo.approve_drop_request(request_id, current_user.id)
    elif action == "deny":
        success = repo.deny_request(request_id, current_user.id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request",
        )

    verb = "approved" if action == "approve" else "denied"
    return ReviewResponse(message=f"Request {verb} successfully", request_id=request_id)


def get_staff_schedule(
    repo: ManagerRepository,
    week_start: str | None = None,
    location: str | None = None,
    student: str | None = None,
) -> StaffScheduleResponse:
    start, end = _get_week_bounds(week_start)

    students = repo.get_student_users(student_search=student)
    shifts = repo.get_staff_shifts(start, end, location=location)

    shift_ids = [str(shift["_id"]) for shift in shifts]
    pending_requests = repo.get_pending_drop_requests_for_shifts(shift_ids)
    pending_shift_ids = {request["shift_id"] for request in pending_requests}

    shifts_by_student: dict[str, list[dict]] = {}
    for shift in shifts:
        student_id = shift.get("student_id")
        if student_id:
            shifts_by_student.setdefault(student_id, []).append(shift)

    staff_items: list[StaffScheduleEmployee] = []

    for student_doc in students:
        student_id = str(student_doc["_id"])
        student_shifts = shifts_by_student.get(student_id, [])

        # If a location filter is active, do not show students with no matching shifts.
        if location and location != "All locations" and not student_shifts:
            continue

        shift_items: list[StaffScheduleShift] = []
        pending_drop_count = 0

        for shift in student_shifts:
            shift_id = str(shift["_id"])
            has_pending_drop = shift_id in pending_shift_ids

            if has_pending_drop:
                pending_drop_count += 1

            shift_items.append(
                StaffScheduleShift(
                    id=shift_id,
                    location=shift["location"],
                    shift_date=shift["shift_date"],
                    start_time=shift["start_time"],
                    end_time=shift["end_time"],
                    hours=float(shift["hours"]),
                    status=shift["status"],
                    has_pending_drop=has_pending_drop,
                )
            )

        hours_this_week = round(sum(shift.hours for shift in shift_items), 2)
        is_international = bool(student_doc.get("is_international", False))
        weekly_limit = INTERNATIONAL_WEEKLY_LIMIT if is_international else None
        remaining_hours = (
            round(max(INTERNATIONAL_WEEKLY_LIMIT - hours_this_week, 0), 2)
            if is_international
            else None
        )

        staff_items.append(
            StaffScheduleEmployee(
                student_id=student_id,
                full_name=student_doc.get("full_name", "Unknown Student"),
                email=student_doc.get("email", ""),
                is_international=is_international,
                hours_this_week=hours_this_week,
                weekly_limit=weekly_limit,
                remaining_hours=remaining_hours,
                shift_count=len(shift_items),
                pending_drop_count=pending_drop_count,
                shifts=shift_items,
            )
        )

    scheduled_shifts = sum(item.shift_count for item in staff_items)
    scheduled_hours = round(sum(item.hours_this_week for item in staff_items), 2)
    pending_drops = sum(item.pending_drop_count for item in staff_items)

    return StaffScheduleResponse(
        week_start=start,
        week_end=end,
        total_staff=len(staff_items),
        scheduled_shifts=scheduled_shifts,
        scheduled_hours=scheduled_hours,
        pending_drops=pending_drops,
        staff=staff_items,
    )