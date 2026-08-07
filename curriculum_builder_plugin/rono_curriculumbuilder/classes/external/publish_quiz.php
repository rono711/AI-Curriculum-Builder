<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Publish Quiz
 *
 * Version 4.0
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

use local_rono_curriculumbuilder\repository\quiz_repository;

class publish_quiz extends external_api {

    /**
     * Parameters
     */

    public static function execute_parameters() {

        return new external_function_parameters([

            "lesson_package_id" =>

                new external_value(

                    PARAM_TEXT,

                    "Lesson Package"

                ),

            "activity_type" =>

                new external_value(

                    PARAM_ALPHA,

                    "QUIZ"

                ),

            "courseid" =>

                new external_value(

                    PARAM_INT,

                    "Course"

                ),

            "section" =>

                new external_value(

                    PARAM_INT,

                    "Section"

                ),

            "title" =>

                new external_value(

                    PARAM_TEXT,

                    "Quiz"

                ),

            "description" =>

                new external_value(

                    PARAM_RAW,

                    "Description",

                    VALUE_DEFAULT,

                    ""

                ),

            "gift_file" =>

                new external_value(

                    PARAM_RAW,

                    "Absolute GIFT file"

                )

        ]);

    }

    /**
     * Execute
     */

    public static function execute(

        string $lessonpackageid,

        string $activitytype,

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $giftfile

    ) {

        self::validate_parameters(

            self::execute_parameters(),

            [

                "lesson_package_id"=>$lessonpackageid,

                "activity_type"=>$activitytype,

                "courseid"=>$courseid,

                "section"=>$section,

                "title"=>$title,

                "description"=>$description,

                "gift_file"=>$giftfile

            ]

        );

        self::validate_context(

            context_system::instance()

        );

        require_capability(

            "local/rono_curriculumbuilder:publish",

            context_system::instance()

        );

        $repository =

            new quiz_repository();

        return $repository->publish(

            $lessonpackageid,

            $courseid,

            $section,

            $title,

            $description,

            $giftfile

        );

    }

    /**
     * Returns
     */

    public static function execute_returns() {

        return new external_single_structure([

            "status" =>

                new external_value(

                    PARAM_TEXT,

                    "SUCCESS"

                ),

            "quizid" =>

                new external_value(

                    PARAM_INT,

                    "Quiz"

                ),

            "cmid" =>

                new external_value(

                    PARAM_INT,

                    "CMID"

                ),

            "url" =>

                new external_value(

                    PARAM_URL,

                    "Quiz URL"

                )

        ]);

    }

}