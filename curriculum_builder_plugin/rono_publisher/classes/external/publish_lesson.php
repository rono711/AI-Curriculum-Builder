<?php
/**
 * External API for publishing a curriculum lesson.
 *
 * Current development stage:
 *
 * - Course structure publishing: enabled.
 * - Quiz activity creation: enabled.
 * - Question Bank import into Quiz module context: enabled.
 * - Question attachment to Quiz: not yet enabled.
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

            'curriculumcode' => new external_value(
                PARAM_TEXT,
                'Lesson curriculum/elaboration code'
            ),

            'elaboration' => new external_value(
                PARAM_RAW,
                'Curriculum elaboration for this lesson'
            ),

            'contentdescription' => new external_value(
                PARAM_RAW,
                'Curriculum content description displayed as Text and Media'
            ),
            'parentcode' => new external_value(
                PARAM_TEXT,
                'Parent curriculum Content Description code'
            ),

            'contentdescriptionimagename' => new external_value(
                PARAM_FILE,
                'Generated Content Description image filename'
            ),

            'contentdescriptionimage' => new external_value(
                PARAM_RAW,
                'Base64 encoded generated Content Description image'
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
     * Current sequence:
     *
     * 1. Strand Section.
     * 2. Sub-strand Subsection.
     * 3. Content Description.
     * 4. Lesson Content.
     * 5. Did You Know?
     * 6. Checking Your Thinking Quiz.
     * 7. Question Bank category in Quiz module context.
     * 8. GIFT/XML question import.
     * 9. Let's Do It.
     * 10. What We Discovered.
     *
     * Imported questions are NOT attached to the Quiz yet.
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
         * VALIDATE PARAMETERS
         * =========================================================
         */

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'strand' => $strand,
                'substrand' => $substrand,
                'curriculumcode' => $curriculumcode,
                'elaboration' => $elaboration,
                'contentdescription' => $contentdescription,
                'parentcode' => $parentcode,
                'contentdescriptionimagename' =>
                    $contentdescriptionimagename,
                'contentdescriptionimage' =>
                    $contentdescriptionimage,
                'lesson' => $lesson,
            ]
        );

        /*
         * =========================================================
         * VERIFY COURSE
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
         * VALIDATE COURSE CONTEXT
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
         * REQUIRE PUBLISHING CAPABILITY
         * =========================================================
         */

        require_capability(
            'local/rono_publisher:publishlesson',
            $context
        );

        /*
         * =========================================================
         * RUN INTERNAL PUBLISHER
         * =========================================================
         */

        $publisher =
            new publisher();

        $result =
            $publisher->publish_structure(
                (int)$course->id,
                $params['strand'],
                $params['substrand'],
                $params['curriculumcode'],
                $params['elaboration'],
                $params['contentdescription'],
                $params['parentcode'],
                $params['contentdescriptionimagename'],
                $params['contentdescriptionimage'],
                $params['lesson']
            );

        /*
         * =========================================================
         * RETURN RESULT
         * =========================================================
         */

        return [

            'status' =>
                'success',

            'message' =>
                'Lesson structure, Quiz activity, Question Bank questions and Quiz question slots published successfully.',
            /*
             * Course.
             */

            'courseid' =>
                (int)$result['courseid'],

            /*
             * Curriculum structure.
             */

            'strandsectionid' =>
                (int)$result['strandsectionid'],

            'subsectioncmid' =>
                (int)$result['subsectioncmid'],

            'subsectionsectionid' =>
                (int)$result['subsectionsectionid'],

            'contentdescriptioncmid' =>
                (int)$result['contentdescriptioncmid'],

            /*
             * Lesson.
             */

            'lessoncontentcmid' =>
                (int)$result['lessoncontentcmid'],

            'didyouknowcmid' =>
                (int)$result['didyouknowcmid'],

            /*
             * Quiz.
             */

            'quizid' =>
                (int)$result['quizid'],

            'quizcmid' =>
                (int)$result['quizcmid'],

            'quizcontextid' =>
                (int)$result['quizcontextid'],

            /*
             * Question Bank.
             */

            'questioncategoryid' =>
                (int)$result['questioncategoryid'],

            'questioncontextid' =>
                (int)$result['questioncontextid'],

            'questioncount' =>
                (int)$result['questioncount'],

            'questionbankentryids' =>
                array_values(
                    array_map(
                        'intval',
                        $result['questionbankentryids']
                    )
                ),

            'questionids' =>
                array_values(
                    array_map(
                        'intval',
                        $result['questionids']
                    )
                ),
            /*
 * Quiz question attachment.
 */

'attachedquestionids' =>
    array_values(
        array_map(
            'intval',
            $result['attachedquestionids']
        )
    ),

'attachedcount' =>
    (int)$result['attachedcount'],

'slotcount' =>
    (int)$result['slotcount'],

'quizsumgrades' =>
    (float)$result['quizsumgrades'],    

            /*
             * Remaining lesson activities.
             */

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

            /*
             * Course.
             */

            'courseid' => new external_value(
                PARAM_INT,
                'Target Moodle course ID'
            ),

            /*
             * Curriculum structure.
             */

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

            /*
             * Lesson.
             */

            'lessoncontentcmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Lesson Content page'
            ),

            'didyouknowcmid' => new external_value(
                PARAM_INT,
                'Course module ID of the Did You Know page'
            ),

            /*
             * Quiz.
             */

            'quizid' => new external_value(
                PARAM_INT,
                'Moodle Quiz instance ID'
            ),

            'quizcmid' => new external_value(
                PARAM_INT,
                'Moodle Quiz course module ID'
            ),

            'quizcontextid' => new external_value(
                PARAM_INT,
                'Moodle module context ID belonging to the Quiz'
            ),

            /*
             * Question Bank.
             */

            'questioncategoryid' => new external_value(
                PARAM_INT,
                'Question Bank category ID belonging to this lesson'
            ),

            'questioncontextid' => new external_value(
                PARAM_INT,
                'Question Bank module context ID'
            ),

            'questioncount' => new external_value(
                PARAM_INT,
                'Number of imported Question Bank entries'
            ),

            'questionbankentryids' =>
                new external_multiple_structure(
                    new external_value(
                        PARAM_INT,
                        'Question Bank entry ID'
                    )
                ),

            'questionids' =>
                new external_multiple_structure(
                    new external_value(
                        PARAM_INT,
                        'Latest imported Moodle question ID'
                    )
                ),
        /*
 * Quiz question attachment.
 */

'attachedquestionids' =>
    new external_multiple_structure(
        new external_value(
            PARAM_INT,
            'Moodle question ID attached to the Quiz'
        )
    ),

'attachedcount' =>
    new external_value(
        PARAM_INT,
        'Number of questions attached during this publishing operation'
    ),

'slotcount' =>
    new external_value(
        PARAM_INT,
        'Total number of question slots in the Quiz'
    ),

'quizsumgrades' =>
    new external_value(
        PARAM_FLOAT,
        'Total raw marks available from the questions in the Quiz'
    ),
            /*
             * Remaining lesson activities.
             */

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
