from pydantic import BaseModel


# ==========================================================
# Publish Request
# ==========================================================

class PublishRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str


# ==========================================================
# Publish Response
# ==========================================================

class PublishResponse(BaseModel):

    status: str

    lesson_package_id: str

    courseid: int

    sectionid: int