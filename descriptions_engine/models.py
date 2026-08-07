from pydantic import BaseModel


# ==========================================================
# Description Request
# ==========================================================

class DescriptionRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str