from pydantic import BaseModel


class DashboardNextShift(BaseModel):
    shift_date: str
    start_time: str
    end_time: str
    location: str
    hours: float


class DashboardShiftItem(BaseModel):
    shift_date: str
    day: str
    location: str
    start_time: str
    end_time: str
    hours: float
    status: str


class StudentDashboardResponse(BaseModel):
    full_name: str
    is_international: bool

    hours_this_week: float
    weekly_limit: int | None
    remaining_hours: float | None

    show_warning: bool
    warning_message: str | None

    upcoming_shifts_count: int
    next_shift: DashboardNextShift | None

    pending_requests_count: int
    marketplace_available_count: int

    weekly_shifts: list[DashboardShiftItem]