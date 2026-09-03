<?php

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

use context_module;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;
use mod_quiz\quiz_settings;

class set_quiz_attempt_limit extends external_api {

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
            'attempts' => new external_value(
                PARAM_INT,
                'Maximum attempts allowed'
            ),
        ]);
    }

    public static function execute(
        int $quizid,
        int $userid,
        int $attempts
    ): array {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'quizid' => $quizid,
                'userid' => $userid,
                'attempts' => $attempts,
            ]
        );

        $quizid = (int)$params['quizid'];
        $userid = (int)$params['userid'];
        $attempts = (int)$params['attempts'];

        if ($attempts < 1 || $attempts > 3) {
            throw new \invalid_parameter_exception(
                'Attempt limit must be between 1 and 3.'
            );
        }

        $quiz = $DB->get_record(
            'quiz',
            ['id' => $quizid],
            'id,course',
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

        $override = [
            'userid' => $userid,
            'attempts' => $attempts,
        ];

        if ($existing) {
            $override['id'] = (int)$existing->id;
        }

        $quizsettings = quiz_settings::create(
            $quizid
        );

        $manager =
            $quizsettings->get_override_manager();

        $overrideid = $manager->save_override(
            $override
        );

        $saved = $DB->get_record(
            'quiz_overrides',
            ['id' => $overrideid],
            '*',
            MUST_EXIST
        );

        return [
            'quizid' => $quizid,
            'userid' => $userid,
            'attempts' => (int)$saved->attempts,
            'overrideid' => (int)$overrideid,
            'created' => $existing ? 0 : 1,
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
                'Effective attempt limit'
            ),
            'overrideid' => new external_value(
                PARAM_INT,
                'Quiz override ID'
            ),
            'created' => new external_value(
                PARAM_INT,
                '1 if created, 0 if updated'
            ),
        ]);
    }
}
