<?php
/**
 * External API for publishing a curriculum lesson.
 *
 * Current development stage:
 *
 * - Course structure publishing: enabled.
 * - Question Bank import: enabled for testing.
 * - Quiz activity creation: not yet enabled.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

use context_course;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_multiple_structure;
use core_external\external_single_structure;
use core_external\external_value;
use local_rono_publisher\service\publisher;

/**
 * External function for publishing one curriculum lesson.
 */
class publish_lesson extends external_api {

    /**
     * Define external function parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            'courseid' => new external_value(
                PARAM_INT,
                'Target Moodle course ID'
            ),

            'strand' => new external_value(
                PARAM_TEXT,
                'Curriculum strand used as the Moodle section title'
            ),

            'substrand' => new external_value(
                PARAM_TEXT,
                'Curriculum sub-strand used as the Moodle subsection title'
            ),

            'contentdescription' => new external_value(
                PARAM_RAW,
                'Curriculum content description displayed as Text and Media'
            ),

            'lesson' => new external_single_structure([

                'title' => new external_value(
                    PARAM_TEXT,
                    'Lesson or elaboration title'
                ),

                'lessoncontent' => new external_value(
                    PARAM_RAW,
                    'Lesson Content / Mission of the Day HTML'
                ),

                'lessondescription' => new external_value(
                    PARAM_RAW,
                    'Optional Lesson Content activity description',
                    VALUE_DEFAULT,
                    ''
                ),

                'didyouknow' => new external_value(
                    PARAM_RAW,
                    'Did You Know page content including Gamma embed HTML'
                ),

                'didyouknowdescription' => new external_value(
                    PARAM_RAW,
                    'Optional Did You Know activity description',
                    VALUE_DEFAULT,
                    ''
                ),

                /*
                 * Question Bank / Quiz data.
                 *
                 * During this development stage quizcontent is imported
                 * into the Question Bank, but no Quiz activity is created.
                 */

                'quiztitle' => new external_value(
                    PARAM_TEXT,
                    'Quiz activity title',
                    VALUE_DEFAULT,
                    'Checking Your Thinking'
                ),

                'quizdescription' => new external_value(
                    PARAM_RAW,
                    'Quiz activity description',
                    VALUE_DEFAULT,
                    ''
                ),

                'quizformat' => new external_value(
                    PARAM_ALPHA,
                    'Question import format: gift or xml',
                    VALUE_DEFAULT,
                    'gift'
                ),

                'quizcontent' => new external_value(
                    PARAM_RAW,
                    'GIFT or Moodle XML question content'
                ),

                'activities' => new external_value(
                    PARAM_RAW,
                    'Lets Do It page HTML'
                ),

                'activitiesdescription' => new external_value(
                    PARAM_RAW,
                    'Optional Lets Do It activity description',
                    VALUE_DEFAULT,
                    ''
                ),

                'recap' => new external_value(
                    PARAM_RAW,
                    'What We Discovered page HTML'
                ),

                'recapdescription' => new external_value(
                    PARAM_RAW,
                    'Optional recap activity description',
                    VALUE_DEFAULT,
                    ''
                ),
            ]),
        ]);
    }

    /**
     * Publish one curriculum lesson.
     *
     * Current version:
     *
     * 1. Publishes course structure.
     * 2. Creates/fetches lesson Question Bank category.
     * 3. Imports GIFT/XML questions.
     * 4. Does NOT create the Quiz activity yet.
     *
     * @param int $courseid
     * @param string $strand
     * @param string $substrand
     * @param string $contentdescription
     * @param array $lesson
     * @return array
     */
    public static function execute(
        int $courseid,
        string $strand,
        string $substrand,
        string $contentdescription,
        array $lesson
    ): array {
        global $DB;

        /*
         * =========================================================
         * STEP 1
         *
         * Validate Web Service parameters.
         * =========================================================
         */

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'strand' => $strand,
                'substrand' => $substrand,
                'contentdescription' => $contentdescription,
                'lesson' => $lesson,
            ]
        );

        /*
         * =========================================================
         * STEP 2
         *
         * Confirm target Moodle course exists.
         * =========================================================
         */

        $course = $DB->get_record(
            'course',
            [
                'id' => $params['courseid'],
            ],
            '*',
            MUST_EXIST
        );

        /*
         * =========================================================
         * STEP 3
         *
         * Validate course context.
         * =========================================================
         */

        $context = context_course::instance(
            $course->id
        );

        self::validate_context(
            $context
        );

        /*
         * =========================================================
         * STEP 4
         *
         * Require Rono Publisher capability.
         * =========================================================
         */

        require_capability(
            'local/rono_publisher:publishlesson',
            $context
        );

        /*
         * =========================================================
         * STEP 5
         *
         * Run internal publisher.
         * =========================================================
         */

        $publisher = new publisher();

        $result = $publisher->publish_structure(
            (int)$course->id,
            $params['strand'],
            $params['substrand'],
            $params['contentdescription'],
            $params['lesson']
        );

        /*
         * =========================================================
         * STEP 6
         *
         * Return structure + Question Bank results.
         * =========================================================
         */

        return [

            'status' =>
                'success',

            'message' =>
                'Lesson structure and Question Bank questions published successfully. Quiz activity creation is not yet enabled.',

            'courseid' =>
                (int)$result['courseid'],

            'strandsectionid' =>
                (int)$result['strandsectionid'],

            'subsectioncmid' =>
                (int)$result['subsectioncmid'],

            'subsectionsectionid' =>
                (int)$result['subsectionsectionid'],

            'contentdescriptioncmid' =>
                (int)$result['contentdescriptioncmid'],

            'lessoncontentcmid' =>
                (int)$result['lessoncontentcmid'],

            'didyouknowcmid' =>
                (int)$result['didyouknowcmid'],

            /*
             * Question Bank results.
             */

            'questioncategoryid' =>
                (int)$result['questioncategoryid'],

            'questioncount' =>
                (int)$result['questioncount'],

            'questionbankentryids' =>
                array_values(
                    array_map(
                        'intval',
                        $result['questionbankentryids']
                    )
                ),

            'activitiescmid' =>
                (int)$result['activitiescmid'],

            'recapcmid' =>
                (int)$result['recapcmid'],
        ];
    }

    /**
     * Define external function return structure.
     *
     * @return external_single_structure
     */
    public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            'status' => new external_value(
                PARAM_TEXT,
                'Publishing status'
            ),

            'message' => new external_value(
                PARAM_TEXT,
                'Publishing result message'
            ),

            'courseid' => new external_value(
                PARAM_INT,
                'Target Moodle course ID'
            ),

            'strandsectionid' => new external_value(
                PARAM_INT,
                'Moodle course section ID for the curriculum strand'
            ),

            'subsectioncmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Moodle subsection'
            ),

            'subsectionsectionid' => new external_value(
                PARAM_INT,
                'Delegated course section ID belonging to the subsection'
            ),

            'contentdescriptioncmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Content Description Text and Media activity'
            ),

            'lessoncontentcmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Lesson Content page'
            ),

            'didyouknowcmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Did You Know page'
            ),

            /*
             * Question Bank return values.
             */

            'questioncategoryid' => new external_value(
                PARAM_INT,
                'Question Bank category ID for this lesson'
            ),

            'questioncount' => new external_value(
                PARAM_INT,
                'Number of Question Bank entries imported'
            ),

            'questionbankentryids' =>
                new external_multiple_structure(
                    new external_value(
                        PARAM_INT,
                        'Question Bank entry ID'
                    )
                ),

            'activitiescmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Lets Do It page'
            ),

            'recapcmid' => new external_value(
                PARAM_INT,
                'Course module ID of the What We Discovered page'
            ),
        ]);
    }
}