import pytest
from fastapi import HTTPException

from services.manager_service import review_request


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