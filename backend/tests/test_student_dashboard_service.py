from services.student_dashboard_service import (
    get_student_dashboard,
    get_student_month_schedule,
    get_student_requests,
)

class FakeStudentUser:
    def __init__(
        self,
        id="student-1",
        full_name="Alex Student",
        is_international=True,
    ):
        self.id = id
        self.full_name = full_name
        self.is_international = is_international


class FakeStudentDashboardRepo:
    def __init__(self):
        self.weekly_shifts = []
        self.upcoming_shifts = []
        self.pending_count = 0
        self.marketplace_count = 0
        self.month_shifts = []
        self.student_requests = []
        self.pending_drop_shift_ids: set[str] = set()

    def get_student_weekly_shifts(self, student_id, week_start, week_end):
        return self.weekly_shifts

    def get_upcoming_student_shifts(self, student_id, today):
        return self.upcoming_shifts

    def count_pending_requests(self, student_id):
        return self.pending_count

    def count_marketplace_available_this_week(self, week_start, week_end):
        return self.marketplace_count

    def get_shift_ids_with_pending_drop_requests(self, student_id):
        return set(self.pending_drop_shift_ids)

    def get_student_month_shifts(self, student_id, month_start, month_end):
        return self.month_shifts
    
    def get_student_requests(self, student_id):
        return self.student_requests


def test_student_dashboard_calculates_hours_and_remaining_limit():
    repo = FakeStudentDashboardRepo()
    repo.weekly_shifts = [
        {
            "_id": "shift-1",
            "shift_date": "2026-06-08",
            "location": "Worcester DC",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4.0,
            "status": "assigned",
        },
        {
            "_id": "shift-2",
            "shift_date": "2026-06-09",
            "location": "Berkshire DC",
            "start_time": "16:00",
            "end_time": "20:00",
            "hours": 4.0,
            "status": "assigned",
        },
    ]
    repo.upcoming_shifts = repo.weekly_shifts
    repo.pending_count = 1
    repo.marketplace_count = 3

    user = FakeStudentUser(is_international=True)

    response = get_student_dashboard(user, repo)

    assert response.full_name == "Alex Student"
    assert response.hours_this_week == 8.0
    assert response.weekly_limit == 20
    assert response.remaining_hours == 12.0
    assert response.show_warning is True
    assert response.warning_message == "You have used 8.0 of your 20 weekly allowed hours."
    assert response.pending_requests_count == 1
    assert response.marketplace_available_count == 3
    assert response.upcoming_shifts_count == 2
    assert len(response.weekly_shifts) == 2
    assert response.next_shift.location == "Worcester DC"


def test_domestic_student_has_no_weekly_limit_warning():
    repo = FakeStudentDashboardRepo()
    user = FakeStudentUser(is_international=False)

    response = get_student_dashboard(user, repo)

    assert response.weekly_limit is None
    assert response.remaining_hours is None
    assert response.show_warning is False
    assert response.warning_message is None
    assert response.hours_this_week == 0
    assert response.upcoming_shifts_count == 0
    assert response.next_shift is None


def test_student_dashboard_marks_weekly_shift_pending_drop_from_requests():
    repo = FakeStudentDashboardRepo()
    repo.weekly_shifts = [
        {
            "_id": "shift-1",
            "shift_date": "2026-06-08",
            "location": "Worcester DC",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4.0,
            "status": "assigned",
        },
    ]
    repo.upcoming_shifts = repo.weekly_shifts
    repo.pending_drop_shift_ids = {"shift-1"}

    user = FakeStudentUser()

    response = get_student_dashboard(user, repo)

    assert response.weekly_shifts[0].has_pending_drop is True


def test_student_dashboard_handles_no_upcoming_shifts():
    repo = FakeStudentDashboardRepo()
    repo.weekly_shifts = [
        {
            "_id": "shift-1",
            "shift_date": "2026-06-08",
            "location": "Franklin Dining",
            "start_time": "09:00",
            "end_time": "13:00",
            "hours": 4.0,
            "status": "assigned",
        }
    ]
    repo.upcoming_shifts = []

    user = FakeStudentUser(is_international=True)

    response = get_student_dashboard(user, repo)

    assert response.hours_this_week == 4.0
    assert response.remaining_hours == 16.0
    assert response.upcoming_shifts_count == 0
    assert response.next_shift is None


def test_student_month_schedule_returns_requested_month_shifts():
    repo = FakeStudentDashboardRepo()
    repo.month_shifts = [
        {
            "_id": "shift-1",
            "shift_date": "2026-06-08",
            "location": "Worcester DC",
            "start_time": "08:00",
            "end_time": "12:00",
            "hours": 4.0,
            "status": "assigned",
        },
        {
            "_id": "shift-2",
            "shift_date": "2026-06-10",
            "location": "Berkshire DC",
            "start_time": "16:00",
            "end_time": "20:00",
            "hours": 4.0,
            "status": "pending",
        },
    ]

    user = FakeStudentUser()

    response = get_student_month_schedule(user, repo, month=6, year=2026)

    assert response.month == 6
    assert response.year == 2026
    assert len(response.shifts) == 2
    assert response.shifts[0].location == "Worcester DC"
    assert response.shifts[0].hours == 4.0
    assert response.shifts[1].status == "pending"


def test_student_month_schedule_handles_empty_month():
    repo = FakeStudentDashboardRepo()
    user = FakeStudentUser()

    response = get_student_month_schedule(user, repo, month=7, year=2026)

    assert response.month == 7
    assert response.year == 2026
    assert response.shifts == []

def test_get_student_requests_maps_request_and_shift_data():
    repo = FakeStudentDashboardRepo()
    repo.student_requests = [
        {
            "_id": "request-1",
            "request_type": "drop",
            "status": "pending",
            "created_at": "2026-06-08T10:00:00Z",
            "reviewed_at": None,
            "shift": {
                "_id": "shift-1",
                "location": "Worcester DC",
                "shift_date": "2026-06-08",
                "start_time": "08:00",
                "end_time": "12:00",
                "hours": 4.0,
            },
        }
    ]

    user = FakeStudentUser()

    response = get_student_requests(user, repo)

    assert response.total == 1
    assert response.requests[0].id == "request-1"
    assert response.requests[0].request_type == "drop"
    assert response.requests[0].status == "pending"
    assert response.requests[0].shift.location == "Worcester DC"
    assert response.requests[0].shift.hours == 4.0