import json
from pathlib import Path

from batch_engine.batch_file_builder import BatchFileBuilder
from batch_engine.config import STAGE1_PROMPT_TYPES


class Stage1BatchBuilder:

    def __init__(self):
        self.batch_builder = BatchFileBuilder()

    @staticmethod
    def make_custom_id(request_id, lesson_package_id, prompt_type):
        return (
            f"{request_id}__"
            f"{lesson_package_id}__"
            f"{str(prompt_type).upper()}"
        )

    def build(
        self,
        request_id,
        prompt_results,
        output_root="data/batches"
    ):
        request_dir = Path(output_root) / str(request_id)
        request_dir.mkdir(parents=True, exist_ok=True)

        batch_requests = []
        manifest_entries = []

        for result in prompt_results:
            prompt_type = str(
                result["prompt_type"]
            ).upper()

            if prompt_type not in STAGE1_PROMPT_TYPES:
                continue

            lesson_package_id = result["lesson_package_id"]
            prompt_path = Path(result["prompt_file"])
            metadata_path = Path(result["metadata_file"])

            if not prompt_path.is_file():
                raise FileNotFoundError(
                    f"Prompt file not found: {prompt_path}"
                )

            if not metadata_path.is_file():
                raise FileNotFoundError(
                    f"Metadata file not found: {metadata_path}"
                )

            prompt = prompt_path.read_text(
                encoding="utf-8"
            )

            custom_id = self.make_custom_id(
                request_id,
                lesson_package_id,
                prompt_type
            )

            batch_requests.append(
                self.batch_builder.make_request(
                    custom_id=custom_id,
                    prompt=prompt
                )
            )

            manifest_entries.append({
                "custom_id": custom_id,
                "request_id": str(request_id),
                "lesson_package_id": lesson_package_id,
                "prompt_type": prompt_type,
                "prompt_file": str(prompt_path),
                "metadata_file": str(metadata_path),
            })

        if not batch_requests:
            raise RuntimeError(
                "No Stage 1 prompts were supplied."
            )

        input_path = request_dir / "stage1_input.jsonl"
        manifest_path = request_dir / "stage1_manifest.json"

        self.batch_builder.write_jsonl(
            batch_requests,
            input_path
        )

        manifest = {
            "request_id": str(request_id),
            "stage": 1,
            "request_count": len(batch_requests),
            "input_file": str(input_path),
            "entries": manifest_entries,
        }

        manifest_path.write_text(
            json.dumps(
                manifest,
                indent=2,
                ensure_ascii=False
            ),
            encoding="utf-8"
        )

        return {
            "request_id": str(request_id),
            "stage": 1,
            "request_count": len(batch_requests),
            "input_file": str(input_path),
            "manifest_file": str(manifest_path),
        }
