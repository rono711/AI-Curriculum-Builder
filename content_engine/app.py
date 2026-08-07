from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from builder import CONTENTBuilder

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School CONTENT Engine",

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

builder = CONTENTBuilder()


# ==========================================================
# Request
# ==========================================================

class CONTENTRequest(BaseModel):

    workbook_path: str

    lesson_package_id: str

    prompt_type: str

    provider: str

    prompt: str

    prompt_file: str

    metadata_file: str


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():
    return {

        "service": "CONTENT Engine",

        "version": "1.0.0"

    }


# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():
    return {

        "status": "OK",

        "service": "CONTENT Engine"

    }


# ==========================================================
# Generate
# ==========================================================

@app.post("/generate")
def generate(

        request: CONTENTRequest

):
    print("=" * 60)
    print("CONTENT REQUEST RECEIVED")
    print("PROMPT TYPE:", request.prompt_type)
    print("=" * 60)
    try:

        return builder.generate(

            request

        )


    except Exception as e:

        import traceback

        print("=" * 60)

        print("CONTENT ENGINE FAILED")

        traceback.print_exc()

        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )