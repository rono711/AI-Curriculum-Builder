from pathlib import Path
import random
import re


# ==========================================================
# People Asset Selector
# ==========================================================

PROJECT_ROOT = Path(
    "/volume1/docker/curriculum-builder"
)

PEOPLE_ROOT = PROJECT_ROOT / "assets" / "people"

TEACHERS_DIR = PEOPLE_ROOT / "teachers"
STUDENTS_DIR = PEOPLE_ROOT / "students"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
}


# ==========================================================
# Person Identity
#
# Multiple photographs belonging to the same person are
# grouped together so that extra photographs do not increase
# that person's probability of being selected.
# ==========================================================

def _person_key(path, role):

    name = path.stem.lower().strip()

    if role == "teacher":

        # MH / Mohammad Hassan photographs = Teacher 1
        if (
            name.startswith("mh")
            or name.startswith("mohammad hassan")
        ):
            return "teacher_001"

        # NA photographs = Teacher 2
        if name.startswith("na"):
            return "teacher_002"

    if role == "student":

        if name.startswith("aliyah"):
            return "student_001"

        if name.startswith("arshil"):
            return "student_002"

    # Future files still work automatically.
    # An unknown filename is treated as another person.

    key = re.sub(
        r"[^a-z0-9]+",
        "_",
        name
    ).strip("_")

    return key or path.name.lower()


# ==========================================================
# Scan People Folder
# ==========================================================

def _scan_people(folder, role):

    people = {}

    if not folder.exists():
        return people

    for path in sorted(folder.iterdir()):

        if not path.is_file():
            continue

        if path.name == ".gitkeep":
            continue

        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue

        person_key = _person_key(
            path,
            role
        )

        people.setdefault(
            person_key,
            []
        ).append(path)

    return people


# ==========================================================
# Select One Person Fairly
# ==========================================================

def _select_person(people):

    if not people:
        return None

    # Select the PERSON first.
    person_key = random.choice(
        list(people.keys())
    )

    # Then randomly select one photograph of that person.
    reference = random.choice(
        people[person_key]
    )

    return {
        "person_key": person_key,
        "reference": reference,
    }


# ==========================================================
# Public Pool Information
# ==========================================================

def get_people_pool():

    teachers = _scan_people(
        TEACHERS_DIR,
        "teacher"
    )

    students = _scan_people(
        STUDENTS_DIR,
        "student"
    )

    return {
        "teachers": teachers,
        "students": students,
    }


# ==========================================================
# Random Reference Selection
# ==========================================================


def select_reference_people(final_prompt):
    pool = get_people_pool()
    teachers = pool["teachers"]
    students = pool["students"]
    prompt = (final_prompt or "").lower()

    teacher_terms = (
        "teacher",
        "educator",
        "instructor",
    )
    student_terms = (
        "student",
        "students",
        "child",
        "children",
        "learner",
        "learners",
        "pupil",
        "pupils",
    )

    teacher_relevant = any(
        term in prompt
        for term in teacher_terms
    )
    student_relevant = any(
        term in prompt
        for term in student_terms
    )

    references = []
    selected = []

    use_asset_teacher = (
        teacher_relevant
        and bool(teachers)
        and random.random() < 0.40
    )
    use_asset_student = (
        student_relevant
        and bool(students)
        and random.random() < 0.35
    )

    if use_asset_teacher:
        teacher = _select_person(teachers)

        if teacher:
            references.append(
                teacher["reference"]
            )
            selected.append({
                "role": "teacher",
                "person_key": teacher["person_key"],
                "reference": teacher["reference"],
            })

    if use_asset_student:
        student = _select_person(students)

        if student:
            references.append(
                student["reference"]
            )
            selected.append({
                "role": "student",
                "person_key": student["person_key"],
                "reference": student["reference"],
            })

    selected_roles = {
        person["role"]
        for person in selected
    }

    if selected_roles == {"teacher", "student"}:
        mode = "teacher_student"
    elif "teacher" in selected_roles:
        mode = "teacher"
    elif "student" in selected_roles:
        mode = "student"
    else:
        mode = "generated"

    return {
        "mode": mode,
        "references": references,
        "selected": selected,
        "teacher_relevant": teacher_relevant,
        "student_relevant": student_relevant,
    }
