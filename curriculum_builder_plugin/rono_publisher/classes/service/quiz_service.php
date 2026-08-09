<?php
/**
 * Quiz service for Rono Publisher.
 *
 * Creates Moodle Quiz activities for curriculum lessons.
 *
 * Current development stage:
 *
 * - Create empty Quiz activity.
 * - Place Quiz in the lesson subsection.
 * - Indent Quiz beneath the Lesson Content page.
 * - Return quiz ID, course-module ID, and module context ID.
 *
 * Question importing and question attachment are handled
 * separately and will be connected after Quiz creation is verified.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

use context_module;
use moodle_exception;
use stdClass;

/**
 * Service responsible for Moodle Quiz activities.
 */
class quiz_service {

    /**
     * Create an empty Moodle Quiz activity.
     *
     * The Quiz is created inside the delegated Moodle subsection
     * belonging to the curriculum sub-strand.
     *
     * It is visually indented beneath the main Lesson Content page.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection course section.
     * @param string $name Quiz activity name.
     * @param string $description Quiz activity description.
     * @param int $indent Course-page indentation level.
     * @return array
     */
    public function create_quiz(
        int $courseid,
        stdClass $section,
        string $name = 'Checking Your Thinking',
        string $description = '',
        int $indent = 1
    ): array {
        global $CFG, $DB;

        /*
         * Moodle course-module creation API.
         */
        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        /*
         * Quiz module library.
         */
        require_once(
            $CFG->dirroot . '/mod/quiz/lib.php'
        );

        $name = trim($name);

        if ($name === '') {
            $name = 'Checking Your Thinking';
        }

        if ($indent < 0) {
            $indent = 0;
        }

        /*
         * ---------------------------------------------------------
         * Validate course.
         * ---------------------------------------------------------
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
         * ---------------------------------------------------------
         * Locate Moodle Quiz module.
         * ---------------------------------------------------------
         */

        $module = $DB->get_record(
            'modules',
            [
                'name' => 'quiz',
            ],
            '*',
            MUST_EXIST
        );

        /*
         * ---------------------------------------------------------
         * Build Moodle module creation object.
         * ---------------------------------------------------------
         */

        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'quiz';

        $moduleinfo->module =
            (int)$module->id;

        $moduleinfo->course =
            (int)$course->id;

        /*
         * IMPORTANT:
         *
         * add_moduleinfo() expects the section NUMBER,
         * not the course_sections database ID.
         *
         * For Rono Publisher this is the delegated section
         * belonging to mod_subsection.
         */
        $moduleinfo->section =
            (int)$section->section;

        /*
         * Quiz name and introduction.
         */
        $moduleinfo->name =
            $name;

        $moduleinfo->intro =
            $description;

        $moduleinfo->introformat =
            FORMAT_HTML;

        /*
         * ---------------------------------------------------------
         * Basic Quiz settings.
         * ---------------------------------------------------------
         */

        // Quiz available immediately.
        $moduleinfo->timeopen = 0;

        // No closing date.
        $moduleinfo->timeclose = 0;

        // No time limit.
        $moduleinfo->timelimit = 0;

        // No grace period.
        $moduleinfo->overduehandling = 'autosubmit';

        $moduleinfo->graceperiod = 0;

        /*
         * Unlimited attempts.
         */
        $moduleinfo->attempts = 0;

        /*
         * Highest attempt grade.
         */
        $moduleinfo->grademethod =
            QUIZ_GRADEHIGHEST;

        /*
         * Maximum grade displayed in gradebook.
         *
         * Question marks will later contribute to sumgrades.
         */
        $moduleinfo->grade = 10;

        /*
         * Questions per page.
         *
         * 1 gives a clean student experience and Moodle can
         * repaginate later if required.
         */
        $moduleinfo->questionsperpage = 1;

        /*
         * Standard navigation.
         */
        $moduleinfo->navmethod = 'free';

        /*
         * Shuffle question order disabled initially.
         *
         * This can become a Publisher setting later.
         */
        $moduleinfo->shuffleanswers = 1;

        /*
         * Preferred question behaviour.
         */
        $moduleinfo->preferredbehaviour =
            'deferredfeedback';

        /*
         * ---------------------------------------------------------
         * Review options.
         * ---------------------------------------------------------
         *
         * Use Moodle's standard defaults suitable for an
         * automatically generated formative quiz.
         */

        $moduleinfo->attemptduring = 1;
        $moduleinfo->correctnessduring = 1;
        $moduleinfo->marksduring = 1;
        $moduleinfo->specificfeedbackduring = 1;
        $moduleinfo->generalfeedbackduring = 1;
        $moduleinfo->rightanswerduring = 1;
        $moduleinfo->overallfeedbackduring = 1;

        $moduleinfo->attemptimmediately = 1;
        $moduleinfo->correctnessimmediately = 1;
        $moduleinfo->marksimmediately = 1;
        $moduleinfo->specificfeedbackimmediately = 1;
        $moduleinfo->generalfeedbackimmediately = 1;
        $moduleinfo->rightanswerimmediately = 1;
        $moduleinfo->overallfeedbackimmediately = 1;

        $moduleinfo->attemptopen = 1;
        $moduleinfo->correctnessopen = 1;
        $moduleinfo->marksopen = 1;
        $moduleinfo->specificfeedbackopen = 1;
        $moduleinfo->generalfeedbackopen = 1;
        $moduleinfo->rightansweropen = 1;
        $moduleinfo->overallfeedbackopen = 1;

        $moduleinfo->attemptclosed = 1;
        $moduleinfo->correctnessclosed = 1;
        $moduleinfo->marksclosed = 1;
        $moduleinfo->specificfeedbackclosed = 1;
        $moduleinfo->generalfeedbackclosed = 1;
        $moduleinfo->rightanswerclosed = 1;
        $moduleinfo->overallfeedbackclosed = 1;

        /*
         * ---------------------------------------------------------
         * Display settings.
         * ---------------------------------------------------------
         */

        $moduleinfo->showuserpicture = 0;

        $moduleinfo->decimalpoints = 2;

        $moduleinfo->questiondecimalpoints = -1;

        $moduleinfo->showblocks = 0;

        /*
         * ---------------------------------------------------------
         * Password / network restrictions.
         * ---------------------------------------------------------
         */

        /*
 * Moodle's Quiz creation processing can convert an empty
 * password string to NULL. The quiz table requires a
 * non-null password value in this Moodle installation.
 *
 * Use a single space during programmatic creation.
 * We do not enable password-restricted access.
 */
        /*
 * Moodle Quiz uses "quizpassword" in the module form.
 *
 * quiz_add_instance() converts:
 *
 *     quizpassword -> password
 *
 * before writing the quiz record.
 *
 * Therefore we must supply quizpassword here rather than
 * setting the database field "password" directly.
 */
        $moduleinfo->quizpassword = '';

        $moduleinfo->subnet = '';

/*
 * No browser security restriction.
 */
        $moduleinfo->browsersecurity = '-';

        $moduleinfo->delay1 = 0;

        $moduleinfo->delay2 = 0;

        /*
         * ---------------------------------------------------------
         * Course module settings.
         * ---------------------------------------------------------
         */

        $moduleinfo->visible = 1;

        $moduleinfo->groupmode = 0;

        $moduleinfo->groupingid = 0;

        $moduleinfo->completion = 0;

        /*
         * ---------------------------------------------------------
         * Create Quiz using Moodle's standard module API.
         * ---------------------------------------------------------
         */

        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created) ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Moodle Quiz activity.'
            );
        }

        $cmid =
            (int)$created->coursemodule;

        /*
         * ---------------------------------------------------------
         * Retrieve course module.
         * ---------------------------------------------------------
         */

        $cm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * The instance field points to the quiz table.
         */
        $quizid =
            (int)$cm->instance;

        $quiz = $DB->get_record(
            'quiz',
            [
                'id' => $quizid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * ---------------------------------------------------------
         * Apply lesson indentation.
         * ---------------------------------------------------------
         */

        if ($indent > 0) {

            $DB->set_field(
                'course_modules',
                'indent',
                $indent,
                [
                    'id' => $cmid,
                ]
            );
        }

        /*
         * ---------------------------------------------------------
         * Obtain Quiz module context.
         * ---------------------------------------------------------
         *
         * This context will be passed to question_service
         * during the next development stage.
         */

        $context =
            context_module::instance(
                $cmid
            );
            

        /*
         * ---------------------------------------------------------
         * Rebuild course cache.
         * ---------------------------------------------------------
         */

        rebuild_course_cache(
            $course->id,
            true
        );

        /*
         * ---------------------------------------------------------
         * Return identifiers.
         * ---------------------------------------------------------
         */

        return [

            'quizid' =>
                $quizid,

            'cmid' =>
                $cmid,

            'contextid' =>
                (int)$context->id,

            'quiz' =>
                $quiz,

            'cm' =>
                $cm,

            'context' =>
                $context,
        ];
    }
        /**
     * Attach imported Question Bank questions to this Quiz.
     *
     * Moodle 5.2 provides:
     *
     * quiz_add_quiz_question(
     *     $questionid,
     *     $quiz,
     *     $page = 0,
     *     $maxmark = null
     * );
     *
     * @param int $quizid Moodle Quiz instance ID.
     * @param array $questionids Moodle question IDs.
     * @return array Attachment result.
     */
    public function attach_questions(
        int $quizid,
        array $questionids
    ): array {
        global $CFG, $DB;

        /*
         * Load Moodle Quiz APIs.
         */
        require_once(
            $CFG->dirroot . '/mod/quiz/lib.php'
        );

        require_once(
            $CFG->dirroot . '/mod/quiz/locallib.php'
        );

        /*
         * Load the Quiz.
         */
        $quiz = $DB->get_record(
            'quiz',
            [
                'id' => $quizid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Resolve the Quiz course module.
         */
        $cm = get_coursemodule_from_instance(
            'quiz',
            $quiz->id,
            $quiz->course,
            false,
            MUST_EXIST
        );

        /*
         * Moodle's quiz_add_quiz_question() expects an extended
         * Quiz object containing its CMID.
         */
        $quiz->cmid =
            (int)$cm->id;

        /*
         * Normalise supplied question IDs.
         */
        $questionids =
            array_values(
                array_unique(
                    array_map(
                        'intval',
                        $questionids
                    )
                )
            );

        /*
         * Remove invalid/non-positive IDs.
         */
        $validquestionids = [];

        foreach ($questionids as $questionid) {
            if ($questionid > 0) {
                $validquestionids[] =
                    $questionid;
            }
        }

        if (empty($validquestionids)) {
            throw new moodle_exception(
                'No valid Moodle question IDs were supplied for Quiz attachment.'
            );
        }

        /*
         * Attach each imported question.
         *
         * page = 0:
         * Moodle appends the question to the end of the Quiz.
         *
         * maxmark = null:
         * Moodle uses the question's default mark.
         */
        $attachedids = [];

        foreach ($validquestionids as $questionid) {

            /*
             * Confirm the question exists.
             */
            $DB->get_record(
                'question',
                [
                    'id' => $questionid,
                ],
                'id',
                MUST_EXIST
            );

            $added =
                quiz_add_quiz_question(
                    $questionid,
                    $quiz,
                    0,
                    null
                );

            /*
             * Moodle returns false when the same Question Bank
             * entry is already present in this Quiz.
             *
             * Do not treat that as a fatal error.
             */
            if ($added !== false) {
                $attachedids[] =
                    (int)$questionid;
            }
        }
        
                /*
         * ---------------------------------------------------------
         * Recalculate Quiz grades.
         * ---------------------------------------------------------
         *
         * Moodle 5.2's own mod/quiz/edit.php performs these
         * operations after adding questions:
         *
         *     quiz_delete_previews($quiz);
         *     $gradecalculator->recompute_quiz_sumgrades();
         *
         * Do the same here so the Quiz structure and total
         * marks are synchronised.
         */

        $quizobj =
            \mod_quiz\quiz_settings::create(
                $quiz->id
            );

        quiz_delete_previews(
            $quiz
        );

        $gradecalculator =
            $quizobj->get_grade_calculator();

        $gradecalculator->recompute_quiz_sumgrades();

        /*
         * Verify that Moodle created Quiz slots.
         */
        $slotcount =
            $DB->count_records(
                'quiz_slots',
                [
                    'quizid' =>
                        $quiz->id,
                ]
            );

        if ($slotcount <= 0) {
            throw new moodle_exception(
                'Question attachment completed but the Quiz contains no question slots.'
            );
        }

        /*
         * Reload the Quiz because quiz_add_quiz_question()
         * updates its structure/sumgrades.
         */
        $quiz =
            $DB->get_record(
                'quiz',
                [
                    'id' => $quizid,
                ],
                '*',
                MUST_EXIST
            );

        /*
         * Rebuild course cache.
         */
        rebuild_course_cache(
            $quiz->course,
            true
        );

        return [

            'quizid' =>
                (int)$quiz->id,

            'quizcmid' =>
                (int)$cm->id,

            'attachedquestionids' =>
                $attachedids,

            'attachedcount' =>
                count($attachedids),

            'slotcount' =>
                (int)$slotcount,

            'sumgrades' =>
                (float)$quiz->sumgrades,
        ];
    }
}