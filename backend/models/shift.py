from pydantic import BaseModel


class Shift(BaseModel):
    id: str
    student_id: str | None = None
    location: str
    shift_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    hours: float
    status: str  # assigned | available

    @classmethod
    def from_mongo(cls, doc: dict) -> "Shift":
        return cls(id=str(doc["_id"]), **{k: v for k, v in doc.items() if k != "_id"})