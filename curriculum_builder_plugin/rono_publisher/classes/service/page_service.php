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

        rebuild_course_cache(
            $course->id,
            true
        );

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

        rebuild_course_cache(
            $course->id,
            true
        );

        return $DB->get_record(
            'course_modules',
            ['id' => $cmid],
            '*',
            MUST_EXIST
        );
    }
}