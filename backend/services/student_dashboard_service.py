from datetime import date, datetime, timedelta
import calendar

from models.user import User
from repositories.student_dashboard_repository import StudentDashboardRepository
from schemas.dashboard import (
    DashboardNextShift,
    DashboardShiftItem,
    StudentDashboardResponse,
    StudentRequestItem,
    StudentRequestShiftInfo,
    StudentRequestsResponse,
    MyScheduleResponse,
)


def _get_week_bounds(today: date) -> tuple[date, date]:
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def _format_day_name(date_str: str) -> str:
    parsed = datetime.strptime(date_str, "%Y-%m-%d").date()
    return parsed.strftime("%a %b %d")


def get_student_dashboard(
    current_user: User,
    repo: StudentDashboardRepository,
) -> StudentDashboardResponse:
    today = date.today()
    today_str = today.isoformat()

    week_start, week_end = _get_week_bounds(today)
    week_start_str = week_start.isoformat()
    week_end_str = week_end.isoformat()

    weekly_shift_docs = repo.get_student_weekly_shifts(
        current_user.id,
        week_start_str,
        week_end_str,
    )

    upcoming_shift_docs = repo.get_upcoming_student_shifts(current_user.id, today_str)
    pending_requests_count = repo.count_pending_requests(current_user.id)

    marketplace_available_count = repo.count_marketplace_available_this_week(
        week_start_str,
        week_end_str,
    )

    hours_this_week = round(sum(float(shift["hours"]) for shift in weekly_shift_docs), 2)

    weekly_limit = 20 if current_user.is_international else None
    remaining_hours = (
        round(max(weekly_limit - hours_this_week, 0), 2)
        if weekly_limit is not None
        else None
    )

    show_warning = current_user.is_international
    warning_message = (
        f"You have used {hours_this_week} of your {weekly_limit} weekly allowed hours."
        if show_warning
        else None
    )

    weekly_shifts = [
        DashboardShiftItem(
            id=str(shift["_id"]),
            shift_date=shift["shift_date"],
            day=_format_day_name(shift["shift_date"]),
            location=shift["location"],
            start_time=shift["start_time"],
            end_time=shift["end_time"],
            hours=float(shift["hours"]),
            status=shift["status"],
        )
        for shift in weekly_shift_docs
    ]

    next_shift = None
    if upcoming_shift_docs:
        first_shift = upcoming_shift_docs[0]
        next_shift = DashboardNextShift(
            id=str(first_shift["_id"]),
            shift_date=first_shift["shift_date"],
            start_time=first_shift["start_time"],
            end_time=first_shift["end_time"],
            location=first_shift["location"],
            hours=float(first_shift["hours"]),
        )

    return StudentDashboardResponse(
        full_name=current_user.full_name,
        is_international=current_user.is_international,
        hours_this_week=hours_this_week,
        weekly_limit=weekly_limit,
        remaining_hours=remaining_hours,
        show_warning=show_warning,
        warning_message=warning_message,
        upcoming_shifts_count=len(upcoming_shift_docs),
        next_shift=next_shift,
        pending_requests_count=pending_requests_count,
        marketplace_available_count=marketplace_available_count,
        weekly_shifts=weekly_shifts,
    )


def get_student_requests(
    current_user: User,
    repo: StudentDashboardRepository,
) -> StudentRequestsResponse:
    docs = repo.get_student_requests(current_user.id)
    items: list[StudentRequestItem] = []

    for doc in docs:
        shift_doc = doc.get("shift")
        shift = None

        if shift_doc is not None:
            shift = StudentRequestShiftInfo(
                id=str(shift_doc["_id"]),
                location=shift_doc["location"],
                shift_date=shift_doc["shift_date"],
                start_time=shift_doc["start_time"],
                end_time=shift_doc["end_time"],
                hours=float(shift_doc["hours"]),
            )

        items.append(
            StudentRequestItem(
                id=str(doc["_id"]),
                request_type=doc["request_type"],
                status=doc["status"],
                created_at=doc.get("created_at"),
                shift=shift,
                reviewed_at=doc.get("reviewed_at"),
            )
        )

    return StudentRequestsResponse(requests=items, total=len(items))

def get_student_month_schedule(
    current_user: User,
    repo: StudentDashboardRepository,
    month: int,
    year: int,
) -> MyScheduleResponse:

    first_day = date(year, month, 1)

    last_day = date(
        year,
        month,
        calendar.monthrange(year, month)[1],
    )

    docs = repo.get_student_month_shifts(
        current_user.id,
        first_day.isoformat(),
        last_day.isoformat(),
    )

    shifts = [
        DashboardShiftItem(
            id=str(shift["_id"]),
            shift_date=shift["shift_date"],
            day=_format_day_name(shift["shift_date"]),
            location=shift["location"],
            start_time=shift["start_time"],
            end_time=shift["end_time"],
            hours=float(shift["hours"]),
            status=shift["status"],
        )
        for shift in docs
    ]

    return MyScheduleResponse(
        month=month,
        year=year,
        shifts=shifts,
    )