<?php
/**
 * Publisher service for Rono Publisher.
 *
 * Current development stage:
 *
 * - Strand Section: enabled.
 * - Sub-strand Subsection: enabled.
 * - Content Description: enabled.
 * - Lesson Pages: enabled.
 * - Quiz creation: enabled.
 * - Question Bank import into Quiz module context: enabled.
 * - Question attachment to Quiz: not yet enabled.
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
     * @var section_service
     */
    private $sections;

    /**
     * @var page_service
     */
    private $pages;

    /**
     * @var lesson_service
     */
    private $lessons;

    /**
     * @var quiz_service
     */
    private $quizzes;

    /**
     * @var question_service
     */
    private $questions;

    /**
     * Constructor.
     */
    public function __construct() {

        $this->sections =
            new section_service();

        $this->pages =
            new page_service();

        $this->lessons =
            new lesson_service();

        $this->quizzes =
            new quiz_service();

        $this->questions =
            new question_service();
    }

    /**
     * Publish one complete lesson structure and import its questions.
     *
     * Current publishing sequence:
     *
     * Strand Section
     *      |
     * Sub-strand Subsection
     *      |
     * Content Description
     *      |
     * Lesson Content                  indent 0
     *      |
     * Did You Know?                   indent 1
     *      |
     * Checking Your Thinking          indent 1
     *      |
     * Quiz module context
     *      |
     * Question Bank category
     *      |
     * GIFT/XML import
     *      |
     * [Question attachment comes later]
     *      |
     * Let's Do It                     indent 1
     *      |
     * What We Discovered              indent 1
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
        string $curriculumcode,
        string $elaboration,
        string $contentdescription,
        string $parentcode,
        string $contentdescriptionimagename,
        string $contentdescriptionimage,
        array $lesson
	): array {

	    global $DB;

        /*
         * =========================================================
         * VALIDATION
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

        if (trim($curriculumcode) === '') {
            throw new moodle_exception(
                'Curriculum code cannot be empty.'
            );
        }

        if (trim($elaboration) === '') {
            throw new moodle_exception(
                'Curriculum elaboration cannot be empty.'
            );
        }

        if (trim($contentdescription) === '') {
            throw new moodle_exception(
                'Content description cannot be empty.'
            );
        }

		        if (trim($parentcode) === '') {
            throw new moodle_exception(
                'Parent curriculum code cannot be empty.'
            );
        }

        if (trim($contentdescriptionimagename) === '') {
            throw new moodle_exception(
                'Content Description image filename cannot be empty.'
            );
        }

        if (trim($contentdescriptionimage) === '') {
            throw new moodle_exception(
                'Content Description image cannot be empty.'
            );
        }
		if (empty($lesson['title'])) {
            throw new moodle_exception(
                'Lesson title cannot be empty.'
            );
        }

        /*
         * Question Bank import is active again.
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
         * SUB-STRAND -> Moodle Subsection
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
         * All lesson activities are placed in this delegated
         * Moodle subsection section.
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
                    $elaboration,
                    $curriculumcode,
                    $contentdescriptionimagename,
                    $contentdescriptionimage
                );

        /*
         * =========================================================
         * STEP 4
         *
         * LESSON CONTENT / MISSION OF THE DAY
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
         * CREATE CHECKING YOUR THINKING QUIZ
         *
         * indent = 1
         * =========================================================
         */

        $quizresult =
            $this->quizzes->create_quiz(
                $course->id,
                $lessonsection,
                isset($lesson['quiztitle'])
                    ? $lesson['quiztitle']
                    : 'Checking Your Thinking',
                isset($lesson['quizdescription'])
                    ? $lesson['quizdescription']
                    : '',
                1
            );

        if (
            empty($quizresult['quizid']) ||
            empty($quizresult['cmid']) ||
            empty($quizresult['contextid'])
        ) {
            throw new moodle_exception(
                'Quiz was created but required Quiz identifiers were not returned.'
            );
        }

        /*
         * =========================================================
         * STEP 7
         *
         * QUESTION BANK
         * =========================================================
         *
         * CRITICAL:
         *
         * We now pass QUIZ CMID rather than course ID.
         *
         * question_service will therefore use:
         *
         * context_module::instance($quizcmid)
         *
         * This is the Moodle 5.2 module context required by
         * the Question Bank import workflow.
         * =========================================================
         */

        $questionresult =
    $this->questions->prepare_lesson_questions(
        (int)$course->id,

        (int)$quizresult['cmid'],

        $lesson['title'],

        isset($lesson['quizformat'])
            ? $lesson['quizformat']
            : 'gift',

        $lesson['quizcontent']
    );
    
            /*
         * =========================================================
         * STEP 8
         *
         * ATTACH IMPORTED QUESTIONS TO QUIZ
         * =========================================================
         *
         * question_service has already:
         *
         * 1. Created the Question Bank category.
         * 2. Imported the GIFT/XML questions.
         * 3. Resolved the latest Moodle question IDs.
         *
         * We now attach those questions to the
         * Checking Your Thinking Quiz.
         * =========================================================
         */

        if (empty($questionresult['questionids'])) {
            throw new moodle_exception(
                'Question Bank import succeeded but no Moodle question IDs were returned.'
            );
        }

        $attachmentresult =
            $this->quizzes->attach_questions(
                (int)$quizresult['quizid'],
                $questionresult['questionids']
            );
            
            

        /*
         * Verify Moodle created Quiz slots.
         */
        if (empty($attachmentresult['slotcount'])) {
            throw new moodle_exception(
                'Questions were imported but no Quiz slots were created.'
            );
        }
        
        /*
         * =========================================================
         * STEP 8
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
         * STEP 9
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
         * STEP 10
         *
         * COMMIT TRANSACTION
         * =========================================================
         *
         * IMPORTANT:
         *
         * The database transaction must be committed BEFORE
         * rebuilding the Moodle course cache.
         *
         * Otherwise the cache may contain course-module IDs
         * created inside a transaction that is later rolled back.
         * =========================================================
         */

        $transaction->allow_commit();

        /*
         * =========================================================
         * STEP 11
         *
         * REBUILD COURSE CACHE
         * =========================================================
         *
         * Rebuild only after all Moodle records have been
         * successfully committed.
         * =========================================================
         */

        rebuild_course_cache(
            $course->id,
            true
        );

        /*
         * =========================================================
         * RETURN RESULT
         * =========================================================
         */

        return [

            /*
             * Course structure.
             */

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

            /*
             * Lesson activities.
             */

            'lessoncontentcmid' =>
                (int)$lessoncontent->id,

            'didyouknowcmid' =>
                (int)$didyouknow->id,

            /*
             * Quiz.
             */

            'quizid' =>
                (int)$quizresult['quizid'],

            'quizcmid' =>
                (int)$quizresult['cmid'],

            'quizcontextid' =>
                (int)$quizresult['contextid'],

            /*
             * Question Bank.
             */

            'questioncategoryid' =>
                (int)$questionresult['categoryid'],

            'questioncontextid' =>
                (int)$questionresult['contextid'],

            'questioncount' =>
                (int)$questionresult['questioncount'],

            'questionbankentryids' =>
                array_values(
                    array_map(
                        'intval',
                        $questionresult['questionbankentryids']
                    )
                ),

            'questionids' =>
                array_values(
                    array_map(
                        'intval',
                        $questionresult['questionids']
                    )
                ),

                        /*
             * Quiz attachment results.
             */

            'attachedquestionids' =>
                array_values(
                    array_map(
                        'intval',
                        $attachmentresult['attachedquestionids']
                    )
                ),

            'attachedcount' =>
                (int)$attachmentresult['attachedcount'],

            'slotcount' =>
                (int)$attachmentresult['slotcount'],

            'quizsumgrades' =>
                (float)$attachmentresult['sumgrades'],
                
            /*
             * Remaining lesson activities.
             */

            'activitiescmid' =>
                (int)$activities->id,

            'recapcmid' =>
                (int)$recap->id,
        ];
    }
}
