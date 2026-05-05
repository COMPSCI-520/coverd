from datetime import date, timedelta

from bson import ObjectId
from pymongo.database import Database


class MarketplaceRepository:
    def __init__(self, db: Database):
        self._shifts = db["shifts"]
        self._requests = db["shift_requests"]

    def get_available_shifts(self) -> list[dict]:
        return list(
            self._shifts.find({"status": "available"}).sort(
                [("shift_date", 1), ("start_time", 1)]
            )
        )

    def get_shift_by_id(self, shift_id: str) -> dict | None:
        return self._shifts.find_one({"_id": ObjectId(shift_id)})

    def get_student_hours_for_shift_week(
        self, student_id: str, shift_date: str
    ) -> float:
        """Sum the hours of all assigned shifts the student has in the same calendar week as shift_date."""
        parsed = date.fromisoformat(shift_date)
        week_start = (parsed - timedelta(days=parsed.weekday())).isoformat()
        week_end = (parsed + timedelta(days=6 - parsed.weekday())).isoformat()

        docs = self._shifts.find(
            {
                "student_id": student_id,
                "status": "assigned",
                "shift_date": {"$gte": week_start, "$lte": week_end},
            }
        )
        return round(sum(float(d["hours"]) for d in docs), 2)

    def claim_shift(self, shift_id: str, student_id: str) -> bool:
        """Atomically set an available shift to assigned. Returns True if successful."""
        result = self._shifts.update_one(
            {"_id": ObjectId(shift_id), "status": "available"},
            {"$set": {"status": "assigned", "student_id": student_id}},
        )
        return result.modified_count == 1

    def has_pending_drop_request(self, shift_id: str) -> bool:
        return (
            self._requests.count_documents(
                {"shift_id": shift_id, "request_type": "drop", "status": "pending"}
            )
            > 0
        )

    def create_drop_request(self, shift_id: str, student_id: str) -> str:
        from datetime import datetime, timezone

        result = self._requests.insert_one(
            {
                "shift_id": shift_id,
                "request_type": "drop",
                "requested_by": student_id,
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "reviewed_by": None,
                "reviewed_at": None,
            }
        )
        return str(result.inserted_id)
