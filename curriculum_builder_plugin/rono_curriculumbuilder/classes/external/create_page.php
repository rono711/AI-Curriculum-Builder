<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Create Moodle Page
 *
 * Moodle 5.2 Compatible
 * Version 5.0
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\external;

defined('MOODLE_INTERNAL') || die();

global $CFG;

require_once($CFG->libdir . '/externallib.php');
require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/course/lib.php');
require_once($CFG->dirroot . '/mod/page/lib.php');

use context_course;
use external_api;
use external_function_parameters;
use external_single_structure;
use external_value;

class create_page extends external_api {

    /**
     * Parameters
     */
    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            'courseid' => new external_value(
                PARAM_INT,
                'Course ID'
            ),

            'section' => new external_value(
                PARAM_INT,
                'Section Number'
            ),

            'title' => new external_value(
                PARAM_TEXT,
                'Page Title'
            ),

            'description' => new external_value(
                PARAM_RAW,
                'Description',
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
     * Execute
     */
    public static function execute(

        int $courseid,
        int $section,
        string $title,
        string $description,
        string $content

    ): array {

        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'section' => $section,
                'title' => $title,
                'description' => $description,
                'content' => $content
            ]
        );

        $context = context_course::instance($params['courseid']);

        self::validate_context($context);

        require_capability(
            'moodle/course:manageactivities',
            $context
        );

        // Activity creation begins here.
                //
        // Load course.
        //
        $course = get_course($params['courseid']);

        if (!$course) {
            throw new \moodle_exception('invalidcourseid');
        }

        //
        // Find the requested course section.
        //
        $coursesection = $DB->get_record(
            'course_sections',
            [
                'course' => $params['courseid'],
                'section' => $params['section']
            ],
            '*',
            MUST_EXIST
        );

        //
        // Build the module data.
        //
        $moduledata = new \stdClass();

        $moduledata->modulename = 'page';

        $moduledata->course = $params['courseid'];

        $moduledata->section = $coursesection->section;

        $moduledata->name = trim($params['title']);

        $moduledata->intro = $params['description'];

        $moduledata->introformat = FORMAT_HTML;

        $moduledata->showdescription = 1;

        $moduledata->content = $params['content'];

        $moduledata->contentformat = FORMAT_HTML;

        //
        // Display settings
        //
        $moduledata->display = 5;

        $moduledata->displayoptions = serialize([]);

        $moduledata->printintro = 0;

        $moduledata->printlastmodified = 0;

        //
        // General activity settings
        //
        $moduledata->visible = 1;

        $moduledata->groupmode = NOGROUPS;

        $moduledata->groupingid = 0;

        $moduledata->completion = COMPLETION_TRACKING_NONE;

        $moduledata->completionview = 0;

        $moduledata->completionexpected = 0;

        $moduledata->availability = null;

        $moduledata->tags = [];

        $transaction = $DB->start_delegated_transaction();

try {

    //
    // Create Page instance.
    //
    $page = new \stdClass();

    $page->course = $params['courseid'];
    $page->name = trim($params['title']);
    $page->intro = $params['description'];
    $page->introformat = FORMAT_HTML;
    $page->showdescription = 1;
    $page->content = $params['content'];
    $page->contentformat = FORMAT_HTML;
    $page->display = 5;
    $page->displayoptions = serialize([]);
    $page->timemodified = time();

    $page->id = $DB->insert_record(
        'page',
        $page
    );

    //
    // Get Page module.
    //
    $module = $DB->get_record(
        'modules',
        ['name' => 'page'],
        '*',
        MUST_EXIST
    );

    //
    // Create Course Module.
    //
    $cm = new \stdClass();

    $cm->course = $params['courseid'];
    $cm->module = $module->id;
    $cm->instance = $page->id;
    $cm->section = $params['section'];
    $cm->visible = 1;
    $cm->groupmode = 0;
    $cm->groupingid = 0;
    $cm->completion = 0;

    $cmid = add_course_module($cm);

    course_add_cm_to_section(
        $params['courseid'],
        $cmid,
        $params['section']
    );
$cm->id = $cmid;
$cm->showdescription = 1;

$DB->update_record(
    "course_modules",
    $cm
);
    rebuild_course_cache(
        $params['courseid'],
        true
    );

    $transaction->allow_commit();

    return [
        'status' => 'SUCCESS',
        'pageid' => $page->id,
        'cmid' => $cmid,
        'url' => (
            new \moodle_url(
                '/mod/page/view.php',
                ['id' => $cmid]
            )
        )->out(false)
    ];

} catch (\Throwable $e) {

    $transaction->rollback($e);

    throw $e;

}
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
                'Page URL'
            )

        ]);

    }

}