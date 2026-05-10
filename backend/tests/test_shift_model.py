from models.shift import Shift


def test_shift_from_mongo_maps_fields():
    mongo_doc = {
        "_id": "shift-1",
        "student_id": "student-1",
        "location": "Worcester DC",
        "shift_date": "2026-06-08",
        "start_time": "08:00",
        "end_time": "12:00",
        "hours": 4.0,
        "status": "assigned",
    }

    result = Shift.from_mongo(mongo_doc)

    assert result.id == "shift-1"
    assert result.student_id == "student-1"
    assert result.location == "Worcester DC"
    assert result.shift_date == "2026-06-08"
    assert result.start_time == "08:00"
    assert result.end_time == "12:00"
    assert result.hours == 4.0
    assert result.status == "assigned"


def test_shift_can_be_created_for_available_marketplace_shift():
    shift = Shift(
        id="shift-2",
        student_id=None,
        location="Berkshire DC",
        shift_date="2026-06-10",
        start_time="16:00",
        end_time="20:00",
        hours=4.0,
        status="available",
    )

    assert shift.id == "shift-2"
    assert shift.student_id is None
    assert shift.location == "Berkshire DC"
    assert shift.status == "available"
    assert shift.hours == 4.0


def test_shift_can_be_created_for_pending_shift():
    shift = Shift(
        id="shift-3",
        student_id="student-1",
        location="Franklin Dining",
        shift_date="2026-06-12",
        start_time="09:00",
        end_time="13:00",
        hours=4.0,
        status="pending",
    )

    assert shift.id == "shift-3"
    assert shift.student_id == "student-1"
    assert shift.location == "Franklin Dining"
    assert shift.status == "pending"
    assert shift.hours == 4.0