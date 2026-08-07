from pathlib import Path

from shared.google.auth import google_credentials

from googleapiclient.discovery import build

from googleapiclient.http import MediaFileUpload

# ==========================================================
# Google Drive Client
# ==========================================================

class GoogleDriveClient:

    SCOPES = [

        "https://www.googleapis.com/auth/drive"

    ]

    def __init__(

        self,

        service_account_file

    ):

        
            credentials=google_credentials()
            service_account_file,

            scopes=self.SCOPES

        )

        self.service = build(

            "drive",

            "v3",

            credentials=credentials

        )

    # ======================================================
    # Upload File
    # ======================================================

    def upload(

        self,

        local_file,

        drive_folder_id,

        mime_type=None

    ):

        local_file = Path(local_file)

        metadata = {

            "name":

                local_file.name,

            "parents":

                [

                    drive_folder_id

                ]

        }

        media = MediaFileUpload(

            str(local_file),

            mimetype=mime_type,

            resumable=True

        )

        uploaded = self.service.files().create(

            body=metadata,

            media_body=media,

            fields="id,name,webViewLink"

        ).execute()

        return uploaded

    # ======================================================
    # Update Existing File
    # ======================================================

    def update(

        self,

        file_id,

        local_file,

        mime_type=None

    ):

        media = MediaFileUpload(

            str(local_file),

            mimetype=mime_type,

            resumable=True

        )

        updated = self.service.files().update(

            fileId=file_id,

            media_body=media,

            fields="id,name,webViewLink"

        ).execute()

        return updated