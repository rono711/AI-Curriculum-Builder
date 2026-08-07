from pathlib import Path

import requests

from config import N8N_WEBHOOK


# ==========================================================
# n8n Client
# ==========================================================

class N8NClient:

    def __init__(self):

        self.webhook = N8N_WEBHOOK

    # ======================================================
    # Notify Build Complete
    # ======================================================

    def notify_build_complete(

        self,

        workbook_path,

        lesson_package_id

    ):

        workbook = Path(

            workbook_path

        )

        #
        # Workbook:
        #
        # builds/YYYY/MM/Workbook/file.xlsx
        #
        # Build Root:
        #
        # builds/YYYY/MM
        #

        build_root = str(

            workbook.parent.parent

        )

        payload = {

            "build_root":

                build_root,

            "lesson_package_id":

                lesson_package_id,

            "workbook_file":

                workbook.name

        }

        print("=" * 60)
        print("Sending build to n8n")
        print("Webhook :", self.webhook)
        print("Payload :", payload)
        print("=" * 60)

        try:

            response = requests.post(

                self.webhook,

                json=payload,

                timeout=30

            )

            response.raise_for_status()

            print("=" * 60)
            print("n8n notified successfully")
            print("=" * 60)

            return True

        except Exception as e:

            print("=" * 60)
            print("Unable to notify n8n")
            print(str(e))
            print("=" * 60)

            return False