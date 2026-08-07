from pydantic import BaseModel


# ==========================================================
# Generate Request
# ==========================================================

class GammaRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str


# ==========================================================
# Generate Response
# ==========================================================

class GammaResponse(BaseModel):

    status: str

    lesson_package_id: str

    presentation_id: str

    presentation_url: str

    embed_url: str

    pdf_url: str