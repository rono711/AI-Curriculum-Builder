<?php
/**
 * Read-only external API for Quiz question mappings.
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

class get_quiz_questions extends external_api {

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([
            'quizid' => new external_value(
                PARAM_INT,
                'Moodle Quiz instance ID'
            ),
        ]);
    }

    public static function execute(
        int $quizid
    ): array {
        global $DB;

        $params =
            self::validate_parameters(
                self::execute_parameters(),
                [
                    'quizid' => $quizid,
                ]
            );

        $quiz =
            $DB->get_record(
                'quiz',
                [
                    'id' => $params['quizid'],
                ],
                'id,course',
                MUST_EXIST
            );

        $context =
            context_course::instance(
                (int)$quiz->course
            );

        self::validate_context(
            $context
        );

        require_capability(
            'local/rono_publisher:viewanalytics',
            $context
        );

        $service =
            new question_service();

        return $service->get_quiz_questions(
            (int)$quiz->id
        );
    }

    public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            'quizid' =>
                new external_value(
                    PARAM_INT,
                    'Moodle Quiz instance ID'
                ),

            'courseid' =>
                new external_value(
                    PARAM_INT,
                    'Moodle course ID'
                ),

            'questioncount' =>
                new external_value(
                    PARAM_INT,
                    'Number of Quiz questions'
                ),

            'questions' =>
                new external_multiple_structure(
                    new external_single_structure([

                        'slot' =>
                            new external_value(
                                PARAM_INT,
                                'Quiz slot number'
                            ),

                        'questionid' =>
                            new external_value(
                                PARAM_INT,
                                'Moodle question ID'
                            ),

                        'questionbankentryid' =>
                            new external_value(
                                PARAM_INT,
                                'Question Bank entry ID'
                            ),

                        'questionname' =>
                            new external_value(
                                PARAM_RAW,
                                'Question name'
                            ),

                        'qtype' =>
                            new external_value(
                                PARAM_ALPHANUMEXT,
                                'Question type'
                            ),

                        'questiontext' =>
                            new external_value(
                                PARAM_RAW,
                                'Question text'
                            ),
                    ])
                ),
        ]);
    }
}

