import json
import sys
from pathlib import Path

import httpx


ROOT = Path(
    "/volume1/docker/curriculum-builder"
)


CONTENT_URL = (
    "http://content-engine:8006/"
    "save-batch-result"
)


def extract_text(body):

    parts = []

    for item in body.get("output") or []:
        if item.get("type") != "message":
            continue

        for content in item.get("content") or []:
            if content.get("type") == "output_text":
                text = content.get("text")
                if text:
                    parts.append(text)

    if not parts:
        raise RuntimeError(
            "No output_text found."
        )

    return "\n".join(parts)


def main(request_id):
    rid = str(request_id).strip()

    batch_dir = ROOT / "data" / "batches" / rid
    output_file = batch_dir / "stage1_output.jsonl"
    manifest_file = batch_dir / "stage1_manifest.json"
    state_file = batch_dir / "prepare_state.json"
    applied_file = batch_dir / "stage1_applied.json"


    if applied_file.exists():
        raise RuntimeError(
            "Stage 1 already applied."
        )

    manifest = json.loads(
        manifest_file.read_text()
    )

    state = json.loads(
        state_file.read_text()
    )

    rows = {}

    for line in output_file.read_text().splitlines():
        if not line.strip():
            continue

        row = json.loads(line)

        rows[row["custom_id"]] = row

    expected_count = int(
        manifest.get("request_count") or 0
    )

    if len(rows) != expected_count:
        raise RuntimeError(
            f"Expected {expected_count} results, "
            f"found {len(rows)}."
        )

    workbook_path = state["workbook_path"]

    applied = []

    with httpx.Client(timeout=900) as client:

        for entry in manifest["entries"]:

            custom_id = entry["custom_id"]

            if custom_id not in rows:
                raise RuntimeError(
                    "Missing result: " + custom_id
                )

            row = rows[custom_id]

            if row.get("error"):
                raise RuntimeError(
                    f"{custom_id}: {row['error']}"
                )

            response = row.get("response") or {}

            if response.get("status_code") != 200:
                raise RuntimeError(
                    f"{custom_id}: HTTP "
                    f"{response.get('status_code')}"
                )

            body = response.get("body") or {}

            if body.get("status") != "completed":
                raise RuntimeError(
                    f"{custom_id}: "
                    f"{body.get('status')}"
                )

            markdown = extract_text(body)

            usage = body.get("usage") or {}

            result = client.post(
                CONTENT_URL,
                json={
                    "workbook_path":
                        workbook_path,
                    "lesson_package_id":
                        entry["lesson_package_id"],
                    "prompt_type":
                        entry["prompt_type"],
                    "markdown":
                        markdown,
                    "model":
                        body.get("model") or "",
                    "tokens":
                        usage.get("total_tokens"),
                }
            )

            result.raise_for_status()

            saved = result.json()

            if saved.get("status") != "SUCCESS":
                raise RuntimeError(
                    "Content Engine save failed: "
                    + str(saved)
                )

            print(
                "APPLIED:",
                entry["prompt_type"]
            )

            applied.append({
                "custom_id": custom_id,
                "prompt_type":
                    entry["prompt_type"],
                "markdown_file":
                    saved["markdown_file"],
                "json_file":
                    saved["json_file"],
            })

    applied_file.write_text(
        json.dumps(
            {
                "request_id": rid,
                "count": len(applied),
                "entries": applied,
            },
            indent=2
        ),
        encoding="utf-8"
    )

    print("STAGE 1 APPLIED:", len(applied))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit(
            "Usage: python3 batch_engine/apply_stage1.py "
            "<REQUEST_ID>"
        )

    main(sys.argv[1])
