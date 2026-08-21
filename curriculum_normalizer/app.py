from pathlib import Path
import sys

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from normalizer import CurriculumNormalizer
from master_db import MasterDB


# ==========================================================
# Shared Project Modules
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from build_registry import (
    make_elaboration_key,
    get_generated_build,
    get_published_build
)

# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="Rono's School Curriculum Service",
    version="3.0.0"
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://build.ronosschool.com",
        "http://localhost:8001",
        "http://192.168.1.108:8001",
        "http://127.0.0.1:8001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ==========================================================
# Master Database
# ==========================================================

master_db = MasterDB()


# ==========================================================
# Home
# ==========================================================

@app.get("/")
def home():
    return {

        "service": "Curriculum Service",

        "version": "3.0.0"

    }


# ==========================================================
# Health
# ==========================================================

@app.get("/health")
def health():
    return {

        "status": "OK",

        "service": "Curriculum Service",

        "version": "3.0.0",

        "rows": len(master_db.df)
        if not master_db.df.empty
        else 0,

        "curriculum_version": "Australian Curriculum v9"

    }


# ==========================================================
# Normalize Government Workbook
# ==========================================================

@app.post("/normalize")
def normalize():
    try:

        normalizer = CurriculumNormalizer()

        normalizer.run()

        master_db.refresh()

        return {

            "status": "SUCCESS",

            "rows": len(normalizer.df),

            "valid": normalizer.is_valid(),

            "errors": normalizer.validation_errors

        }

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)

        )


# ==========================================================
# Learning Areas
# ==========================================================

@app.get("/learning-areas")
def learning_areas():
    return master_db.learning_areas()


# ==========================================================
# Subjects
# ==========================================================

@app.get("/subjects")
def subjects(

        learning_area: str = Query(...)

):
    return master_db.subjects(

        learning_area

    )


# ==========================================================
# Year Levels
# ==========================================================

@app.get("/year-levels")
def year_levels(

        learning_area: str = Query(...),

        subject: str = Query(...)

):
    return master_db.year_levels(

        learning_area,

        subject

    )


# ==========================================================
# Strands
# ==========================================================

@app.get("/strands")
def strands(

        learning_area: str = Query(...),

        subject: str = Query(...),

        year_level: str = Query(...)

):
    return master_db.strands(

        learning_area,

        subject,

        year_level

    )


# ==========================================================
# Sub-Strands
# ==========================================================

@app.get("/sub-strands")
def sub_strands(

        learning_area: str = Query(...),

        subject: str = Query(...),

        year_level: str = Query(...),

        strand: str = Query(...)

):
    return master_db.sub_strands(

        learning_area,

        subject,

        year_level,

        strand

    )


# ==========================================================
# Topics
# ==========================================================

@app.get("/topics")
def topics(

        learning_area: str,

        subject: str,

        year_level: str,

        strand: str,

        sub_strand: str = Query("")

):
    return master_db.topics(

        learning_area,

        subject,

        year_level,

        strand,

        sub_strand

    )


# ==========================================================
# Lessons
# ==========================================================

@app.get("/lessons")
def lessons(

        parent_code: str = Query(...)

):

    lessons_df = (

        master_db.df[

            master_db.df["Parent Code"] == parent_code

        ]

        .sort_values(

            "Topic Lesson Number"

        )

    )

    results = []

    for _, row in lessons_df.iterrows():

        #
        # Generate the same stable elaboration identity
        # used by Lesson Package Builder / Pipeline Engine.
        #

        elaboration_key = make_elaboration_key(

            year_level=row["Year Level"],

            subject=row["Subject"],

            parent_code=row["Parent Code"],

            topic_id=row["Topic ID"],

            elaboration=row["Elaboration"]

        )

        #
        # Look for the most recent successful publication
        # of this curriculum elaboration.
        #

        published_build = get_published_build(

            elaboration_key

        )
        generated_build = get_generated_build(
            elaboration_key
        )

        generated_pending = (
            generated_build is not None
        )

        pending_build_id = None
        pending_lesson_package_id = None

        if generated_pending:

            pending_build_id = generated_build.get(
                "build_id"
            )

            pending_lesson_package_id = generated_build.get(
                "lesson_package_id"
            )

        already_built = (

            published_build is not None

        )

        if already_built:

            build_status = "PUBLISHED"

            build_id = published_build.get(
                "build_id"
            )

            lesson_package_id = published_build.get(
                "lesson_package_id"
            )

        else:

            if generated_pending:
                build_status = "GENERATED"
            else:
                build_status = "NOT_BUILT"

            build_id = None
            lesson_package_id = None

        results.append({

            "parent_code":

                row["Parent Code"],

            "curriculum_code":

                row["Curriculum Code"],

            "content_description":

                row["Content Description"],

            "topic_id":

                row["Topic ID"],

            "lesson_number":

                int(
                    row["Topic Lesson Number"]
                ),

            "lesson":

                row["Elaboration"],

            #
            # Build Registry
            #

            "elaboration_key":

                elaboration_key,

            "build_status":

                build_status,

            "already_built":

                already_built,

            "can_build":

                (
                    not already_built
                    and
                    not generated_pending
                ),

            "can_update":

                already_built,

            "previous_build_id":

                build_id,

            "previous_lesson_package_id":

                lesson_package_id,

            "generated_pending":

                generated_pending,

            "pending_build_id":

                pending_build_id,

            "pending_lesson_package_id":

                pending_lesson_package_id

        })

    return results


# ==========================================================
# Curriculum Record
# ==========================================================

@app.get("/curriculum")
def curriculum(

        curriculum_code: str = Query(...)

):
    return master_db.curriculum(

        curriculum_code

    )
