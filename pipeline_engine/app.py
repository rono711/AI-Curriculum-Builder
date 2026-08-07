from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import PipelineRequest

from builder import PipelineBuilder

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Pipeline Engine",

    version="1.0.0"

)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "https://build.ronosschool.com",

        "http://localhost:8001",

        "http://192.168.1.108:8001"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# ==========================================================
# Builder
# ==========================================================

builder = PipelineBuilder()

# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {

        "service": "Pipeline Engine",

        "version": "1.0.0"

    }

# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():

    return {

        "status": "OK",

        "service": "Pipeline Engine"

    }

# ==========================================================
# Run Pipeline
# ==========================================================

@app.post("/run")
def run_pipeline(

        request: PipelineRequest

):

    try:

        print("=" * 60)
        print("PIPELINE REQUEST RECEIVED")
        print("Build Root :", request.build_root)
        print("Build Name :", request.build_name)
        print("Lessons    :", len(request.lesson_rows))
        print("=" * 60)

        result = builder.run(

            request.build_root,

            request.build_name,

            request.lesson_rows

        )

        return result

    except Exception as e:

        import traceback

        print("=" * 60)
        print("PIPELINE ENGINE FAILED")
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )