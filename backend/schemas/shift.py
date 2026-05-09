from pydantic import BaseModel


class ShiftResponse(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float
    status: str
    posted_by: str | None = None
    can_claim: bool = True
    claim_block_reason: str | None = None
    projected_weekly_hours: float | None = None
    would_exceed_limit: bool = False


class MarketplaceListResponse(BaseModel):
    shifts: list[ShiftResponse]
    total: int
    hours_this_week: float
    weekly_limit: float | None = None
    remaining_capacity: float | None = None


class ClaimResponse(BaseModel):
    message: str
    shift_id: str


class DropResponse(BaseModel):
    message: str
    shift_id: str
    request_id: str