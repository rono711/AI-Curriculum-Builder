<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Update Moodle Page
 *
 * Version 4.1
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');

use context_module;
use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class update_page extends external_api {

    /**
     * ======================================================
     * Parameters
     * ======================================================
     */

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            "pageid" => new external_value(
                PARAM_INT,
                "Page ID"
            ),

            "title" => new external_value(
                PARAM_TEXT,
                "Page Title"
            ),

            "description" => new external_value(
                PARAM_RAW,
                "Description",
                VALUE_DEFAULT,
                ""
            ),

            "content" => new external_value(
                PARAM_RAW,
                "HTML Content"
            )

        ]);

    }

    /**
     * ======================================================
     * Execute
     * ======================================================
     */

    public static function execute(

        int $pageid,

        string $title,

        string $description,

        string $content

    ): array {

        global $DB;

        self::validate_parameters(

            self::execute_parameters(),

            [

                "pageid"=>$pageid,

                "title"=>$title,

                "description"=>$description,

                "content"=>$content

            ]

        );

        $page = $DB->get_record(

            "page",

            [

                "id"=>$pageid

            ],

            "*",

            MUST_EXIST

        );

        $cm = get_coursemodule_from_instance(

            "page",

            $pageid,

            $page->course,

            false,

            MUST_EXIST

        );

        $context = context_module::instance(

            $cm->id

        );

        self::validate_context(

            $context

        );

        require_capability(

            "moodle/course:update",

            $context

        );

        //
        // Update
        //

        $page->name = $title;

        //
        // Only overwrite
        // description if supplied.
        //

        if (

            trim($description)

            != ""

        ) {

            $page->intro = $description;

            $page->introformat = FORMAT_HTML;

            $page->showdescription = 1;

        }

        $page->content = $content;

        $page->contentformat = FORMAT_HTML;

        $page->timemodified = time();

        $DB->update_record(

        "page",

        $page

       );

//
// Show description on course page
//

           $cm->showdescription = 1;

            $DB->update_record(

            "course_modules",

             $cm

            );

        rebuild_course_cache(

            $page->course,

            true

        );

        return [

            "status"=>"SUCCESS",

            "pageid"=>$page->id,

            "cmid"=>$cm->id,

            "url"=>

                (new \moodle_url(

                    "/mod/page/view.php",

                    [

                        "id"=>$cm->id

                    ]

                ))->out(false)

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

        "status"=>new external_value(

            PARAM_TEXT,

            "SUCCESS"

        ),

        "pageid"=>new external_value(

            PARAM_INT,

            "Page"

        ),

        "cmid"=>new external_value(

            PARAM_INT,

            "CMID"

        ),

        "url"=>new external_value(

            PARAM_URL,

            "URL"

        )

    ]);

  }
}