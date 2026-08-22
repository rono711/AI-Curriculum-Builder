import json
import os
from pathlib import Path


class BatchFileBuilder:

    def __init__(self):

        self.model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.4-mini"
        )

    def make_request(
            self,
            custom_id,
            prompt
    ):

        return {
            "custom_id": custom_id,
            "method": "POST",
            "url": "/v1/responses",
            "body": {
                "model": self.model,
                "input": prompt
            }
        }

    def write_jsonl(
            self,
            requests,
            output_path
    ):

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with output_path.open(
            "w",
            encoding="utf-8"
        ) as handle:

            for request in requests:

                handle.write(
                    json.dumps(
                        request,
                        ensure_ascii=False
                    )
                    + "\n"
                )

        return str(output_path)
