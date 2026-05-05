from pydantic import BaseModel


class ShiftResponse(BaseModel):
    id: str
    location: str
    shift_date: str
    start_time: str
    end_time: str
    hours: float
    status: str


class MarketplaceListResponse(BaseModel):
    shifts: list[ShiftResponse]
    total: int


class ClaimResponse(BaseModel):
    message: str
    shift_id: str


class DropResponse(BaseModel):
    message: str
    shift_id: str
    request_id: str
