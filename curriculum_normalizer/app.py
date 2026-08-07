from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from normalizer import CurriculumNormalizer
from master_db import MasterDB

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
    lessons = (

        master_db.df[

            master_db.df["Parent Code"] == parent_code

            ]

        .sort_values(

            "Topic Lesson Number"

        )

    )

    return [

        {

            "topic_id":

                row["Topic ID"],

            "lesson_number":

                int(

                    row["Topic Lesson Number"]

                ),

            "lesson":

                row["Elaboration"]

        }

        for _, row in lessons.iterrows()

    ]


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
