import requests
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from workbook_reader import WorkbookReader
from workbook_updater import WorkbookUpdater

from fastapi.responses import JSONResponse
import json
from pathlib import Path

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(

    title="Rono's School Workbook Service",

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
# Models
# ==========================================================

class ReadWorkbookRequest(BaseModel):
    workbook_path: str

    worksheet: str


class UpdateWorkbookRequest(BaseModel):
    workbook_path: str

    worksheet: str

    lesson_package_id: str

    values: dict


# ==========================================================
# Markdown Update Request
# ==========================================================


class UpdateMarkdownRequest(BaseModel):
    workbook_path: str

    worksheet: str

    lesson_package_id: str

    markdown_file: str

    field: str = "lesson_markdown"


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():
    return {

        "service": "Workbook Service",

        "version": "1.0.0"

    }


# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():
    return {

        "status": "OK",

        "service": "Workbook Service"

    }


# ==========================================================
# Read Worksheet
# ==========================================================

@app.post("/read")
def read(

        request: ReadWorkbookRequest

):
    try:

        reader = WorkbookReader(

            request.workbook_path

        )

        rows = reader.rows(

            request.worksheet

        )

        reader.close()

        return {

            "status": "SUCCESS",

            "rows": rows

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Update Worksheet
# ==========================================================

@app.post("/update")
def update(

        request: UpdateWorkbookRequest

):

    try:

        updater = WorkbookUpdater(

            request.workbook_path

        )
        print("=" * 60)
        print("UPDATE REQUEST")
        print(request.worksheet)
        print(request.lesson_package_id)
        print(request.values)
        print("=" * 60)

        updater.update(

            request.worksheet,

            request.lesson_package_id,

            request.values

        )

        updater.save()
        print("=" * 60)
        print("UPDATE REQUEST")
        print(request.worksheet)
        print(request.lesson_package_id)
        print(request.values)
        print("=" * 60)

        return {

            "status": "SUCCESS"

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Update Markdown
# ==========================================================

@app.post("/update_markdown")
def update_markdown(

        request: UpdateMarkdownRequest

):
    try:
        #
        # Read Markdown
        #

        with open(

                request.markdown_file,

                "r",

                encoding="utf-8"

        ) as f:
            markdown = f.read()
        lesson_json_file = (
                Path(request.markdown_file)
                .parent
                / "lesson_content.json"
        )

        lesson = {}

        if lesson_json_file.exists():
            with open(
                    lesson_json_file,
                    "r",
                    encoding="utf-8"
            ) as f:
                lesson = json.load(f)

        #
        # Update Workbook
        #

        updater = WorkbookUpdater(

            request.workbook_path

        )

        updater.update(

            request.worksheet,

            request.lesson_package_id,

            {

                "content_description":

                    lesson.get("content_description"),

                "elaboration":

                    lesson.get("elaboration"),

                request.field:

                    markdown,

                "generation_status":

                    "COMPLETED",

                "review_status":

                    "PENDING"

            }

        )

        updater.save()
        #
        # ======================================================
        # VERSION 3
        #
        # Workbook update complete.
        #
        # LessonPackageBuilder is now responsible for
        # orchestrating all downstream engines.
        #
        # The orchestration code below is intentionally
        # disabled to avoid duplicate execution.
        #
        # ======================================================
        #

        return {

            "status": "SUCCESS"

        }

        """

        #
        # Generate Slides Prompt
        #

        prompt_response = requests.post(

            "http://127.0.0.1:8005/prompt",

            json={

                "workbook_path":

                    request.workbook_path,

                "lesson_package_id":

                    request.lesson_package_id,

                "prompt_type":

                    "GOOGLE_SLIDES"

            },

            timeout=600

        )

        prompt_response.raise_for_status()

        print("=" * 60)
        print("Slides Prompt Generated")
        print("=" * 60)

        #
        # Workbook
        #

        workbook = Path(

            request.workbook_path

        )

        build_root = str(

            workbook.parent.parent

        )

        build_name = workbook.stem

        #
        # Gamma Engine
        #

        gamma_response = requests.post(

            "http://127.0.0.1:8006/generate",

            json={

                "build_root":

                    build_root,

                "build_name":

                    build_name,

                "lesson_package_id":

                    request.lesson_package_id

            },

            timeout=900

        )

        gamma_response.raise_for_status()

        print("=" * 60)
        print("Gamma Presentation Generated")
        print("=" * 60)

        # ======================================================
        # Generate Quiz Prompt
        # ======================================================

        quiz_prompt = requests.post(

            "http://127.0.0.1:8005/prompt",

            json={

                "workbook_path":

                    request.workbook_path,

                "lesson_package_id":

                    request.lesson_package_id,

                "prompt_type":

                    "QUIZ"

            },

            timeout=600

        )

        quiz_prompt.raise_for_status()

        print("=" * 60)
        print("QUIZ PROMPT GENERATED")
        print("=" * 60)

        # ======================================================
        # Quiz Engine
        # ======================================================

        quiz_response = requests.post(

            "http://127.0.0.1:8002/generate",

            json={

                "build_root":

                    build_root,

                "build_name":

                    build_name,

                "lesson_package_id":

                    request.lesson_package_id

            },

            timeout=900

        )

        quiz_response.raise_for_status()

        print("=" * 60)
        print("QUIZ GENERATED")
        print("=" * 60)

        print("=" * 60)
        print(quiz_response.json())
        print("=" * 60)

        # ======================================================
        # Generate Activities Prompt
        # ======================================================

        activities_prompt = requests.post(

            "http://127.0.0.1:8005/prompt",

            json={

                "workbook_path":

                    request.workbook_path,

                "lesson_package_id":

                    request.lesson_package_id,

                "prompt_type":

                    "ACTIVITIES"

            },

            timeout=600

        )

        activities_prompt.raise_for_status()

        print("=" * 60)
        print("ACTIVITIES PROMPT GENERATED")
        print("=" * 60)
        # ======================================================
        # Generate Let's Do It Prompt
        # ======================================================

        lets_do_it_prompt = requests.post(

            "http://127.0.0.1:8005/prompt",

            json={

                "workbook_path": request.workbook_path,

                "lesson_package_id": request.lesson_package_id,

                "prompt_type": "LETS_DO_IT"

            },

            timeout=600

        )

        lets_do_it_prompt.raise_for_status()

        print("=" * 60)
        print("LETS_DO_IT PROMPT GENERATED")
        print("=" * 60)

        # ======================================================
        # Activities Engine
        # ======================================================

        activities_response = requests.post(

            "http://127.0.0.1:8010/generate",

            json={

                "build_root":

                    build_root,

                "build_name":

                    build_name,

                "lesson_package_id":

                    request.lesson_package_id

            },

            timeout=900

        )

        activities_response.raise_for_status()

        print("=" * 60)
        print("ACTIVITIES GENERATED")
        print("=" * 60)

        # ======================================================
        # Generate Recap Prompt
        # ======================================================

        recap_prompt = requests.post(

            "http://127.0.0.1:8005/prompt",

            json={

                "workbook_path":

                    request.workbook_path,

                "lesson_package_id":

                    request.lesson_package_id,

                "prompt_type":

                    "RECAP"

            },

            timeout=600

        )

        recap_prompt.raise_for_status()

        print("=" * 60)
        print("RECAP PROMPT GENERATED")
        print("=" * 60)

        # ======================================================
        # Recap Engine
        # ======================================================

        recap_response = requests.post(

            "http://127.0.0.1:8011/generate",

            json={

                "build_root":

                    build_root,

                "build_name":

                    build_name,

                "lesson_package_id":

                    request.lesson_package_id

            },

            timeout=900

        )

        recap_response.raise_for_status()

        print("=" * 60)
        print("RECAP GENERATED")
        print("=" * 60)

        print(recap_response.json())

        # ======================================================
        # Publisher Engine
        # ======================================================

        publisher_response = requests.post(

            "http://127.0.0.1:8012/publish",

            json={

                "build_root":

                    build_root,

                "build_name":

                    build_name,

                "lesson_package_id":

                    request.lesson_package_id

            },

            timeout=900

        )

        publisher_response.raise_for_status()

        print("=" * 60)
        print("MOODLE PUBLISH COMPLETED")
        print("=" * 60)

        print(

            publisher_response.json()

        )

        return {

            "status": "SUCCESS"

        }

        """
    except Exception as e:

        import traceback

        print("=" * 60)

        print("UPDATE_MARKDOWN FAILED")

        traceback.print_exc()

        print("=" * 60)

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )

# ==========================================================
# Read Asset Request
# ==========================================================

class ReadAssetRequest(BaseModel):
    build_root: str

    build_name: str

    folder: str

    filename: str


# ==========================================================
# Read Build Asset
# ==========================================================

@app.post("/read_asset")
def read_asset(

        request: ReadAssetRequest

):
    try:

        asset_file = (

                Path(request.build_root)

                / request.folder

                / request.build_name

                / request.filename

        )

        if not asset_file.exists():
            raise HTTPException(

                status_code=404,

                detail=f"{asset_file} not found."

            )

        #
        # JSON
        #

        if asset_file.suffix.lower() == ".json":
            with open(

                    asset_file,

                    "r",

                    encoding="utf-8"

            ) as f:
                return JSONResponse(

                    content=json.load(f)

                )

        #
        # Markdown / Text
        #

        return {

            "content":

                asset_file.read_text(

                    encoding="utf-8"

                )

        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )