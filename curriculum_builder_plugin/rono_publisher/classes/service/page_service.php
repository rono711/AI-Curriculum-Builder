<?php
/**
 * Page and Text & Media service for Rono Publisher.
 *
 * Creates:
 * - Text & Media activities for curriculum content descriptions.
 * - Moodle Page activities for lesson components.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

use moodle_exception;
use stdClass;

/**
 * Service responsible for Text & Media and Page activities.
 */
class page_service {

    /**
     * Find or create the Content Description Text & Media activity.
     *
     * This activity is placed as the first curriculum item inside
     * the delegated subsection.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $contentdescription Curriculum content description.
     * @return stdClass Created or existing course module record.
     */
    public function find_or_create_content_description(
        int $courseid,
        stdClass $section,
        string $contentdescription
    ): stdClass {
        global $DB;

        $contentdescription = trim($contentdescription);

        if ($contentdescription === '') {
            throw new moodle_exception(
                'Content description cannot be empty.'
            );
        }

        /*
         * Moodle still uses the internal module name "label"
         * for the activity presented in the UI as Text & Media.
         */
        $labelmodule = $DB->get_record(
            'modules',
            ['name' => 'label'],
            '*',
            MUST_EXIST
        );

        /*
         * Look for an existing matching Text & Media activity
         * inside this exact subsection.
         */
        $sql = "
            SELECT
                cm.id,
                cm.instance,
                l.name,
                l.intro
            FROM {course_modules} cm
            JOIN {label} l
              ON l.id = cm.instance
            WHERE cm.course = :courseid
              AND cm.section = :sectionid
              AND cm.module = :moduleid
        ";

        $records = $DB->get_records_sql(
            $sql,
            [
                'courseid' => $courseid,
                'sectionid' => $section->id,
                'moduleid' => $labelmodule->id,
            ]
        );

        foreach ($records as $record) {
            if (
                trim(strip_tags((string)$record->intro)) ===
                trim(strip_tags($contentdescription))
            ) {
                return $DB->get_record(
                    'course_modules',
                    ['id' => $record->id],
                    '*',
                    MUST_EXIST
                );
            }
        }

        return $this->create_text_and_media(
            $courseid,
            $section,
            $contentdescription
        );
    }

    /**
     * Create the curriculum Content Description as Text & Media.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $contentdescription Content description HTML/text.
     * @return stdClass Course module record.
     */
    private function create_text_and_media(
        int $courseid,
        stdClass $section,
        string $contentdescription
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        $module = $DB->get_record(
            'modules',
            ['name' => 'label'],
            '*',
            MUST_EXIST
        );

        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'label';
        $moduleinfo->module = $module->id;

        $moduleinfo->course = $course->id;

        /*
         * add_moduleinfo() expects the section NUMBER,
         * not the course_sections database ID.
         */
        $moduleinfo->section = $section->section;

        /*
         * Text & Media content is stored in intro.
         */
        $moduleinfo->name = shorten_text(
            trim(strip_tags($contentdescription)),
            100
        );

        $moduleinfo->intro = $contentdescription;
        $moduleinfo->introformat = FORMAT_HTML;

        $moduleinfo->visible = 1;

        $moduleinfo->groupmode = 0;
        $moduleinfo->groupingid = 0;
        $moduleinfo->completion = 0;

		        /*
         * Temporary diagnostics for Moodle module creation.
         * Do not log full HTML content.
         */
        debugging(
            'RONO PAGE CREATE: ' .
            'name_type=' . gettype($moduleinfo->name) .
            ', intro_type=' . gettype($moduleinfo->intro) .
            ', content_type=' . gettype($moduleinfo->content) .
            ', section_type=' . gettype($moduleinfo->section) .
            ', name=' . (string)$moduleinfo->name,
            DEBUG_DEVELOPER
		);

		debugging(
            'RONO LABEL CREATE: ' .
            'name_type=' . gettype($moduleinfo->name) .
            ', intro_type=' . gettype($moduleinfo->intro) .
            ', section_type=' . gettype($moduleinfo->section),
            DEBUG_DEVELOPER
        );
        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created) ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Content Description Text & Media activity.'
            );
        }



        return $DB->get_record(
            'course_modules',
            ['id' => (int)$created->coursemodule],
            '*',
            MUST_EXIST
        );
    }

    /**
     * Create a Moodle Page activity.
     *
     * Used for:
     *
     * Lesson Content / Mission of the Day
     * Did You Know?
     * Let's Do It
     * What We Discovered
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $name Page activity title.
     * @param string $content Page HTML.
     * @param string $description Activity description.
     * @param int $indent Moodle course-page indentation level.
     * @return stdClass Course module record.
     */
    public function create_page(
        int $courseid,
        stdClass $section,
        string $name,
        string $content,
        string $description = '',
        int $indent = 0
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        $name = trim($name);

        if ($name === '') {
            throw new moodle_exception(
                'Page activity name cannot be empty.'
            );
        }

        if ($indent < 0) {
            $indent = 0;
        }

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        $module = $DB->get_record(
            'modules',
            ['name' => 'page'],
            '*',
            MUST_EXIST
        );

        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'page';
        $moduleinfo->module = $module->id;

        $moduleinfo->course = $course->id;
        $moduleinfo->section = $section->section;

        $moduleinfo->name = $name;

        /*
         * Activity description.
         */
        $moduleinfo->intro = $description;
        $moduleinfo->introformat = FORMAT_HTML;

        /*
         * Actual Page body.
         */
        $moduleinfo->content = $content;
        $moduleinfo->contentformat = FORMAT_HTML;

        /*
         * Page display settings.
         *
         * 5 = Display page name.
         * 10 = Display page description.
         */
        $moduleinfo->display = 5;

        $moduleinfo->visible = 1;

        $moduleinfo->groupmode = 0;
        $moduleinfo->groupingid = 0;
        $moduleinfo->completion = 0;

        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created) ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Moodle Page activity.'
            );
        }

        $cmid = (int)$created->coursemodule;

        /*
         * Moodle stores activity indentation on course_modules.
         *
         * Lesson Content:
         *     indent = 0
         *
         * Did You Know?
         * Quiz
         * Let's Do It
         * What We Discovered:
         *     indent = 1
         */
        if ($indent > 0) {
            $DB->set_field(
                'course_modules',
                'indent',
                $indent,
                ['id' => $cmid]
            );
        }

        

        return $DB->get_record(
            'course_modules',
            ['id' => $cmid],
            '*',
            MUST_EXIST
        );
    }
    /**
     * Update an existing Moodle Page activity in place.
     *
     * Safety:
     * - Exact CMID is required.
     * - CMID must belong to the supplied course.
     * - CMID must be mod_page.
     * - Existing Page instance is updated.
     * - No new course module is created.
     *
     * @param int $courseid Moodle course ID.
     * @param int $cmid Existing Page course-module ID.
     * @param string $content Replacement Page HTML.
     * @param string|null $description Optional replacement description.
     * @return stdClass Existing course module.
     */
    public function update_page(
        int $courseid,
        int $cmid,
        string $content,
        ?string $description = null
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        if ($courseid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course ID.'
            );
        }

        if ($cmid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course module ID.'
            );
        }

        /*
         * Exact target course.
         */
        $course = $DB->get_record(
            'course',
            [
                'id' => $courseid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Exact target course module.
         */
        $cm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Verify target is really mod_page.
         */
        $module = $DB->get_record(
            'modules',
            [
                'id' => $cm->module,
            ],
            '*',
            MUST_EXIST
        );

        if ($module->name !== 'page') {
            throw new moodle_exception(
                'Target course module is not a Moodle Page.'
            );
        }

        /*
         * Verify the underlying Page instance.
         */
        $page = $DB->get_record(
            'page',
            [
                'id' => $cm->instance,
                'course' => $course->id,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Ask Moodle for the existing module information.
         */
        [
            $existingcm,
            $context,
            $existingmodule,
            $moduleinfo,
            $section
        ] = get_moduleinfo_data(
            $cm,
            $course
        );

        /*
         * Defensive identity checks.
         */
        if ((int)$existingcm->id !== $cmid) {
            throw new moodle_exception(
                'Moodle returned an unexpected course module.'
            );
        }

        if ($existingmodule->name !== 'page') {
            throw new moodle_exception(
                'Validated Moodle module is not a Page.'
            );
        }

        /*
         * Preserve existing Page name.
         */
        $moduleinfo->name =
            $page->name;

        /*
         * Moodle 5.2 mod_page update contract.
         *
         * page_update_instance() reads the Page body from:
         *
         * $data->page['itemid']
         * $data->page['text']
         * $data->page['format']
         */
        $moduleinfo->page = [
            'itemid' => 0,
            'text' => $content,
            'format' => FORMAT_HTML,
        ];

        /*
         * Keep direct content fields populated too.
         */
        $moduleinfo->content =
            $content;

        $moduleinfo->contentformat =
            FORMAT_HTML;

        /*
         * Preserve existing Page-specific display options.
         */
        $displayoptions = [];

        if (!empty($page->displayoptions)) {
            $decodedoptions =
                unserialize($page->displayoptions);

            if (is_array($decodedoptions)) {
                $displayoptions =
                    $decodedoptions;
            }
        }

        $moduleinfo->display =
            $page->display;

        $moduleinfo->printintro =
            $displayoptions['printintro']
            ?? 0;

        $moduleinfo->printlastmodified =
            $displayoptions['printlastmodified']
            ?? 0;

        $moduleinfo->popupwidth =
            $displayoptions['popupwidth']
            ?? 620;

        $moduleinfo->popupheight =
            $displayoptions['popupheight']
            ?? 450;

        /*
         * Preserve existing description unless a replacement
         * description was explicitly supplied.
         */
        if ($description !== null) {

            if (
                isset($moduleinfo->introeditor) &&
                is_array($moduleinfo->introeditor)
            ) {
                $moduleinfo->introeditor['text'] =
                    $description;

                $moduleinfo->introeditor['format'] =
                    FORMAT_HTML;
            }

            $moduleinfo->intro =
                $description;

            $moduleinfo->introformat =
                FORMAT_HTML;
        }

        /*
         * Critical existing Moodle identity.
         */
        $moduleinfo->coursemodule =
            $cmid;

        $moduleinfo->instance =
            $page->id;

        $moduleinfo->course =
            $course->id;

        $moduleinfo->module =
            $module->id;

        $moduleinfo->modulename =
            'page';
        /*
         * update_moduleinfo() triggers course_module_updated
         * using the $cm object.
         *
         * Because $cm was loaded directly from the
         * course_modules table, Moodle's derived "modname"
         * property is not present automatically.
         */
        $cm->modname =
            'page';
		
		/*
         * Update the EXISTING Moodle activity.
         *
         * No add_moduleinfo() call occurs here.
         */
        update_moduleinfo(
            $cm,
            $moduleinfo,
            $course
        );

        /*
         * Verify the same CMID still points to the same
         * Page instance after the update.
         */
        $updatedcm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
                'instance' => $page->id,
            ],
            '*',
            MUST_EXIST
        );

        return $updatedcm;
    }

}
