<?php
/**
 * Publisher service for Rono Publisher.
 *
 * Coordinates publishing of curriculum content into Moodle.
 *
 * Current development stage:
 *
 * - Strand Section: enabled.
 * - Sub-strand Subsection: enabled.
 * - Content Description: enabled.
 * - Lesson Pages: enabled.
 * - Question Bank category: enabled.
 * - Question import: enabled for testing.
 * - Quiz creation: NOT YET enabled.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

use moodle_exception;

/**
 * Main publishing orchestrator.
 */
class publisher {

    /**
     * Section service.
     *
     * @var section_service
     */
    private $sections;

    /**
     * Page service.
     *
     * @var page_service
     */
    private $pages;

    /**
     * Lesson service.
     *
     * @var lesson_service
     */
    private $lessons;

    /**
     * Question Bank service.
     *
     * @var question_service
     */
    private $questions;

    /**
     * Constructor.
     */
    public function __construct() {

        $this->sections = new section_service();

        $this->pages = new page_service();

        $this->lessons = new lesson_service();

        $this->questions = new question_service();
    }

    /**
     * Publish one lesson structure and import its questions.
     *
     * Current publishing order:
     *
     * Section: Strand
     *
     *   Subsection: Sub-strand
     *
     *     Text & Media: Content Description
     *
     *     Lesson Content                  indent 0
     *
     *         Did You Know?               indent 1
     *
     *         Question Bank Category
     *         Question Import
     *
     *         [Quiz will be created here later]
     *
     *         Let's Do It                 indent 1
     *
     *         What We Discovered          indent 1
     *
     * @param int $courseid Moodle course ID.
     * @param string $strand Curriculum strand.
     * @param string $substrand Curriculum sub-strand.
     * @param string $contentdescription Curriculum content description.
     * @param array $lesson Lesson data.
     * @return array
     */
    public function publish_structure(
        int $courseid,
        string $strand,
        string $substrand,
        string $contentdescription,
        array $lesson
    ): array {
        global $DB;

        /*
         * =========================================================
         * BASIC VALIDATION
         * =========================================================
         */

        if ($courseid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course ID.'
            );
        }

        if (trim($strand) === '') {
            throw new moodle_exception(
                'Strand cannot be empty.'
            );
        }

        if (trim($substrand) === '') {
            throw new moodle_exception(
                'Sub-strand cannot be empty.'
            );
        }

        if (trim($contentdescription) === '') {
            throw new moodle_exception(
                'Content description cannot be empty.'
            );
        }

        if (empty($lesson['title'])) {
            throw new moodle_exception(
                'Lesson title cannot be empty.'
            );
        }

        /*
         * For the Question Bank test, quiz content is now required.
         */
        if (empty($lesson['quizcontent'])) {
            throw new moodle_exception(
                'Quiz question content cannot be empty.'
            );
        }

        /*
         * =========================================================
         * VERIFY COURSE
         * =========================================================
         */

        $course = $DB->get_record(
            'course',
            [
                'id' => $courseid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * =========================================================
         * START TRANSACTION
         * =========================================================
         */

        $transaction =
            $DB->start_delegated_transaction();

        /*
         * =========================================================
         * STEP 1
         *
         * STRAND -> Moodle Section
         * =========================================================
         */

        $strandsection =
            $this->sections->find_or_create_strand(
                $course->id,
                $strand
            );

        /*
         * =========================================================
         * STEP 2
         *
         * SUB-STRAND -> real Moodle Subsection
         * =========================================================
         */

        $subsection =
            $this->sections->find_or_create_subsection(
                $course->id,
                $strandsection,
                $substrand
            );

        if (empty($subsection['section'])) {
            throw new moodle_exception(
                'Unable to obtain delegated subsection section.'
            );
        }

        /*
         * Activities belonging to this curriculum sub-strand
         * are published into the delegated subsection section.
         */
        $lessonsection =
            $subsection['section'];

        /*
         * =========================================================
         * STEP 3
         *
         * CONTENT DESCRIPTION -> Text & Media
         * =========================================================
         */

        $contentdescriptioncm =
            $this->pages
                ->find_or_create_content_description(
                    $course->id,
                    $lessonsection,
                    $contentdescription
                );

        /*
         * =========================================================
         * STEP 4
         *
         * LESSON / ELABORATION
         *
         * Lesson Content / Mission of the Day
         *
         * indent = 0
         * =========================================================
         */

        $lessoncontent =
            $this->lessons->create_lesson_content(
                $course->id,
                $lessonsection,
                $lesson['title'],
                isset($lesson['lessoncontent'])
                    ? $lesson['lessoncontent']
                    : '',
                isset($lesson['lessondescription'])
                    ? $lesson['lessondescription']
                    : ''
            );

        /*
         * =========================================================
         * STEP 5
         *
         * DID YOU KNOW? / GAMMA
         *
         * indent = 1
         * =========================================================
         */

        $didyouknow =
            $this->lessons->create_did_you_know(
                $course->id,
                $lessonsection,
                isset($lesson['didyouknow'])
                    ? $lesson['didyouknow']
                    : '',
                isset($lesson['didyouknowdescription'])
                    ? $lesson['didyouknowdescription']
                    : ''
            );

        /*
         * =========================================================
         * STEP 6
         *
         * QUESTION BANK TEST
         * =========================================================
         *
         * This is the new part.
         *
         * For every lesson:
         *
         * Lesson title
         *      |
         *      v
         * Dedicated Question Bank category
         *      |
         *      v
         * Import GIFT/XML
         *      |
         *      v
         * Return Question Bank entry IDs
         *
         * NO QUIZ IS CREATED YET.
         * =========================================================
         */

        $questionresult =
            $this->questions->prepare_lesson_questions(
                $course->id,

                $lesson['title'],

                isset($lesson['quizformat'])
                    ? $lesson['quizformat']
                    : 'gift',

                $lesson['quizcontent']
            );

        /*
         * =========================================================
         * FUTURE STEP 7
         *
         * QUIZ WILL GO HERE.
         * =========================================================
         *
         * $quiz = $this->quizzes->create_quiz(...);
         *
         * It will receive the Question Bank entries produced above.
         *
         * Final visual ordering:
         *
         * Lesson Content
         *
         *     Did You Know?
         *
         *     Checking Your Thinking
         *
         *     Let's Do It
         *
         *     What We Discovered
         *
         * =========================================================
         */

        /*
         * =========================================================
         * STEP 7 - CURRENT
         *
         * LET'S DO IT
         *
         * indent = 1
         * =========================================================
         */

        $activities =
            $this->lessons->create_activities(
                $course->id,
                $lessonsection,
                isset($lesson['activities'])
                    ? $lesson['activities']
                    : '',
                isset($lesson['activitiesdescription'])
                    ? $lesson['activitiesdescription']
                    : ''
            );

        /*
         * =========================================================
         * STEP 8
         *
         * WHAT WE DISCOVERED
         *
         * indent = 1
         * =========================================================
         */

        $recap =
            $this->lessons->create_recap(
                $course->id,
                $lessonsection,
                isset($lesson['recap'])
                    ? $lesson['recap']
                    : '',
                isset($lesson['recapdescription'])
                    ? $lesson['recapdescription']
                    : ''
            );

        /*
         * =========================================================
         * STEP 9
         *
         * REBUILD COURSE CACHE
         * =========================================================
         */

        rebuild_course_cache(
            $course->id,
            true
        );

        /*
         * =========================================================
         * STEP 10
         *
         * COMMIT
         * =========================================================
         */

        $transaction->allow_commit();

        /*
         * =========================================================
         * RESPONSE
         * =========================================================
         */

        return [

            'courseid' =>
                (int)$course->id,

            'strandsectionid' =>
                (int)$strandsection->id,

            'subsectioncmid' =>
                (int)$subsection['cmid'],

            'subsectionsectionid' =>
                (int)$lessonsection->id,

            'contentdescriptioncmid' =>
                (int)$contentdescriptioncm->id,

            'lessoncontentcmid' =>
                (int)$lessoncontent->id,

            'didyouknowcmid' =>
                (int)$didyouknow->id,

            /*
             * New Question Bank information.
             */

            'questioncategoryid' =>
                (int)$questionresult['categoryid'],

            'questioncount' =>
                (int)$questionresult['questioncount'],

            'questionbankentryids' =>
                $questionresult['questionbankentryids'],

            'activitiescmid' =>
                (int)$activities->id,

            'recapcmid' =>
                (int)$recap->id,
        ];
    }
}