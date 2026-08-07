from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from builder import PromptBuilder

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Prompt Engine",

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

builder = PromptBuilder()


# ==========================================================
# Request
# ==========================================================

class PromptRequest(BaseModel):
    workbook_path: str

    lesson_package_id: str

    prompt_type: str


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():
    return {

        "service": "Prompt Engine",

        "version": "1.0.0"

    }


# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():
    return {

        "status": "OK",

        "service": "Prompt Engine"

    }


# ==========================================================
# Build Prompt
# ==========================================================

@app.post("/prompt")
def prompt(

        request: PromptRequest

):
    print("=" * 60)
    print("PROMPT REQUEST RECEIVED")
    print("PROMPT TYPE:", request.prompt_type)
    print("=" * 60)
    try:

        return builder.build(

            workbook_path=request.workbook_path,

            lesson_package_id=request.lesson_package_id,

            prompt_type=request.prompt_type

        )

        print("=" * 60)
        print("PROMPT REQUEST RECEIVED")
        print(request.dict())
        print("=" * 60)

    except Exception as e:

        import traceback

        print("=" * 60)

        print("PROMPT ENGINE FAILED")

        traceback.print_exc()

        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )
