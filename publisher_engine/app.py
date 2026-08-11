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

from builder import PublisherBuilder

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Publisher Engine",

    version="1.0.0"

)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "*"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# ==========================================================
# Builder
# ==========================================================

builder = PublisherBuilder()

# ==========================================================
# Request
# ==========================================================

class PublishRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str

class UpdatePublishRequest(BaseModel):

    build_root: str

    build_name: str

    lesson_package_id: str

    update_components: list[str]

    moodle_identity: dict
    
# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():

    return {

        "service":

            "Publisher Engine",

        "version":

            "1.0.0"

    }

# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():

    return {

        "status":"OK",
        "service": "Publisher Engine"

    }

# ==========================================================
# Publish
# ==========================================================

@app.post("/publish")
def publish(

        request: PublishRequest

):

    try:

        return builder.publish(

            build_root=request.build_root,

            build_name=request.build_name,

            lesson_package_id=request.lesson_package_id

        )

    except Exception as e:

        import traceback

        print("=" * 60)

        print("PUBLISHER ENGINE FAILED")

        traceback.print_exc()

        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
        # ==========================================================
# Publish Selective UPDATE
# ==========================================================

@app.post("/publish/update")
def publish_update(

        request: UpdatePublishRequest

):

    try:

        return builder.publish_update(

            build_root=
                request.build_root,

            build_name=
                request.build_name,

            lesson_package_id=
                request.lesson_package_id,

            update_components=
                request.update_components,

            moodle_identity=
                request.moodle_identity

        )

    except Exception as e:

        import traceback

        print("=" * 60)
        print("PUBLISHER UPDATE FAILED")
        traceback.print_exc()
        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )
