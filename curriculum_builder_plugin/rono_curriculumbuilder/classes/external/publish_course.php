<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Publish Course
 *
 * Version 5.0
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');
require_once($CFG->dirroot . '/course/lib.php');

use context_system;
use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class publish_course extends external_api {

    /**
     * ======================================================
     * Parameters
     * ======================================================
     */

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            "build_id" => new external_value(
                PARAM_TEXT,
                "Build ID"
            ),

            "lesson_package_id" => new external_value(
                PARAM_TEXT,
                "Lesson Package ID"
            ),

            "school_level" => new external_value(
                PARAM_TEXT,
                "School Level"
            ),

            "subject" => new external_value(
                PARAM_TEXT,
                "Subject"
            ),

            "year_level" => new external_value(
                PARAM_TEXT,
                "Year Level"
            )

        ]);

    }

    /**
     * ======================================================
     * Execute
     * ======================================================
     */

    public static function execute(

        string $buildid,
        string $lessonpackageid,
        string $schoollevel,
        string $subject,
        string $yearlevel

    ): array {

        global $DB;

        self::validate_parameters(

            self::execute_parameters(),

            [

                "build_id" => $buildid,

                "lesson_package_id" => $lessonpackageid,

                "school_level" => $schoollevel,

                "subject" => $subject,

                "year_level" => $yearlevel

            ]

        );

        self::validate_context(

            context_system::instance()

        );

        require_capability(

            "moodle/course:create",

            context_system::instance()

        );

        //
        // Course Name
        //

        $fullname =

            $subject

            . " - "

            . $yearlevel;

        $shortname = strtoupper(

            preg_replace(

                "/[^A-Za-z0-9]/",

                "",

                $subject

            )

        )

        . "_"

        .

        strtoupper(

            preg_replace(

                "/[^A-Za-z0-9]/",

                "",

                $yearlevel

            )

        );

        //
        // Existing Course?
        //

        $course = $DB->get_record(

            "course",

            [

                "shortname" => $shortname

            ]

        );

        if (!$course) {

            $record = new \stdClass();

            $record->fullname = $fullname;

            $record->shortname = $shortname;

            $record->category = self::get_category(

                $schoollevel,

                $subject,

                $yearlevel

            );

            $record->visible = 1;

            $course = create_course(

                $record

            );

        }

        return [

            "status" => "SUCCESS",

            "courseid" => $course->id,

            "fullname" => $course->fullname,

            "shortname" => $course->shortname,

            "build_id" => $buildid,

            "lesson_package_id" => $lessonpackageid

        ];

    }

    /**
     * ======================================================
     * Get / Create Category
     * ======================================================
     */

    protected static function get_category(

        string $schoollevel,

        string $subject,

        string $yearlevel

    ): int {

        global $DB;
                //
        // Root Category
        // (Manually created: Australian Curriculum)
        //

        $rootid = (int)get_config(

            "local_rono_curriculumbuilder",

            "defaultcoursecategory"

        );

        if ($rootid < 1) {

            throw new \moodle_exception(

                "Default Course Category has not been configured."

            );

        }

        $root = $DB->get_record(

            "course_categories",

            [

                "id" => $rootid

            ],

            "*",

            MUST_EXIST

        );

        //
        // ======================================================
        // School Level
        // ======================================================
        //

        $level = $DB->get_record(

            "course_categories",

            [

                "parent" => $root->id,

                "name" => $schoollevel

            ]

        );

        if (!$level) {

            $record = new \stdClass();

            $record->name = $schoollevel;

            $record->parent = $root->id;

            $level = \core_course_category::create(

                $record

            );

        }

        //
        // ======================================================
        // Subject
        // ======================================================
        //

        $area = $DB->get_record(

            "course_categories",

            [

                "parent" => $level->id,

                "name" => $subject

            ]

        );

        if (!$area) {

            $record = new \stdClass();

            $record->name = $subject;

            $record->parent = $level->id;

            $area = \core_course_category::create(

                $record

            );

        }

        //
        // ======================================================
        // Year Level
        // ======================================================
        //

        $year = $DB->get_record(

            "course_categories",

            [

                "parent" => $area->id,

                "name" => $yearlevel

            ]

        );

        if (!$year) {

            $record = new \stdClass();

            $record->name = $yearlevel;

            $record->parent = $area->id;

            $year = \core_course_category::create(

                $record

            );

        }

        return $year->id;

    }

    /**
     * ======================================================
     * Returns
     * ======================================================
     */
         public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            "status" => new external_value(

                PARAM_TEXT,

                "Status"

            ),

            "courseid" => new external_value(

                PARAM_INT,

                "Course ID"

            ),

            "fullname" => new external_value(

                PARAM_TEXT,

                "Course Full Name"

            ),

            "shortname" => new external_value(

                PARAM_TEXT,

                "Course Short Name"

            ),

            "build_id" => new external_value(

                PARAM_TEXT,

                "Build ID"

            ),

            "lesson_package_id" => new external_value(

                PARAM_TEXT,

                "Lesson Package ID"

            )

        ]);

    }

}