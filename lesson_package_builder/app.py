from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from pydantic import BaseModel

from builder import LessonPackageBuilder

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Lesson Package Builder",

    version="1.0.0"

)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "https://build.ronosschool.com",

        "http://localhost:8002",

        "http://192.168.1.108:8002"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# ==========================================================
# Builder
# ==========================================================

builder = LessonPackageBuilder()


# ==========================================================
# Request Model
# ==========================================================

class BuildRequest(BaseModel):
    requested_by: str

    learning_area: str

    subject: str

    year_level: str

    strand: str

    sub_strand: str

    parent_code: str

    lesson_numbers: List[int]

    build_mode: str = "NEW"

    update_components: List[str] = []

    publication_mode: str = "IMMEDIATE"

    progress_job_id: str = ""

    progress_url: str = ""
    
    
# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():
    return {

        "service":

            "Lesson Package Builder",

        "version":

            "1.0.0"

    }


# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():
    return {

        "status": "OK",

        "service": "Lesson Package Builder",

        "version": "1.0.0"

    }


# ==========================================================
# Build Lesson Package
# ==========================================================

@app.post("/build")
def build(request: BuildRequest):
    print("===================================")
    print("===== REQUEST RECEIVED =====")
    print(request.dict())
    print("===================================")

    try:
        result = builder.build(request.dict())

        print("===== BUILD RESULT =====")
        print(result)
        print("===================================")

        return result

    except Exception as e:

        import traceback

        ...

        print("=" * 60)
        print("BUILD FAILED")
        traceback.print_exc()
        print("=" * 60)

        raise

    raise HTTPException(
        status_code=500,
        detail=str(e)
    )
