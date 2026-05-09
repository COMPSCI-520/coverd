from pydantic import BaseModel


class RequestShiftInfo(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float
    status: str


class RequestListItem(BaseModel):
    id: str
    request_type: str
    status: str
    created_at: str | None
    student_name: str
    student_id: str
    shift: RequestShiftInfo | None
    reviewed_by: str | None = None
    reviewed_at: str | None = None


class RequestsListResponse(BaseModel):
    requests: list[RequestListItem]
    total: int


class ReviewResponse(BaseModel):
    message: str
    request_id: str


class StaffScheduleShift(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float
    status: str
    has_pending_drop: bool = False

class StaffCoverageShift(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float

class StaffScheduleEmployee(BaseModel):
    student_id: str
    full_name: str
    email: str
    is_international: bool
    hours_this_week: float
    weekly_limit: int | None = None
    remaining_hours: float | None = None
    shift_count: int
    pending_drop_count: int
    shifts: list[StaffScheduleShift]


class StaffScheduleResponse(BaseModel):
    week_start: str
    week_end: str
    total_staff: int
    scheduled_shifts: int
    scheduled_hours: float
    pending_drops: int
    coverage_needed_count: int
    shifts_needing_coverage: list[StaffCoverageShift]
    staff: list[StaffScheduleEmployee]