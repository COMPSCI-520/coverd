import pytest
from fastapi import HTTPException
from services.manager_service import get_staff_schedule, review_request


class FakeManagerUser:
    def __init__(self, id="manager-1", role="manager"):
        self.id = id
        self.role = role


class FakeManagerRepo:
    def __init__(self):
        self.request = None
        self.approve_result = True
        self.deny_result = True
        self.approved_request_id = None
        self.denied_request_id = None

    def get_request_by_id(self, request_id):
        return self.request

    def approve_drop_request(self, request_id, manager_id):
        self.approved_request_id = request_id
        return self.approve_result

    def deny_request(self, request_id, manager_id):
        self.denied_request_id = request_id
        return self.deny_result
    
    def get_student_users(self, student_search=None):
        return [
            {
                "_id": "student-1",
                "full_name": "Alex Student",
                "email": "student@coverd.dev",
                "is_international": True,
            },
            {
                "_id": "student-2",
                "full_name": "Taylor Kim",
                "email": "taylor@coverd.dev",
                "is_international": False,
            },
        ]

    def get_staff_shifts(self, week_start, week_end, location=None):
        return [
            {
                "_id": "shift-1",
                "student_id": "student-1",
                "location": "Worcester DC",
                "shift_date": week_start,
                "start_time": "08:00",
                "end_time": "12:00",
                "hours": 4.0,
                "status": "assigned",
            },
            {
                "_id": "shift-2",
                "student_id": "student-1",
                "location": "Berkshire DC",
                "shift_date": week_start,
                "start_time": "16:00",
                "end_time": "20:00",
                "hours": 4.0,
                "status": "assigned",
            },
        ]

    def get_pending_drop_requests_for_shifts(self, shift_ids):
        return [
            {
                "shift_id": "shift-1",
                "request_type": "drop",
                "status": "pending",
            }
        ]

    def get_shifts_needing_coverage(self, week_start, week_end, location=None):
        return [
            {
                "_id": "shift-3",
                "location": "Franklin Dining",
                "shift_date": week_start,
                "start_time": "09:00",
                "end_time": "13:00",
                "hours": 4.0,
            }
        ]

def test_review_request_returns_404_when_request_missing():
    repo = FakeManagerRepo()
    manager = FakeManagerUser()

    with pytest.raises(HTTPException) as exc:
        review_request("missing-request", "approve", manager, repo)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Request not found"


def test_review_request_blocks_already_reviewed_request():
    repo = FakeManagerRepo()
    repo.request = {
        "_id": "request-1",
        "status": "approved",
    }
    manager = FakeManagerUser()

    with pytest.raises(HTTPException) as exc:
        review_request("request-1", "approve", manager, repo)

    assert exc.value.status_code == 409
    assert exc.value.detail == "Request has already been approved"


def test_review_request_blocks_invalid_action():
    repo = FakeManagerRepo()
    repo.request = {
        "_id": "request-1",
        "status": "pending",
    }
    manager = FakeManagerUser()

    with pytest.raises(HTTPException) as exc:
        review_request("request-1", "invalid", manager, repo)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Invalid action"


def test_approve_request_success():
    repo = FakeManagerRepo()
    repo.request = {
        "_id": "request-1",
        "status": "pending",
    }
    manager = FakeManagerUser()

    response = review_request("request-1", "approve", manager, repo)

    assert response.message == "Request approved successfully"
    assert response.request_id == "request-1"
    assert repo.approved_request_id == "request-1"


def test_deny_request_success():
    repo = FakeManagerRepo()
    repo.request = {
        "_id": "request-1",
        "status": "pending",
    }
    manager = FakeManagerUser()

    response = review_request("request-1", "deny", manager, repo)

    assert response.message == "Request denied successfully"
    assert response.request_id == "request-1"
    assert repo.denied_request_id == "request-1"

def test_get_staff_schedule_calculates_staff_summary():
    repo = FakeManagerRepo()

    response = get_staff_schedule(
        repo,
        week_start="2026-06-08",
        view="week",
    )

    assert response.week_start == "2026-06-08"
    assert response.week_end == "2026-06-14"
    assert response.total_staff == 2
    assert response.scheduled_shifts == 2
    assert response.scheduled_hours == 8.0
    assert response.pending_drops == 1
    assert response.coverage_needed_count == 1


def test_get_staff_schedule_calculates_international_remaining_hours():
    repo = FakeManagerRepo()

    response = get_staff_schedule(
        repo,
        week_start="2026-06-08",
        view="week",
    )

    alex = response.staff[0]

    assert alex.full_name == "Alex Student"
    assert alex.is_international is True
    assert alex.hours_this_week == 8.0
    assert alex.weekly_limit == 20
    assert alex.remaining_hours == 12.0
    assert alex.pending_drop_count == 1


def test_get_staff_schedule_includes_coverage_needed_shifts():
    repo = FakeManagerRepo()

    response = get_staff_schedule(
        repo,
        week_start="2026-06-08",
        view="week",
    )

    assert len(response.shifts_needing_coverage) == 1
    assert response.shifts_needing_coverage[0].location == "Franklin Dining"
    assert response.shifts_needing_coverage[0].hours == 4.0