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
    get_latest_build,
    get_published_build,
    get_connection
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
# Curriculum No / Focus
# ==========================================================

@app.get("/curriculum-focuses")
def curriculum_focuses(
        learning_area: str = Query(...),
        subject: str = Query(...),
        year_level: str = Query(...),
        strand: str = Query(...)
):
    return master_db.curriculum_focuses(
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

# ==========================================================
# Canonical Curriculum Order
# ==========================================================

@app.get("/canonical-order")
def canonical_order(
        curriculum_code: list[str] = Query(default=[])
):
    return master_db.canonical_order(
        curriculum_codes=curriculum_code
    )


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
        latest_build = get_latest_build(
            elaboration_key
        )

        latest_status = str(
            (latest_build or {}).get("status") or ""
        ).strip().upper()
        latest_mode = str(
            (latest_build or {}).get("build_mode") or "NEW"
        ).strip().upper()

        update_components = str(
            (latest_build or {}).get("update_components") or ""
        ).strip()

        if not latest_build:
            display_status = "NOT_BUILT"
        elif "FAIL" in latest_status or "ERROR" in latest_status:
            display_status = "FAILED"
        elif latest_mode == "REBUILD":
            if latest_status == "PUBLISHED":
                display_status = "REBUILT"
            else:
                display_status = "REBUILDING"
        elif latest_mode == "UPDATE":
            if latest_status == "PUBLISHED":
                display_status = "UPDATED"
            else:
                display_status = "UPDATING"
        elif latest_status == "PUBLISHED":
            display_status = "PUBLISHED"
        elif latest_status in ("GENERATED", "UPDATE_READY"):
            display_status = "GENERATED"
        elif latest_status == "PUBLISHING":
            display_status = "PUBLISHING"
        else:
            display_status = "GENERATING"

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

            "display_status":

                display_status,

            "latest_build_mode":

                latest_mode,

            "latest_registry_status":

                latest_status,

            "latest_update_components":

                update_components,

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
# Build Selection - Content Descriptions + Lessons
# ==========================================================

@app.get("/build-selection")
def build_selection(
        learning_area: str,
        subject: str,
        year_level: str,
        strand: str,
        sub_strand: str = Query("")
):
    df = master_db.df[
        (master_db.df["Learning Area"] == learning_area)
        &
        (master_db.df["Subject"] == subject)
        &
        (master_db.df["Year Level"] == year_level)
        &
        (master_db.df["Strand"] == strand)
    ].copy()

    has_sub_strands = (
        df["Sub-Strand"]
        .fillna("")
        .astype(str)
        .str.strip()
        .ne("")
        .any()
    )

    if has_sub_strands:
        df = df[
            df["Sub-Strand"] == sub_strand
        ]
    elif sub_strand:
        df = df[
            df["Content Description"] == sub_strand
        ]

    parent_codes = (
        df["Parent Code"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    results = []

    for parent_code in parent_codes:

        lesson_rows = lessons(
            parent_code=parent_code
        )

        if not lesson_rows:
            continue

        first = lesson_rows[0]

        results.append({
            "parent_code":
                first["parent_code"],

            "curriculum_code":
                first["parent_code"],

            "content_description":
                first["content_description"],

            "lesson_count":
                len(lesson_rows),

            "lessons":
                lesson_rows
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

# ==========================================================
# Queue / Batch Scope Items
# ==========================================================

@app.get("/scope-items")
def scope_items(
    learning_area: str,
    subject: str,
    year_level: str = "",
    strand: str = "",
    sub_strand: str = "",
    parent_code: str = ""
):
    df = master_db.df[
        (master_db.df["Learning Area"] == learning_area) &
        (master_db.df["Subject"] == subject)
    ].copy()

    if year_level:
        df = df[df["Year Level"] == year_level]

    if strand:
        df = df[df["Strand"] == strand]

    if sub_strand:
        has_sub_strands = (
            df["Sub-Strand"]
            .fillna("")
            .astype(str)
            .str.strip()
            .ne("")
            .any()
        )

        if has_sub_strands:
            df = df[df["Sub-Strand"] == sub_strand]
        else:
            df = df[df["Content Description"] == sub_strand]

    if parent_code:
        df = df[df["Parent Code"] == parent_code]

    items = []
    total = 0
    published = 0
    generated = 0

    parent_codes = (
        df["Parent Code"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    for code in parent_codes:
        parent_rows = df[df["Parent Code"].astype(str) == code]
        if parent_rows.empty:
            continue

        hierarchy = parent_rows.iloc[0]

        for lesson in lessons(parent_code=code):
            total += 1
            status = str(lesson.get("build_status") or "NOT_BUILT").upper()

            if status == "PUBLISHED":
                published += 1
                continue

            if status == "GENERATED":
                generated += 1
                continue

            if not lesson.get("can_build"):
                continue

            item = dict(lesson)
            item.update({
                "learning_area": str(hierarchy["Learning Area"]),
                "subject": str(hierarchy["Subject"]),
                "year_level": str(hierarchy["Year Level"]),
                "strand": str(hierarchy["Strand"]),
                "sub_strand": (
                    ""
                    if str(hierarchy.get("Sub-Strand", "")).lower() == "nan"
                    else str(hierarchy.get("Sub-Strand", ""))
                ),
            })
            items.append(item)

    return {
        "total": total,
        "eligible": len(items),
        "published": published,
        "generated": generated,
        "items": items,
    }


# ==========================================================
# Queue / Batch Scope Summary
# ==========================================================

@app.get("/scope-summary")
def scope_summary(
    learning_area: str,
    subject: str,
    year_level: str = "",
    strand: str = "",
    sub_strand: str = "",
    parent_code: str = ""
):
    df = master_db.df[
        (master_db.df["Learning Area"] == learning_area) &
        (master_db.df["Subject"] == subject)
    ].copy()

    if year_level:
        df = df[df["Year Level"] == year_level]

    if strand:
        df = df[df["Strand"] == strand]

    if sub_strand:
        df = df[df["Sub-Strand"] == sub_strand]

    if parent_code:
        df = df[df["Parent Code"] == parent_code]

    codes = (
        df["Curriculum Code"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    )

    total = 0
    new = 0
    rebuild = 0
    generated = 0

    for parent_code in (
        df["Parent Code"]
        .dropna()
        .astype(str)
        .drop_duplicates()
        .tolist()
    ):
        for lesson in lessons(parent_code=parent_code):

            total += 1

            if lesson["build_status"] == "PUBLISHED":
                rebuild += 1

            elif lesson["build_status"] == "GENERATED":
                generated += 1

            else:
                new += 1

    return {
        "total": total,
        "new": new,
        "rebuild": rebuild,
        "generated": generated
    }

# ==========================================================
# Teacher Course Progress
# ==========================================================

@app.get("/course-progress")
def course_progress(
    learning_area: str,
    subject: str,
    year_level: str
):
    df = master_db.df[
        (master_db.df["Learning Area"] == learning_area) &
        (master_db.df["Subject"] == subject) &
        (master_db.df["Year Level"] == year_level)
    ].copy()

    items = []

    for _, row in df.iterrows():

        key = make_elaboration_key(
            row["Year Level"],
            row["Subject"],
            row["Parent Code"],
            row["Topic ID"],
            row["Elaboration"]
        )

        published = get_published_build(key)
        generated = get_generated_build(key)

        with get_connection() as db:
            latest = db.execute(
                """
                SELECT status
                FROM elaboration_builds
                WHERE elaboration_key = ?
                ORDER BY id DESC
                LIMIT 1
                """,
                (key,)
            ).fetchone()

        with get_connection() as db:
            queue_row = db.execute(
                """
                SELECT i.status
                FROM build_request_items i
                JOIN build_requests r
                  ON r.request_id = i.request_id
                WHERE i.curriculum_code = ?
                  AND i.status NOT IN ('PUBLISHED', 'FAILED')
                  AND r.status NOT IN ('PUBLISHED', 'FAILED')
                ORDER BY i.id DESC
                LIMIT 1
                """,
                (str(row["Curriculum Code"]),)
            ).fetchone()

        if published:
            state = "PUBLISHED"

        elif generated:
            state = "GENERATED"

        elif queue_row is not None:
            state = "QUEUED"

        elif latest and str(latest["status"]).upper() in (
            "FAILED", "BUILDING", "PROCESSING"
        ):
            state = "FAILED"

        else:
            state = "NEW"

        items.append({
            "state": state,
            "strand": str(row["Strand"]),
            "sub_strand": str(row["Sub-Strand"]),
            "parent_code": str(row["Parent Code"]),
            "content_description":
                str(row["Content Description"]),
            "topic_id": str(row["Topic ID"]),
            "curriculum_code":
                str(row["Curriculum Code"]),
            "lesson_number":
                int(row["Topic Lesson Number"]),
            "lesson": str(row["Elaboration"])
        })

    def first(state):
        return next(
            (x for x in items if x["state"] == state),
            None
        )

    counts = {
        state.lower(): sum(
            x["state"] == state for x in items
        )
        for state in (
            "FAILED",
            "GENERATED",
            "QUEUED",
            "NEW",
            "PUBLISHED"
        )
    }

    return {
        "total": len(items),
        "counts": counts,
        "options": {
            "failed": first("FAILED"),
            "generated": first("GENERATED"),
            "new": first("NEW")
        },
        "course_complete": (
            len(items) > 0 and
            counts["published"] == len(items)
        )
    }
