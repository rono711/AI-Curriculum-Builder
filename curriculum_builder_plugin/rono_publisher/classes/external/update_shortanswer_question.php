<?php
/**
 * Update one existing Moodle SHORTANSWER question.
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
use local_rono_publisher\service\question_service;

class update_shortanswer_question extends external_api {

    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'quizid' => new external_value(
                PARAM_INT,
                'Moodle Quiz instance ID'
            ),
            'slot' => new external_value(
                PARAM_INT,
                'Quiz slot number'
            ),
            'questionid' => new external_value(
                PARAM_INT,
                'Current Moodle question ID'
            ),
            'questionbankentryid' => new external_value(
                PARAM_INT,
                'Question Bank entry ID'
            ),
            'answers' => new external_multiple_structure(
                new external_single_structure([
                    'answer' => new external_value(
                        PARAM_RAW,
                        'Fully correct accepted answer'
                    ),
                ])
            ),
        ]);
    }

    public static function execute(
        int $quizid,
        int $slot,
        int $questionid,
        int $questionbankentryid,
        array $answers
    ): array {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'quizid' => $quizid,
                'slot' => $slot,
                'questionid' => $questionid,
                'questionbankentryid' =>
                    $questionbankentryid,
                'answers' => $answers,
            ]
        );

        $quiz = $DB->get_record(
            'quiz',
            [
                'id' => $params['quizid'],
            ],
            'id,course',
            MUST_EXIST
        );

        $context = context_course::instance(
            (int)$quiz->course
        );

        self::validate_context(
            $context
        );

        require_capability(
            'moodle/question:editall',
            $context
        );

        $service =
            new question_service();

        return $service->update_shortanswer_question(
            (int)$params['quizid'],
            (int)$params['slot'],
            (int)$params['questionid'],
            (int)$params['questionbankentryid'],
            array_map(
                static function(array $item): string {
                    return (string)$item['answer'];
                },
                $params['answers']
            )
        );
    }

    public static function execute_returns(): external_single_structure {
        return new external_single_structure([
            'status' => new external_value(
                PARAM_ALPHA,
                'Result status'
            ),
            'quizid' => new external_value(
                PARAM_INT,
                'Quiz ID'
            ),
            'slot' => new external_value(
                PARAM_INT,
                'Quiz slot'
            ),
            'questionbankentryid' => new external_value(
                PARAM_INT,
                'Question Bank entry ID'
            ),
            'oldquestionid' => new external_value(
                PARAM_INT,
                'Previous question ID'
            ),
            'newquestionid' => new external_value(
                PARAM_INT,
                'New question ID'
            ),
            'oldversion' => new external_value(
                PARAM_INT,
                'Previous question version'
            ),
            'newversion' => new external_value(
                PARAM_INT,
                'New question version'
            ),
            'answercount' => new external_value(
                PARAM_INT,
                'Accepted answer count'
            ),
            'referenceversion' => new external_value(
                PARAM_ALPHANUMEXT,
                'Quiz reference version'
            ),
        ]);
    }
}
