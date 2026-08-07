from pathlib import Path

# ==========================================================
# Quiz Publisher
# ==========================================================

class QuizPublisher:

    def __init__(

            self,

            moodle

    ):

        self.moodle = moodle

    # ======================================================
    # Publish Quiz
    # ======================================================

    def publish(
            self,
            course,
            section,
            lesson,
            build_root,
            build_name
    ):
        print("=" * 60)
        print("QUIZ PUBLISH")
        print("build_root :", build_root)
        print("build_name :", build_name)
        print("type(build_name):", type(build_name))
        print("=" * 60)
        metadata = lesson["metadata"]

        quiz = lesson["quiz"]
        print("=" * 60)
        print("QUIZ OBJECT")
        print(quiz)
        print("=" * 60)

        descriptions = lesson["descriptions"]
        lesson_package_id = metadata["lesson_package_id"]

        #
        # --------------------------------------------------
        # Create GIFT file
        # --------------------------------------------------

        gift_file = (

                Path(build_root)

                / "Quiz"

                / build_name

                / quiz["gift_filename"]

        )

        #
        # --------------------------------------------------
        # Moodle Payload
        # --------------------------------------------------
        #

        payload = {

            "lesson_package_id":

                lesson_package_id,

            "activity_type":

                "QUIZ",

            "courseid":

                course["courseid"],

            "section":

                section["section"],

            "title":

                "📝 Check Your Thinking",

            "description":

                descriptions.get(

                    "quiz_description",

                    ""

                ),

            "gift_file":

                str(gift_file)

        }

        if not quiz.get("gift_filename"):
            print("=" * 60)
            print("QUIZ NOT GENERATED - SKIPPING")
            print("=" * 60)

            return {
                "status": "SKIPPED",
                "cmid": 0,
                "quizid": 0,
                "url": ""
            }
        print("=" * 60)
        print("QUIZ PAYLOAD")
        print(payload)
        print("=" * 60)

        result = self.moodle.publish_quiz(

            payload

        )

        print("=" * 60)
        print("QUIZ MOODLE RESULT")
        print(result)
        print(type(result))
        print("=" * 60)

        return result