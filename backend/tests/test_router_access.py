import pytest
from fastapi import HTTPException

from routers.manager import require_manager


class FakeUser:
    def __init__(self, role):
        self.role = role


def test_require_manager_allows_manager():
    manager = FakeUser(role="manager")

    result = require_manager(manager)

    assert result == manager


def test_require_manager_blocks_student():
    student = FakeUser(role="student")

    with pytest.raises(HTTPException) as exc:
        require_manager(student)

    assert exc.value.status_code == 403
    assert exc.value.detail == "Manager access required"