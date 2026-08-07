import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )

from workbook_reader import WorkbookReader
from moodle_client import MoodleClient
from page_publisher import PagePublisher
from quiz_publisher import QuizPublisher
from sync_writer import SyncWriter


# ==========================================================
# Publisher Builder
# ==========================================================

class PublisherBuilder:

    def __init__(self):

        self.reader = WorkbookReader()

        self.moodle = MoodleClient()

        self.pages = PagePublisher(
            self.moodle
        )

        self.quiz = QuizPublisher(
            self.moodle
        )

        self.sync = SyncWriter()

    # ======================================================
    # Publish
    # ======================================================

    def publish(

            self,

            build_root,

            build_name,

            lesson_package_id

    ):

        workbook = (

            Path(build_root)

            / "Workbook"

            / f"{build_name}.xlsx"

        )

        print("=" * 60)
        print("PUBLISHER WORKBOOK")
        print(workbook)
        print("=" * 60)

        lesson = self.reader.read(
            workbook,
            lesson_package_id
        )
        
        print("=" * 60)
        print("DISPLAY TITLE READ")
        print(
            lesson["descriptions"].get("display_title")
        )
        print("=" * 60)

        metadata = lesson["metadata"]

        #
        # ---------------------------------------------
        # Determine School Level
        # ---------------------------------------------
        #
        print("=" * 60)
        print("METADATA KEYS")
        print(metadata.keys())
        print(metadata)
        print("=" * 60)
        year = str(
            metadata["year_level"]
        ).strip()

        if year in [
            "Foundation Year",
            "Year 1",
            "Year 2"
        ]:

            school_level = "Primary"

        elif year in [
            "Year 3",
            "Year 4",
            "Year 5",
            "Year 6"
        ]:

            school_level = "Upper Primary"

        elif year in [
            "Year 7",
            "Year 8",
            "Year 9",
            "Year 10"
        ]:

            school_level = "Secondary"

        else:

            school_level = "Senior Secondary"

        print("=" * 60)
        print("LESSON METADATA")
        print(metadata)
        print("=" * 60)

        payload = {

            "build_id":

                build_name,

            "lesson_package_id":

                metadata["lesson_package_id"],

            "school_level":

                metadata["school_level"],

            "subject":

                metadata["subject"],

            "year_level":

                metadata["year_level"]

        }

        print("=" * 60)
        print("PAYLOAD TO MOODLE")
        print(payload)
        print("=" * 60)

        course = self.moodle.publish_course(
            payload
        )
        #
        # Section
        #

        section = self.moodle.publish_section({

            "courseid":

                course["courseid"],

            "strand":

                metadata["strand"],

            "sub-strand":

                metadata["sub_strand"]

        })

        #
        # Mission
        #
        mission = self.pages.publish_mission(

            course,

            section,

            lesson,

            build_root,

            build_name

        )
        #
        # Did You Know
        #
        did_you_know = self.pages.publish_did_you_know(

            course,

            section,

            lesson,

            build_root,

            build_name

        )
        #
        activities = self.pages.publish_activities(

            course,

            section,

            lesson,

            build_root,

            build_name

        )
        # Quiz
        #

        quiz = self.quiz.publish(

            course,

            section,

            lesson,

            build_root,

            build_name

        )
        print("=" * 60)
        print("QUIZ RETURN")
        print(quiz)
        print(type(quiz))
        print("=" * 60)
        #
        # Recap
        #

        recap = self.pages.publish_recap(

            course,

            section,

            lesson,

            build_root,

            build_name

        )

        #
        # Update Workbook
        #

        self.sync.update(

            workbook,

            lesson_package_id,

            course,

            section,

            mission,

            quiz,

            activities,

            recap

        )

        #
        # Finished
        #

        return {

            "status":

                "SUCCESS",

            "lesson_package_id":

                lesson_package_id,

            "course":

                course,

            "section":

                section,

            "mission":

                mission,
            "did_you_know":

                did_you_know,

            "quiz":

                quiz,

            "activities":

                activities,

            "recap":

                recap

        }
