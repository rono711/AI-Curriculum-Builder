#!/bin/sh

set -a
. ./.env
set +a

if [ -z "$MOODLE_URL" ]; then
    echo "ERROR: MOODLE_URL is not loaded"
    exit 1
fi

if [ -z "$MOODLE_TOKEN" ]; then
    echo "ERROR: MOODLE_TOKEN is not loaded"
    exit 1
fi

echo "Testing Rono Publisher Question Bank..."
echo "Course: 47"
echo

curl -sS \
  -w '\nHTTP_STATUS=%{http_code}\n' \
  -X POST \
  "${MOODLE_URL%/}/webservice/rest/server.php" \
  --data-urlencode "wstoken=${MOODLE_TOKEN}" \
  --data-urlencode "wsfunction=local_rono_publisher_publish_lesson" \
  --data-urlencode "moodlewsrestformat=json" \
  --data-urlencode "courseid=47" \
  --data-urlencode "strand=Language" \
  --data-urlencode "substrand=Language for interacting with others" \
  --data-urlencode "contentdescription=TEST CONTENT DESCRIPTION - How We Change Our Language" \
  --data-urlencode "lesson[title]=TEST Lesson 9 - Complete Quiz Grade Test" \
  --data-urlencode "lesson[lessoncontent]=Mission of the Day - Moodle Question Bank publishing test." \
  --data-urlencode "lesson[lessondescription]=Question Bank integration test." \
  --data-urlencode "lesson[didyouknow]=Did You Know? - Gamma placeholder." \
  --data-urlencode "lesson[didyouknowdescription]=Question Bank test." \
  --data-urlencode "lesson[quiztitle]=Checking Your Thinking" \
  --data-urlencode "lesson[quizdescription]=Three-question Question Bank test." \
  --data-urlencode "lesson[quizformat]=gift" \
  --data-urlencode "lesson[quizcontent]=::Rono Test MCQ:: What is 2 + 2? {=4 ~3 ~5}

::Rono Test TF:: The sky is blue. {TRUE}

::Rono Test Short:: What word means the opposite of hot? {=cold}" \
  --data-urlencode "lesson[activities]=Let's Do It - Question Bank test activity." \
  --data-urlencode "lesson[activitiesdescription]=Test activity." \
  --data-urlencode "lesson[recap]=What We Discovered - Question Bank integration test recap." \
  --data-urlencode "lesson[recapdescription]=Test recap."

echo
