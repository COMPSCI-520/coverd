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
