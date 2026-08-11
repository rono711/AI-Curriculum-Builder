import os
import requests
from dotenv import load_dotenv

# Load root .env.
load_dotenv()

moodle_url = os.getenv("MOODLE_URL")
moodle_token = os.getenv("MOODLE_TOKEN")

if not moodle_url:
    raise RuntimeError("MOODLE_URL is missing from .env")

if not moodle_token:
    raise RuntimeError("MOODLE_TOKEN is missing from .env")

endpoint = moodle_url.rstrip("/") + "/webservice/rest/server.php"

payload = {
    "wstoken": moodle_token,
    "wsfunction": "local_rono_publisher_publish_lesson",
    "moodlewsrestformat": "json",

    # Target test course.
    "courseid": 47,

    # Moodle Section.
    "strand": "Language",

    # Real Moodle Subsection.
    "substrand": "Language for interacting with others",

    # First Text & Media activity inside subsection.
    "contentdescription": (
        "<strong>TEST CONTENT DESCRIPTION</strong><br>"
        "How We Change Our Language"
    ),

    # Main lesson.
    "lesson[title]": "TEST Lesson 1 - How We Change Our Language",

    "lesson[lessoncontent]": (
        "<h3>Mission of the Day</h3>"
        "<p>This is a structural publishing test from Rono Publisher.</p>"
    ),

    "lesson[lessondescription]": (
        "<p>Test Lesson Content description.</p>"
    ),

    # Did You Know?
    "lesson[didyouknow]": (
        "<h3>Did You Know?</h3>"
        "<p>This is where the Gamma Slides will be embedded.</p>"
    ),

    "lesson[didyouknowdescription]": (
        "<p>Test Did You Know description.</p>"
    ),

    # Quiz fields are sent but should NOT be processed yet.
    "lesson[quiztitle]": "Checking Your Thinking",
    "lesson[quizdescription]": "Quiz structural placeholder.",
    "lesson[quizformat]": "gift",
    "lesson[quizcontent]": "",

    # Activities.
    "lesson[activities]": (
        "<h3>Let's Do It</h3>"
        "<p>This is the test student activity content.</p>"
    ),

    "lesson[activitiesdescription]": (
        "<p>Test activities description.</p>"
    ),

    # Recap.
    "lesson[recap]": (
        "<h3>What We Discovered</h3>"
        "<p>This is the test lesson recap.</p>"
    ),

    "lesson[recapdescription]": (
        "<p>Test recap description.</p>"
    ),
}

print("Calling Rono Publisher...")
print(f"Course ID: {payload['courseid']}")
print(f"Endpoint: {endpoint}")
print()

response = requests.post(
    endpoint,
    data=payload,
    timeout=60,
)

print("HTTP status:", response.status_code)
print()
print("Moodle response:")
print(response.text)
