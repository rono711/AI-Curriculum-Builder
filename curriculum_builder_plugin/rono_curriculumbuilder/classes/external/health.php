<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Health Check
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

class health extends external_api {

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

        global $DB,$CFG;

        self::validate_context(

            context_system::instance()

        );

        $database = true;

        try {

            $DB->count_records(

                "course"

            );

        }

        catch (\Throwable $e) {

            $database = false;

        }

        return [

            "status" =>

                $database

                ? "SUCCESS"

                : "FAILED",

            "plugin" =>

                "Rono Curriculum Builder",

            "plugin_version" =>

                get_config(

                    "local_rono_curriculumbuilder",

                    "version"

                )

                ?? "4.1",

            "moodle_version" =>

                $CFG->release,

            "database" =>

                $database,

            "php_version" =>

                PHP_VERSION,

            "server_time" =>

                date(

                    "Y-m-d H:i:s"

                )

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

            "status" =>

                new external_value(

                    PARAM_TEXT,

                    "SUCCESS"

                ),

            "plugin" =>

                new external_value(

                    PARAM_TEXT,

                    "Plugin"

                ),

            "plugin_version" =>

                new external_value(

                    PARAM_TEXT,

                    "Plugin Version"

                ),

            "moodle_version" =>

                 new external_value(

                    PARAM_TEXT,

                  "Moodle Version"

                 ),

            "database" =>

                new external_value(

                    PARAM_BOOL,

                    "Database"

                ),

            "php_version" =>

                new external_value(

                    PARAM_TEXT,

                    "PHP"

                ),

            "server_time" =>

                new external_value(

                    PARAM_TEXT,

                    "Server Time"

                )

        ]);

    }

}