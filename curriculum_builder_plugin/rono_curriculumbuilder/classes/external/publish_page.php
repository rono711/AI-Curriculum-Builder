<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Publish Page Web Service
 *
 * Version 4.0
 *
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

use local_rono_curriculumbuilder\repository\page_repository;

/**
 * ============================================================================
 * Publish Page
 * ============================================================================
 */
class publish_page extends external_api {

    /**
     * ======================================================
     * Parameters
     * ======================================================
     */

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            'lesson_package_id' => new external_value(

                PARAM_TEXT,

                'Lesson Package ID'

            ),

            'activity_type' => new external_value(

               PARAM_ALPHANUMEXT,

               'Activity Type'

            ),

               'courseid' => new external_value(

                 PARAM_INT,

                 'Course ID'

),
            'section' => new external_value(

                PARAM_INT,

                'Course Section Number'

            ),

            'title' => new external_value(

                PARAM_TEXT,

                'Page Title'

            ),

            'description' => new external_value(

                PARAM_RAW,

                'Activity Description',

                VALUE_DEFAULT,

                ''

            ),

            'content' => new external_value(

                PARAM_RAW,

                'HTML Content'

            )

        ]);

    }

    /**
     * ======================================================
     * Execute
     * ======================================================
     */

    public static function execute(

        string $lesson_package_id,

        string $activity_type,

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $content

    ): array {

        self::validate_parameters(

            self::execute_parameters(),

            [

                'lesson_package_id' => $lesson_package_id,

                'activity_type' => $activity_type,

                'courseid' => $courseid,

                'section' => $section,

                'title' => $title,

                'description' => $description,

                'content' => $content

            ]

        );

        self::validate_context(

            context_system::instance()

        );

        require_capability(

            'local/rono_curriculumbuilder:publish',

            context_system::instance()

        );

        $repository = new page_repository();

        return $repository->publish(

            $lesson_package_id,

            $activity_type,

            $courseid,

            $section,

            $title,

            $description,

            $content

        );

    }

    /**
     * ======================================================
     * Returns
     * ======================================================
     */

    public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            'status' => new external_value(

                PARAM_TEXT,

                'SUCCESS'

            ),

            'pageid' => new external_value(

                PARAM_INT,

                'Page ID'

            ),

            'cmid' => new external_value(

                PARAM_INT,

                'Course Module ID'

            ),

            'url' => new external_value(

                PARAM_URL,

                'Activity URL'

            )

        ]);

    }

}