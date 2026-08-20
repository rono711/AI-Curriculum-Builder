<?php
/**
 * Section service for Rono Publisher.
 *
 * Creates and locates:
 * - Strand sections.
 * - Sub-strand subsections.
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
 * Service responsible for Moodle course sections and subsections.
 */
class section_service {

    /**
     * Find an existing strand section or create a new one.
     *
     * Example:
     * Language
     * Literature
     * Literacy
     *
     * @param int $courseid Moodle course ID.
     * @param string $strand Strand name.
     * @return stdClass Moodle course_sections record.
     */
    public function find_or_create_strand(
        int $courseid,
        string $strand
    ): stdClass {
        global $DB;

        $strand = trim($strand);

        if ($strand === '') {
            throw new moodle_exception(
                'Strand name cannot be empty.'
            );
        }

        // Look only for normal top-level course sections.
        $sections = $DB->get_records(
            'course_sections',
            [
                'course' => $courseid,
            ],
            'section ASC'
        );

        foreach ($sections as $section) {

            // Delegated sections belong to activities such as subsection.
            // They must not be treated as top-level strand sections.
            if (!empty($section->component)) {
                continue;
            }

            if (
                trim((string)$section->name) === $strand
            ) {
                return $section;
            }
        }

        return $this->create_strand(
            $courseid,
            $strand
        );
    }

    /**
     * Create a new top-level Moodle section for a strand.
     *
     * @param int $courseid Moodle course ID.
     * @param string $strand Strand name.
     * @return stdClass
     */
    private function create_strand(
        int $courseid,
        string $strand
    ): stdClass {
        global $DB;

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        /*
         * course_create_section() is Moodle's course API helper.
         * Do not INSERT directly into course_sections.
         */
        $section = course_create_section(
            $course->id
        );

        if (!$section) {
            throw new moodle_exception(
                'Unable to create strand section.'
            );
        }

        // Give the newly-created section the curriculum strand name.
        $updatedata = new stdClass();
        $updatedata->id = $section->id;
        $updatedata->name = $strand;
        $updatedata->timemodified = time();

        $DB->update_record(
            'course_sections',
            $updatedata
        );

        

        return $DB->get_record(
            'course_sections',
            ['id' => $section->id],
            '*',
            MUST_EXIST
        );
    }

    /**
     * Find an existing Moodle subsection under a strand.
     *
     * If one does not exist, create it.
     *
     * Example:
     *
     * Language
     *   └── Language for interacting with others
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $strandsection Parent strand section.
     * @param string $substrand Sub-strand name.
     * @return array
     */
    public function find_or_create_subsection(
        int $courseid,
        stdClass $strandsection,
        string $substrand
    ): array {
        global $DB;

        $substrand = trim($substrand);

        if ($substrand === '') {
            throw new moodle_exception(
                'Sub-strand name cannot be empty.'
            );
        }

        /*
         * Learner-facing subsection title:
         * capitalise the first Unicode character while preserving
         * the remainder of the curriculum text.
         */
        $substrand =
            mb_strtoupper(
                mb_substr(
                    $substrand,
                    0,
                    1,
                    'UTF-8'
                ),
                'UTF-8'
            )
            .
            mb_substr(
                $substrand,
                1,
                null,
                'UTF-8'
            );

        /*
         * Moodle Subsection is a real activity module (mod_subsection).
         *
         * The subsection activity lives in the parent strand section.
         * Its delegated course section contains the activities belonging
         * to that subsection.
         */

        $subsectionmodule = $DB->get_record(
            'modules',
            ['name' => 'subsection']
        );

        if (!$subsectionmodule) {
            throw new moodle_exception(
                'The Moodle Subsection activity is not installed.'
            );
        }

        /*
         * Find subsection activities located in this strand section.
         */
        $sql = "
            SELECT
                cm.id AS cmid,
                cm.instance,
                s.name
            FROM {course_modules} cm
            JOIN {subsection} s
              ON s.id = cm.instance
            WHERE cm.course = :courseid
              AND cm.section = :sectionid
              AND cm.module = :moduleid
        ";

        $records = $DB->get_records_sql(
            $sql,
            [
                'courseid' => $courseid,
                'sectionid' => $strandsection->id,
                'moduleid' => $subsectionmodule->id,
            ]
        );

        foreach ($records as $record) {

            $existingname =
                trim((string)$record->name);

            /*
             * Match case-insensitively so an existing subsection
             * is reused rather than duplicated only because its
             * first character previously used lowercase.
             */
            if (
                mb_strtolower(
                    $existingname,
                    'UTF-8'
                )
                ===
                mb_strtolower(
                    $substrand,
                    'UTF-8'
                )
            ) {

                /*
                 * Upgrade the existing learner-facing title while
                 * retaining the same subsection instance and CMID.
                 */
                if ($existingname !== $substrand) {

                    $existing =
                        $DB->get_record(
                            'subsection',
                            [
                                'id' =>
                                    (int)$record->instance,
                            ],
                            '*',
                            MUST_EXIST
                        );

                    $existing->name =
                        $substrand;

                    $DB->update_record(
                        'subsection',
                        $existing
                    );

                    rebuild_course_cache(
                        $courseid,
                        true
                    );
                }

                return $this->get_subsection_result(
                    $courseid,
                    (int)$record->instance,
                    (int)$record->cmid
                );
            }
        }

        return $this->create_subsection(
            $courseid,
            $strandsection,
            $substrand
        );
    }

    /**
     * Create a Moodle Subsection activity.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $strandsection Parent strand section.
     * @param string $substrand Sub-strand name.
     * @return array
     */
    private function create_subsection(
        int $courseid,
        stdClass $strandsection,
        string $substrand
    ): array {
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
            ['name' => 'subsection'],
            '*',
            MUST_EXIST
        );

        /*
         * Prepare module creation data using Moodle's standard
         * course-module creation API.
         */
        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'subsection';
        $moduleinfo->module = $module->id;

        $moduleinfo->course = $course->id;

        // This is the parent Strand section number.
        $moduleinfo->section = $strandsection->section;

        $moduleinfo->name = $substrand;

        $moduleinfo->visible = 1;

        $moduleinfo->groupmode = 0;
        $moduleinfo->groupingid = 0;

        $moduleinfo->completion = 0;

        /*
         * Moodle creates:
         *
         * mod_subsection instance
         *       +
         * course_module
         *       +
         * delegated course section
         */
        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created) ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Moodle subsection.'
            );
        }



        $cmid = (int)$created->coursemodule;

        $cm = $DB->get_record(
            'course_modules',
            ['id' => $cmid],
            '*',
            MUST_EXIST
        );

        return $this->get_subsection_result(
            $courseid,
            (int)$cm->instance,
            $cmid
        );
    }

    /**
     * Return information about a Moodle subsection and its delegated section.
     *
     * @param int $courseid Moodle course ID.
     * @param int $instanceid mod_subsection instance ID.
     * @param int $cmid Course module ID.
     * @return array
     */
    private function get_subsection_result(
        int $courseid,
        int $instanceid,
        int $cmid
    ): array {
        global $DB;

        $subsection = $DB->get_record(
            'subsection',
            ['id' => $instanceid],
            '*',
            MUST_EXIST
        );

        /*
         * Moodle delegated sections identify their owning component
         * and item.
         */
        $delegatedsection = $DB->get_record(
            'course_sections',
            [
                'course' => $courseid,
                'component' => 'mod_subsection',
                'itemid' => $instanceid,
            ],
            '*',
            MUST_EXIST
        );

        return [
            'instanceid' => $instanceid,
            'cmid' => $cmid,
            'subsection' => $subsection,
            'section' => $delegatedsection,
        ];
    }
}
