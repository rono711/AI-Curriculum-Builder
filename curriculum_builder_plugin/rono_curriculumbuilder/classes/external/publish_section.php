<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Publish Section
 *
 * Version 4.2
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');
require_once($CFG->dirroot . '/course/lib.php');

use context_course;
use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class publish_section extends external_api {

    /**
     * Parameters
     */
    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            "courseid" => new external_value(
                PARAM_INT,
                "Course ID"
            ),

            "strand" => new external_value(
                PARAM_TEXT,
                "Strand"
            ),

            "sub_strand" => new external_value(
                PARAM_TEXT,
                "Sub-Strand",
                VALUE_DEFAULT,
                ""
            )

        ]);

    }

    /**
     * Execute
     */
    public static function execute(

        int $courseid,

        string $strand,

        string $substrand

    ): array {

        global $DB;

        self::validate_parameters(

            self::execute_parameters(),

            [

                "courseid"=>$courseid,

                "strand"=>$strand,

                "sub_strand"=>$substrand

            ]

        );

        $context = context_course::instance(

            $courseid

        );

        self::validate_context(

            $context

        );

        require_capability(

            "moodle/course:update",

            $context

        );

        //
        // Existing Sections
        //

        $sections = $DB->get_records(

            "course_sections",

            [

                "course"=>$courseid

            ],

            "section ASC"

        );

        foreach ($sections as $section) {

            if (

                trim($section->name)

                ===

                trim($strand)

            ) {

                return [

                    "status"=>"SUCCESS",

                    "sectionid"=>$section->id,

                    "section"=>$section->section,

                    "name"=>$section->name

                ];

            }

        }

        //
        // Create new Moodle section
        //

        $sectionnumber = count($sections);

        course_create_section(

            $courseid,

            $sectionnumber

        );

        $newsection = $DB->get_record(

            "course_sections",

            [

                "course"=>$courseid,

                "section"=>$sectionnumber

            ],

            "*",

            MUST_EXIST

        );

        $newsection->name = trim($strand);

        //
        // Summary
        //

        $summary =

            "<h3>"

            .

            htmlspecialchars($strand)

            .

            "</h3>";

        if (

            trim($substrand)

            !== ""

        ) {

            $summary .=

                "<p><strong>Sub-strand:</strong> "

                .

                htmlspecialchars($substrand)

                .

                "</p>";

        }

        $newsection->summary = $summary;

        $newsection->summaryformat = FORMAT_HTML;

        $DB->update_record(

            "course_sections",

            $newsection

        );

        rebuild_course_cache(

            $courseid,

            true

        );

        return [

            "status"=>"SUCCESS",

            "sectionid"=>$newsection->id,

            "section"=>$newsection->section,

            "name"=>$newsection->name

        ];

    }

    /**
     * Returns
     */
    public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            "status" => new external_value(
                PARAM_TEXT,
                "SUCCESS"
            ),

            "sectionid" => new external_value(
                PARAM_INT,
                "Section ID"
            ),

            "section" => new external_value(
                PARAM_INT,
                "Section Number"
            ),

            "name" => new external_value(
                PARAM_TEXT,
                "Section Name"
            )

        ]);

    }

}