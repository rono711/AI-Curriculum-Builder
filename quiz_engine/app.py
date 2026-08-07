import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(

        0,

        str(PROJECT_ROOT)

    )

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from builder import QuizBuilder

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Quiz Engine",

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

builder = QuizBuilder()

# ==========================================================
# Request
# ==========================================================

class QuizRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str

# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {

        "service":

            "Quiz Engine",

        "version":

            "1.0.0"

    }

# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():

    return {

        "status":

            "OK"

    }

# ==========================================================
# Generate
# ==========================================================

@app.post("/generate")
def generate(

        request: QuizRequest

):

    try:

        return builder.generate(

            build_root=request.build_root,

            build_name=request.build_name,

            lesson_package_id=request.lesson_package_id

        )

    except Exception as e:

        import traceback

        print("=" * 60)

        print("QUIZ ENGINE FAILED")

        traceback.print_exc()

        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )