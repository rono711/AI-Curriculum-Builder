from pydantic import BaseModel


# ==========================================================
# Generate Request
# ==========================================================

class QuizRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str


# ==========================================================
# Generate Response
# ==========================================================

class QuizResponse(BaseModel):

    status: str

    lesson_package_id: str

    provider: str

    model: str

    quiz_filename: str

    gift_filename: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int