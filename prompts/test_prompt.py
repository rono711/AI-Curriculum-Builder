from builder import PromptBuilder

WORKBOOK = (
    "/volume1/docker/curriculum-builder/builds/2026/07/Workbook/"
    "BLD_20260716_000115_English_FoundationYear_Language.xlsx"
)

LESSON = "LP_000115_001"

PROMPT = "MISSION"

builder = PromptBuilder()

result = builder.build(

    workbook_path=WORKBOOK,

    lesson_package_id=LESSON,

    prompt_type=PROMPT

)

print()

print("=" * 60)

print("PROMPT GENERATED")

print("=" * 60)

print(result["prompt_file"])

print("=" * 60)

print(result["metadata_file"])

print("=" * 60)
