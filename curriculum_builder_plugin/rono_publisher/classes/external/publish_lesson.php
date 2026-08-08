<?php
/**
 * External API for publishing a curriculum lesson.
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
                    'Did You Know page content, including Gamma embed HTML'
                ),

                'didyouknowdescription' => new external_value(
                    PARAM_RAW,
                    'Optional Did You Know activity description',
                    VALUE_DEFAULT,
                    ''
                ),

                /*
                 * Quiz fields are accepted now so that the external API
                 * contract does not need to change when Question Bank
                 * publishing is added.
                 *
                 * They are NOT processed by the current structural-test
                 * publisher.
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
                    'Question format: gift or xml',
                    VALUE_DEFAULT,
                    'gift'
                ),

                'quizcontent' => new external_value(
                    PARAM_RAW,
                    'GIFT or Moodle XML question content',
                    VALUE_DEFAULT,
                    ''
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
     * Current version publishes the Moodle course structure only.
     *
     * Question Bank import and Quiz creation will be connected after
     * the structure has been verified on Moodle 5.2.
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
         * ---------------------------------------------------------
         * STEP 1
         *
         * Validate all incoming Web Service parameters.
         * ---------------------------------------------------------
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
         * ---------------------------------------------------------
         * STEP 2
         *
         * Confirm target course exists.
         * ---------------------------------------------------------
         */

        $course = $DB->get_record(
            'course',
            ['id' => $params['courseid']],
            '*',
            MUST_EXIST
        );

        /*
         * ---------------------------------------------------------
         * STEP 3
         *
         * Validate Moodle course context.
         * ---------------------------------------------------------
         */

        $context = context_course::instance(
            $course->id
        );

        self::validate_context($context);

        /*
         * ---------------------------------------------------------
         * STEP 4
         *
         * Require Rono Publisher permission.
         * ---------------------------------------------------------
         */

        require_capability(
            'local/rono_publisher:publishlesson',
            $context
        );

        /*
         * ---------------------------------------------------------
         * STEP 5
         *
         * Call the internal Publisher service.
         *
         * The external API does not contain Moodle publishing
         * implementation details.
         * ---------------------------------------------------------
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
         * ---------------------------------------------------------
         * STEP 6
         *
         * Return Moodle identifiers to the Pipeline Engine.
         * ---------------------------------------------------------
         */

        return [
            'status' => 'success',

            'message' =>
                'Lesson structure published successfully. Quiz publishing is not enabled in this structural-test version.',

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