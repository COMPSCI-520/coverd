from datetime import date, datetime, timedelta, timezone

from bson import ObjectId
from pymongo.database import Database


class MarketplaceRepository:
    def __init__(self, db: Database):
        self._shifts = db["shifts"]
        self._requests = db["shift_requests"]
        self._users = db["users"]
    
    def get_marketplace_shifts(self) -> list[dict]:
        """
        Return future/today shifts that should appear in the marketplace table.

        available = claimable
        pending (legacy shift row status) = visible but not claimable
        assigned + pending drop request = still on the poster's schedule until a
        manager approves; shown here as not claimable

        Past shifts are excluded because students should not be able to claim shifts
        that have already happened.
        """
        today = date.today().isoformat()

        docs = list(
            self._shifts.find(
                {
                    "status": {"$in": ["available", "pending"]},
                    "shift_date": {"$gte": today},
                }
            ).sort([("shift_date", 1), ("start_time", 1)])
        )
        seen_ids = {str(d["_id"]) for d in docs}

        pending_drop_shift_ids = self._requests.distinct(
            "shift_id",
            {"request_type": "drop", "status": "pending"},
        )
        extra_oids: list[ObjectId] = []
        for sid in pending_drop_shift_ids:
            if sid in seen_ids:
                continue
            try:
                extra_oids.append(ObjectId(sid))
            except Exception:
                continue

        if extra_oids:
            assigned_pending_drop = list(
                self._shifts.find(
                    {
                        "_id": {"$in": extra_oids},
                        "status": "assigned",
                        "shift_date": {"$gte": today},
                    }
                )
            )
            for shift in assigned_pending_drop:
                sid = str(shift["_id"])
                if sid not in seen_ids:
                    docs.append(shift)
                    seen_ids.add(sid)

        docs.sort(key=lambda s: (s["shift_date"], s["start_time"]))

        for shift in docs:
            posted_by_id = shift.get("posted_by") or shift.get("student_id")
            shift["posted_by_name"] = "—"

            if posted_by_id:
                try:
                    user = self._users.find_one({"_id": ObjectId(posted_by_id)})
                    if user:
                        shift["posted_by_name"] = user.get("full_name", "Student")
                except Exception:
                    shift["posted_by_name"] = "Student"

        return docs
    
    def get_shift_by_id(self, shift_id: str) -> dict | None:
        try:
            return self._shifts.find_one({"_id": ObjectId(shift_id)})
        except Exception:
            return None

    def get_student_hours_for_shift_week(self, student_id: str, shift_date: str) -> float:
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
        """
        Atomic claim:
        Only one request can change an available shift to assigned.
        If another student already claimed it, modified_count will be 0.
        """
        try:
            result = self._shifts.update_one(
                {"_id": ObjectId(shift_id), "status": "available"},
                {
                    "$set": {
                        "status": "assigned",
                        "student_id": student_id,
                        "claimed_at": datetime.now(timezone.utc).isoformat(),
                    }
                },
            )
            return result.modified_count == 1
        except Exception:
            return False

    def has_pending_drop_request(self, shift_id: str) -> bool:
        return (
            self._requests.count_documents(
                {
                    "shift_id": shift_id,
                    "request_type": "drop",
                    "status": "pending",
                }
            )
            > 0
        )

    def create_drop_request(self, shift_id: str, student_id: str) -> str:
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