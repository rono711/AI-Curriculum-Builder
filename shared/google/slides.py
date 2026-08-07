from googleapiclient.discovery import build

from shared.google.auth import google_credentials


# ==========================================================
# Google Slides Client
# ==========================================================

class GoogleSlidesClient:

    def __init__(self):

        credentials = google_credentials()

        self.service = build(

            "slides",

            "v1",

            credentials=credentials

        )

    # ======================================================
    # Get Presentation
    # ======================================================

    def presentation(

        self,

        presentation_id

    ):

        return self.service.presentations().get(

            presentationId=presentation_id

        ).execute()

    # ======================================================
    # Batch Update
    # ======================================================

    def batch_update(

        self,

        presentation_id,

        requests

    ):

        body = {

            "requests": requests

        }

        return self.service.presentations().batchUpdate(

            presentationId=presentation_id,

            body=body

        ).execute()

    # ======================================================
    # Get Slides URL
    # ======================================================

    @staticmethod
    def slides_url(

        presentation_id

    ):

        return (

            "https://docs.google.com/presentation/d/"

            + presentation_id +

            "/edit"

        )

    # ======================================================
    # Embed URL
    # ======================================================

    @staticmethod
    def embed_url(

        presentation_id

    ):

        return (

            "https://docs.google.com/presentation/d/"

            + presentation_id +

            "/embed"

        )

    # ======================================================
    # Thumbnail URL
    # ======================================================

    @staticmethod
    def thumbnail_url(

        presentation_id,

        page_id

    ):

        return (

            "https://slides.googleapis.com/v1/"

            "presentations/"

            f"{presentation_id}"

            "/pages/"

            f"{page_id}"

            "/thumbnail"

        )