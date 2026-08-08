<?php
/**
 * Publisher service for Rono Publisher.
 *
 * Coordinates publishing of curriculum content into Moodle.
 *
 * This initial version is intentionally a structural-test version.
 * Question Bank and Quiz publishing will be added after the Moodle
 * Section -> Subsection -> activities hierarchy has been verified.
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
    public function __construct() {
        $this->sections = new section_service();
        $this->pages = new page_service();
        $this->lessons = new lesson_service();
    }

    /**
     * Publish the structural components of one lesson.
     *
     * Current structure:
     *
     * Section: Strand
     *
     *   Subsection: Sub-strand
     *
     *     Text & Media: Content Description
     *
     *     Lesson Content                  indent 0
     *         Did You Know?               indent 1
     *         Let's Do It                 indent 1
     *         What We Discovered          indent 1
     *
     * The quiz will later be inserted between Did You Know?
     * and Let's Do It.
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
         * ---------------------------------------------------------
         * Validate basic input.
         * ---------------------------------------------------------
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
         * Confirm course exists before starting.
         */
        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        /*
         * ---------------------------------------------------------
         * Start Moodle database transaction.
         * ---------------------------------------------------------
         *
         * If an exception is thrown during publishing, Moodle will
         * roll back the database changes made in this transaction.
         */

        $transaction = $DB->start_delegated_transaction();

        /*
         * ---------------------------------------------------------
         * STEP 1
         *
         * Find or create Strand SECTION.
         *
         * Example:
         *
         * Language
         * ---------------------------------------------------------
         */

        $strandsection =
            $this->sections->find_or_create_strand(
                $course->id,
                $strand
            );

        /*
         * ---------------------------------------------------------
         * STEP 2
         *
         * Find or create real Moodle SUBSECTION.
         *
         * Example:
         *
         * Language for interacting with others
         * ---------------------------------------------------------
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
         * This is the delegated Moodle course section belonging
         * to mod_subsection.
         *
         * All Content Description and lesson activities go here.
         */
        $lessonsection = $subsection['section'];

        /*
         * ---------------------------------------------------------
         * STEP 3
         *
         * Find or create Content Description.
         *
         * This is a Moodle Text & Media activity and should be the
         * first curriculum item inside the subsection.
         * ---------------------------------------------------------
         */

        $contentdescriptioncm =
            $this->pages->find_or_create_content_description(
                $course->id,
                $lessonsection,
                $contentdescription
            );

        /*
         * ---------------------------------------------------------
         * STEP 4
         *
         * Create main Lesson Content / Mission page.
         *
         * indent = 0
         * ---------------------------------------------------------
         */

        $lessoncontent =
            $this->lessons->create_lesson_content(
                $course->id,
                $lessonsection,
                $lesson['title'],
                $lesson['lessoncontent'] ?? '',
                $lesson['lessondescription'] ?? ''
            );

        /*
         * ---------------------------------------------------------
         * STEP 5
         *
         * Create Did You Know? / Gamma page.
         *
         * indent = 1
         * ---------------------------------------------------------
         */

        $didyouknow =
            $this->lessons->create_did_you_know(
                $course->id,
                $lessonsection,
                $lesson['didyouknow'] ?? '',
                $lesson['didyouknowdescription'] ?? ''
            );

        /*
         * =========================================================
         * QUIZ WILL GO HERE.
         * =========================================================
         *
         * Final version:
         *
         * Question Bank category
         *        ↓
         * Import GIFT/XML
         *        ↓
         * Obtain question references
         *        ↓
         * Create Checking Your Thinking quiz
         *        ↓
         * Attach questions
         *        ↓
         * indent = 1
         *
         * We deliberately do NOT implement that yet.
         * =========================================================
         */

        /*
         * ---------------------------------------------------------
         * STEP 6
         *
         * Create Let's Do It.
         *
         * indent = 1
         * ---------------------------------------------------------
         */

        $activities =
            $this->lessons->create_activities(
                $course->id,
                $lessonsection,
                $lesson['activities'] ?? '',
                $lesson['activitiesdescription'] ?? ''
            );

        /*
         * ---------------------------------------------------------
         * STEP 7
         *
         * Create What We Discovered.
         *
         * indent = 1
         * ---------------------------------------------------------
         */

        $recap =
            $this->lessons->create_recap(
                $course->id,
                $lessonsection,
                $lesson['recap'] ?? '',
                $lesson['recapdescription'] ?? ''
            );

        /*
         * ---------------------------------------------------------
         * STEP 8
         *
         * Rebuild course cache after course structure changes.
         * ---------------------------------------------------------
         */

        rebuild_course_cache(
            $course->id,
            true
        );

        /*
         * ---------------------------------------------------------
         * STEP 9
         *
         * Commit transaction.
         * ---------------------------------------------------------
         */

        $transaction->allow_commit();

        /*
         * ---------------------------------------------------------
         * Return identifiers.
         * ---------------------------------------------------------
         */

        return [
            'courseid' => (int)$course->id,

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

            'activitiescmid' =>
                (int)$activities->id,

            'recapcmid' =>
                (int)$recap->id,
        ];
    }
}