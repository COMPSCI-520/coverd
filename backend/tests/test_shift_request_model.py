from models.shift_request import ShiftRequest


def test_shift_request_from_mongo_maps_id():
    mongo_doc = {
        "_id": "abc123",
        "shift_id": "shift1",
        "request_type": "claim",
        "requested_by": "user1",
        "status": "pending",
        "created_at": None,
        "reviewed_by": None,
        "reviewed_at": None,
    }

    result = ShiftRequest.from_mongo(mongo_doc)

    assert result.id == "abc123"
    assert result.shift_id == "shift1"
    assert result.request_type == "claim"
    assert result.requested_by == "user1"
    assert result.status == "pending"


def test_shift_request_can_be_created_for_drop_request():
    request = ShiftRequest(
        id="req1",
        shift_id="shift2",
        request_type="drop",
        requested_by="student1",
        status="pending",
    )

    assert request.request_type == "drop"
    assert request.status == "pending"