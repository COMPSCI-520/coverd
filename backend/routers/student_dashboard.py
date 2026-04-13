from fastapi import APIRouter, Depends
from pymongo.database import Database

from dependencies.auth import get_current_user
from dependencies.database import get_db
from models.user import User
from repositories.student_dashboard_repository import StudentDashboardRepository
from schemas.dashboard import StudentDashboardResponse
from services.student_dashboard_service import get_student_dashboard

router = APIRouter(prefix="/students", tags=["Student Dashboard"])


@router.get("/me/dashboard", response_model=StudentDashboardResponse)
def read_student_dashboard(
    current_user: User = Depends(get_current_user),
    db: Database = Depends(get_db),
):
    repo = StudentDashboardRepository(db)
    return get_student_dashboard(current_user, repo)