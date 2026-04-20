from fastapi import APIRouter
from pydantic import BaseModel
from app.services.quiz_service import generate_validation_quiz

router = APIRouter()

# Data model for incoming quiz request
class QuizRequest(BaseModel):
    student_id: str
    error_type: str
    code_snippet: str

@router.post("/generate")
def create_quiz(data: QuizRequest):
    # Call the AI service to generate the quiz
    quiz_questions = generate_validation_quiz(
        student_id=data.student_id,
        error_type=data.error_type,
        code_snippet=data.code_snippet
    )
    
    return {
        "status": "success",
        "quiz_data": quiz_questions
    }