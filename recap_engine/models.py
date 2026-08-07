from pydantic import BaseModel


# ==========================================================
# Generate Request
# ==========================================================

class RecapRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str


# ==========================================================
# Generate Response
# ==========================================================

class RecapResponse(BaseModel):

    status: str

    lesson_package_id: str

    provider: str

    model: str

    markdown_file: str

    html_file: str

    json_file: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int