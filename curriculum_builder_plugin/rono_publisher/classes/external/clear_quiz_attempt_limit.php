<?php

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

use context_module;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;
use mod_quiz\quiz_settings;

class clear_quiz_attempt_limit extends external_api {

    public static function execute_parameters():
        external_function_parameters {

        return new external_function_parameters([
            'quizid' => new external_value(
                PARAM_INT,
                'Moodle Quiz instance ID'
            ),
            'userid' => new external_value(
                PARAM_INT,
                'Moodle user ID'
            ),
        ]);
    }

    public static function execute(
        int $quizid,
        int $userid
    ): array {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'quizid' => $quizid,
                'userid' => $userid,
            ]
        );

        $quizid = (int)$params['quizid'];
        $userid = (int)$params['userid'];

        $quiz = $DB->get_record(
            'quiz',
            ['id' => $quizid],
            'id,course,attempts',
            MUST_EXIST
        );

        $cm = get_coursemodule_from_instance(
            'quiz',
            $quizid,
            (int)$quiz->course,
            false,
            MUST_EXIST
        );

        $context = context_module::instance(
            (int)$cm->id
        );

        self::validate_context($context);

        require_capability(
            'local/rono_publisher:viewanalytics',
            $context
        );

        if (!$DB->record_exists(
            'user',
            [
                'id' => $userid,
                'deleted' => 0,
            ]
        )) {
            throw new \invalid_parameter_exception(
                'Invalid Moodle user ID.'
            );
        }

        $existing = $DB->get_record(
            'quiz_overrides',
            [
                'quiz' => $quizid,
                'userid' => $userid,
                'groupid' => null,
            ],
            '*',
            IGNORE_MISSING
        );

        $deleted = 0;

        if ($existing) {
            $quizsettings = quiz_settings::create(
                $quizid
            );

            $manager =
                $quizsettings->get_override_manager();

            $manager->delete_overrides_by_id(
               [(int)$existing->id]
            );

            $deleted = 1;
        }

        return [
            'quizid' => $quizid,
            'userid' => $userid,
            'attempts' => (int)$quiz->attempts,
            'deleted' => $deleted,
        ];
    }

    public static function execute_returns():
        external_single_structure {

        return new external_single_structure([
            'quizid' => new external_value(
                PARAM_INT,
                'Moodle Quiz instance ID'
            ),
            'userid' => new external_value(
                PARAM_INT,
                'Moodle user ID'
            ),
            'attempts' => new external_value(
                PARAM_INT,
                'Quiz default attempt limit after override removal'
            ),
            'deleted' => new external_value(
                PARAM_INT,
                '1 if an override was removed, otherwise 0'
            ),
        ]);
    }
}
