import pytest
from fastapi import HTTPException

from services.marketplace_service import (
    claim_shift,
    list_available_shifts,
    request_drop,
)


class FakeUser:
    def __init__(
        self,
        id="student-1",
        role="student",
        full_name="Alex Student",
        is_international=False,
    ):
        self.id = id
        self.role = role
        self.full_name = full_name
        self.is_international = is_international


class FakeMarketplaceRepo:
    def __init__(self):
        self.shift = None
        self.marketplace_shifts = []
        self.hours = 0.0
        self.claim_result = True
        self.pending_drop_exists = False
        self.created_drop_request = "request-1"

    def get_marketplace_shifts(self):
        return self.marketplace_shifts

    def get_student_hours_for_shift_week(self, student_id, shift_date):
        return self.hours

    def get_shift_by_id(self, shift_id):
        return self.shift

    def claim_shift(self, shift_id, student_id):
        return self.claim_result

    def has_pending_drop_request(self, shift_id):
        return self.pending_drop_exists

    def create_drop_request(self, shift_id, student_id):
        return self.created_drop_request


def test_list_available_shifts_marks_available_shift_as_claimable():
    repo = FakeMarketplaceRepo()
    repo.marketplace_shifts = [
        {
            "_id": "shift-1",
            "location": "Worcester DC",
            "shift_date": "2026-06-08",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4.0,
            "status": "available",
            "posted_by_name": "Maya Patel",
        }
    ]

    user = FakeUser(is_international=True)

    response = list_available_shifts(user, repo)

    assert response.total == 1
    assert response.shifts[0].can_claim is True
    assert response.shifts[0].would_exceed_limit is False
    assert response.remaining_capacity == 20.0


def test_list_available_shifts_blocks_international_student_over_20_hours():
    repo = FakeMarketplaceRepo()
    repo.hours = 18.0
    repo.marketplace_shifts = [
        {
            "_id": "shift-1",
            "location": "Berkshire DC",
            "shift_date": "2026-06-08",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4.0,
            "status": "available",
            "posted_by_name": "Taylor Kim",
        }
    ]

    user = FakeUser(is_international=True)

    response = list_available_shifts(user, repo)

    assert response.shifts[0].can_claim is False
    assert response.shifts[0].would_exceed_limit is True
    assert "exceeding the 20-hr limit" in response.shifts[0].claim_block_reason


def test_manager_cannot_claim_shift():
    repo = FakeMarketplaceRepo()
    user = FakeUser(role="manager")

    with pytest.raises(HTTPException) as exc:
        claim_shift("shift-1", user, repo)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Only students can claim marketplace shifts"


def test_claim_shift_returns_404_when_shift_missing():
    repo = FakeMarketplaceRepo()
    user = FakeUser()

    with pytest.raises(HTTPException) as exc:
        claim_shift("missing-shift", user, repo)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Shift not found"


def test_claim_shift_blocks_non_available_shift():
    repo = FakeMarketplaceRepo()
    repo.shift = {
        "_id": "shift-1",
        "status": "pending",
        "shift_date": "2026-06-08",
        "hours": 4.0,
    }
    user = FakeUser()

    with pytest.raises(HTTPException) as exc:
        claim_shift("shift-1", user, repo)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Shift is no longer available"


def test_claim_shift_blocks_international_student_over_limit():
    repo = FakeMarketplaceRepo()
    repo.hours = 18.0
    repo.shift = {
        "_id": "shift-1",
        "status": "available",
        "shift_date": "2026-06-08",
        "hours": 4.0,
    }
    user = FakeUser(is_international=True)

    with pytest.raises(HTTPException) as exc:
        claim_shift("shift-1", user, repo)

    assert exc.value.status_code == 422
    assert "exceeding the 20-hr limit" in exc.value.detail


def test_claim_shift_success():
    repo = FakeMarketplaceRepo()
    repo.shift = {
        "_id": "shift-1",
        "status": "available",
        "shift_date": "2026-06-08",
        "hours": 4.0,
    }
    user = FakeUser()

    response = claim_shift("shift-1", user, repo)

    assert response.message == "Shift claimed successfully"
    assert response.shift_id == "shift-1"


def test_drop_shift_only_allows_own_assigned_shift():
    repo = FakeMarketplaceRepo()
    repo.shift = {
        "_id": "shift-1",
        "student_id": "different-student",
        "status": "assigned",
        "shift_date": "2026-06-08",
        "end_time": "12:00",
    }
    user = FakeUser(id="student-1")

    with pytest.raises(HTTPException) as exc:
        request_drop("shift-1", user, repo)

    assert exc.value.status_code == 403
    assert exc.value.detail == "You can only request to drop your own shifts"


def test_drop_shift_success():
    repo = FakeMarketplaceRepo()
    repo.shift = {
        "_id": "shift-1",
        "student_id": "student-1",
        "status": "assigned",
        "shift_date": "2099-06-08",
        "end_time": "12:00",
    }
    user = FakeUser(id="student-1")

    response = request_drop("shift-1", user, repo)

    assert response.message == "Drop request submitted for manager review"
    assert response.shift_id == "shift-1"
    assert response.request_id == "request-1"