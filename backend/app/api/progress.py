from fastapi import APIRouter
from pydantic import BaseModel
from app.services.progress_service import update_student_progress, get_student_progress

router = APIRouter()

# Data model for incoming progress update
class ProgressRequest(BaseModel):
    student_id: str
    concept: str  
    score: int
    total_questions: int

@router.post("/update")
def update_progress(data: ProgressRequest):
    # Call the service to update database
    result = update_student_progress(
        student_id=data.student_id,
        concept=data.concept,
        score=data.score,
        total=data.total_questions
    )
    return result

@router.get("/{student_id}")
def get_progress(student_id: str):
    # Call the service to fetch student data from Neo4j
    result = get_student_progress(student_id)
    return result