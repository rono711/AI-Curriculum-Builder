<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Publish Lesson
 *
 * Version 4.1
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');

use context_system;
use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class publish_lesson extends external_api {

    /**
     * ======================================================
     * Parameters
     * ======================================================
     */

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            "lesson_package_id" => new external_value(

                PARAM_TEXT,

                "Lesson Package ID"

            )

        ]);

    }

    /**
     * ======================================================
     * Execute
     * ======================================================
     */

    public static function execute(

        string $lessonpackageid

    ): array {

        self::validate_parameters(

            self::execute_parameters(),

            [

                "lesson_package_id" => $lessonpackageid

            ]

        );

        self::validate_context(

            context_system::instance()

        );

        require_capability(

            "local/rono_curriculumbuilder:publish",

            context_system::instance()

        );

        //
        // Publisher Engine owns the orchestration.
        // This endpoint simply confirms that the
        // plugin is ready to publish.
        //

        return [

            "status" => "SUCCESS",

            "lesson_package_id" => $lessonpackageid,

            "message" =>

                "Plugin ready. Publisher Engine controls lesson publishing."

        ];

    }

    /**
     * ======================================================
     * Returns
     * ======================================================
     */

    public static function execute_returns()

    : external_single_structure {

        return new external_single_structure([

            "status" => new external_value(

                PARAM_TEXT,

                "Status"

            ),

            "lesson_package_id" => new external_value(

                PARAM_TEXT,

                "Lesson Package ID"

            ),

            "message" => new external_value(

                PARAM_TEXT,

                "Result"

            )

        ]);

    }

}