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
            {"$set": {"status": "denied", "reviewed_by": manager_id, "reviewed_at": now}},
        )
        return True
