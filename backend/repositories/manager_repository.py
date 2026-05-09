from datetime import datetime, timezone

from bson import ObjectId
from pymongo.database import Database


class ManagerRepository:
    def __init__(self, db: Database):
        self._shifts = db["shifts"]
        self._requests = db["shift_requests"]
        self._users = db["users"]

    def get_requests(self, status_filter: str | None = None) -> list[dict]:
        query: dict = {}
        if status_filter:
            query["status"] = status_filter

        requests = list(self._requests.find(query).sort("created_at", -1))

        for req in requests:
            shift_id = req.get("shift_id")
            req["shift"] = None
            if shift_id:
                try:
                    req["shift"] = self._shifts.find_one({"_id": ObjectId(shift_id)})
                except Exception:
                    pass

            student_id = req.get("requested_by")
            req["student"] = None
            if student_id:
                try:
                    req["student"] = self._users.find_one({"_id": ObjectId(student_id)})
                except Exception:
                    pass

        return requests

    def get_request_by_id(self, request_id: str) -> dict | None:
        try:
            req = self._requests.find_one({"_id": ObjectId(request_id)})
        except Exception:
            return None

        if req is None:
            return None

        shift_id = req.get("shift_id")
        req["shift"] = None
        if shift_id:
            try:
                req["shift"] = self._shifts.find_one({"_id": ObjectId(shift_id)})
            except Exception:
                pass

        return req

    def approve_drop_request(self, request_id: str, manager_id: str) -> bool:
        req = self._requests.find_one({"_id": ObjectId(request_id)})
        if req is None:
            return False

        now = datetime.now(timezone.utc).isoformat()
        self._requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "approved", "reviewed_by": manager_id, "reviewed_at": now}},
        )

        shift_id = req.get("shift_id")
        if shift_id:
            try:
                self._shifts.update_one(
                    {"_id": ObjectId(shift_id)},
                    {"$set": {"status": "available", "student_id": None}},
                )
            except Exception:
                pass

        return True

    def deny_request(self, request_id: str, manager_id: str) -> bool:
        req = self._requests.find_one({"_id": ObjectId(request_id)})
        if req is None:
            return False

        now = datetime.now(timezone.utc).isoformat()

        self._requests.update_one(
            {"_id": ObjectId(request_id)},
            {
                "$set": {
                    "status": "denied",
                    "reviewed_by": manager_id,
                    "reviewed_at": now,
                }
            },
        )

        shift_id = req.get("shift_id")
        student_id = req.get("requested_by")

        if shift_id and student_id:
            try:
                self._shifts.update_one(
                    {"_id": ObjectId(shift_id)},
                    {
                        "$set": {
                            "status": "assigned",
                            "student_id": student_id,
                        },
                        "$unset": {
                            "posted_by": "",
                        },
                    },
                )
            except Exception:
                pass

        return True
    
    def get_student_users(self, student_search: str | None = None) -> list[dict]:
        query: dict = {"role": "student"}

        if student_search:
            query["$or"] = [
                {"full_name": {"$regex": student_search, "$options": "i"}},
                {"email": {"$regex": student_search, "$options": "i"}},
            ]

        return list(self._users.find(query).sort("full_name", 1))

    def get_staff_shifts(
        self,
        week_start: str,
        week_end: str,
        location: str | None = None,
    ) -> list[dict]:
        query: dict = {
            "student_id": {"$ne": None},
            "status": {"$in": ["assigned", "pending"]},
            "shift_date": {"$gte": week_start, "$lte": week_end},
        }

        if location and location != "All locations":
            query["location"] = location

        return list(self._shifts.find(query).sort([("shift_date", 1), ("start_time", 1)]))

    def get_pending_drop_requests_for_shifts(self, shift_ids: list[str]) -> list[dict]:
        if not shift_ids:
            return []

        return list(
            self._requests.find(
                {
                    "shift_id": {"$in": shift_ids},
                    "request_type": "drop",
                    "status": "pending",
                }
            )
        )
    
    def get_shifts_needing_coverage(
        self,
        week_start: str,
        week_end: str,
        location: str | None = None,
    ) -> list[dict]:
        """
        Return shifts whose drop request was approved and that are now available
        in the marketplace but have not been claimed yet.
        """
        shift_query: dict = {
            "student_id": None,
            "status": "available",
            "shift_date": {"$gte": week_start, "$lte": week_end},
        }

        if location and location != "All locations":
            shift_query["location"] = location

        available_shifts = list(
            self._shifts.find(shift_query).sort([("shift_date", 1), ("start_time", 1)])
        )

        if not available_shifts:
            return []

        shift_ids = [str(shift["_id"]) for shift in available_shifts]

        approved_requests = list(
            self._requests.find(
                {
                    "shift_id": {"$in": shift_ids},
                    "request_type": "drop",
                    "status": "approved",
                }
            )
        )

        approved_shift_ids = {request["shift_id"] for request in approved_requests}

        return [
            shift
            for shift in available_shifts
            if str(shift["_id"]) in approved_shift_ids
        ]
    
