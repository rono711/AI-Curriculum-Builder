<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Ping
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

class ping extends external_api {

    /**
     * ======================================================
     * Parameters
     * ======================================================
     */

    public static function execute_parameters()

    : external_function_parameters {

        return new external_function_parameters([]);

    }

    /**
     * ======================================================
     * Execute
     * ======================================================
     */

    public static function execute(): array {

        self::validate_context(

            context_system::instance()

        );

        return [

            "status" => "SUCCESS",

            "message" => "PONG",

            "plugin" => "Rono Curriculum Builder",

            "timestamp" => time()

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

                "SUCCESS"

            ),

            "message" => new external_value(

                PARAM_TEXT,

                "PONG"

            ),

            "plugin" => new external_value(

                PARAM_TEXT,

                "Plugin"

            ),

            "timestamp" => new external_value(

                PARAM_INT,

                "Unix Timestamp"

            )

        ]);

    }

}