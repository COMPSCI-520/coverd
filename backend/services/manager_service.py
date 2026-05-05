from fastapi import HTTPException, status

from models.user import User
from repositories.manager_repository import ManagerRepository
from schemas.manager import RequestListItem, RequestShiftInfo, RequestsListResponse, ReviewResponse


def list_requests(
    repo: ManagerRepository, status_filter: str | None = None
) -> RequestsListResponse:
    docs = repo.get_requests(status_filter)
    items: list[RequestListItem] = []

    for doc in docs:
        shift_doc = doc.get("shift")
        student_doc = doc.get("student")

        shift = None
        if shift_doc is not None:
            shift = RequestShiftInfo(
                id=str(shift_doc["_id"]),
                location=shift_doc["location"],
                shift_date=shift_doc["shift_date"],
                start_time=shift_doc["start_time"],
                end_time=shift_doc["end_time"],
                hours=float(shift_doc["hours"]),
                status=shift_doc["status"],
            )

        student_name = (
            student_doc.get("full_name", "Unknown") if student_doc else "Unknown"
        )

        items.append(
            RequestListItem(
                id=str(doc["_id"]),
                request_type=doc["request_type"],
                status=doc["status"],
                created_at=doc.get("created_at"),
                student_name=student_name,
                student_id=doc.get("requested_by", ""),
                shift=shift,
                reviewed_by=doc.get("reviewed_by"),
                reviewed_at=doc.get("reviewed_at"),
            )
        )

    return RequestsListResponse(requests=items, total=len(items))


def review_request(
    request_id: str,
    action: str,
    current_user: User,
    repo: ManagerRepository,
) -> ReviewResponse:
    req = repo.get_request_by_id(request_id)

    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    if req["status"] != "pending":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Request has already been {req['status']}",
        )

    if action == "approve":
        success = repo.approve_drop_request(request_id, current_user.id)
    elif action == "deny":
        success = repo.deny_request(request_id, current_user.id)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update request",
        )

    verb = "approved" if action == "approve" else "denied"
    return ReviewResponse(message=f"Request {verb} successfully", request_id=request_id)
