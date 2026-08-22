# ==========================================================
# OpenAI Batch Pipeline Configuration
# ==========================================================

STAGE1_PROMPT_TYPES = (
    "LESSON_CONTENT",
    "DISPLAY_TITLE",
    "MISSION",
    "DID_YOU_KNOW",
    "CHECKING_YOUR_THINKING",
    "LETS_DO_IT",
    "WHAT_WE_DISCOVERED",
)

STAGE2_PROMPT_TYPES = (
    "QUIZ",
    "ACTIVITIES",
    "RECAP",
)

NON_BATCH_PROMPT_TYPES = (
    "GAMMA_SLIDES",
    "IMAGE",
)


def get_batch_stage(prompt_type):

    prompt_type = str(
        prompt_type
    ).strip().upper()

    if prompt_type in STAGE1_PROMPT_TYPES:
        return 1

    if prompt_type in STAGE2_PROMPT_TYPES:
        return 2

    if prompt_type in NON_BATCH_PROMPT_TYPES:
        return None

    raise ValueError(
        f"Unknown Batch prompt type: {prompt_type}"
    )
