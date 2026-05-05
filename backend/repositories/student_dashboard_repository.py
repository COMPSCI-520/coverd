from bson import ObjectId
from pymongo.database import Database


class StudentDashboardRepository:
    def __init__(self, db: Database):
        self._shifts = db["shifts"]
        self._shift_requests = db["shift_requests"]

    def get_student_weekly_shifts(
        self,
        student_id: str,
        week_start: str,
        week_end: str,
    ) -> list[dict]:
        return list(
            self._shifts.find(
                {
                    "student_id": student_id,
                    "status": "assigned",
                    "shift_date": {"$gte": week_start, "$lte": week_end},
                }
            ).sort("shift_date", 1)
        )

    def get_upcoming_student_shifts(self, student_id: str, today: str) -> list[dict]:
        return list(
            self._shifts.find(
                {
                    "student_id": student_id,
                    "status": "assigned",
                    "shift_date": {"$gte": today},
                }
            ).sort([("shift_date", 1), ("start_time", 1)])
        )

    def count_pending_requests(self, student_id: str) -> int:
        return self._shift_requests.count_documents(
            {
                "requested_by": student_id,
                "status": "pending",
            }
        )

    def count_marketplace_available_this_week(
        self,
        week_start: str,
        week_end: str,
    ) -> int:
        return self._shifts.count_documents(
            {
                "status": "available",
                "shift_date": {"$gte": week_start, "$lte": week_end},
            }
        )

    def get_student_requests(self, student_id: str) -> list[dict]:
        """Return all requests for a student, newest first, with shift info joined."""
        requests = list(
            self._shift_requests.find({"requested_by": student_id}).sort("created_at", -1)
        )
        for req in requests:
            shift_id = req.get("shift_id")
            req["shift"] = None
            if shift_id:
                try:
                    req["shift"] = self._shifts.find_one({"_id": ObjectId(shift_id)})
                except Exception:
                    pass
        return requests