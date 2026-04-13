from pydantic import BaseModel


class ShiftRequest(BaseModel):
    id: str
    shift_id: str
    request_type: str  # drop | claim
    requested_by: str
    status: str  # pending | approved | rejected
    created_at: str | None = None
    reviewed_by: str | None = None
    reviewed_at: str | None = None

    @classmethod
    def from_mongo(cls, doc: dict) -> "ShiftRequest":
        return cls(id=str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"})