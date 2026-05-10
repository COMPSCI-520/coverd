from pydantic import BaseModel


class StudentRequestShiftInfo(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float


class StudentRequestItem(BaseModel):
    id: str
    request_type: str
    status: str
    created_at: str | None
    shift: StudentRequestShiftInfo | None
    reviewed_at: str | None


class StudentRequestsResponse(BaseModel):
    requests: list[StudentRequestItem]
    total: int


class DashboardNextShift(BaseModel):
    id: str
    shift_date: str
    start_time: str
    end_time: str
    location: str
    hours: float


class DashboardShiftItem(BaseModel):
    id: str
    shift_date: str
    day: str
    location: str
    start_time: str
    end_time: str
    hours: float
    status: str

class MyScheduleResponse(BaseModel):
    month: int
    year: int
    shifts: list[DashboardShiftItem]


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