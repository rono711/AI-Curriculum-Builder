<?php
/**
 * External API for creating or reusing a curriculum course.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/course/lib.php');

use context_system;
use context_course;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;

/**
 * Create or reuse the Moodle category hierarchy and course.
 */
class ensure_course extends external_api {

    public static function execute_parameters(): external_function_parameters {

        return new external_function_parameters([

            'school_level' => new external_value(
                PARAM_TEXT,
                'School level'
            ),

            'subject' => new external_value(
                PARAM_TEXT,
                'Curriculum subject'
            ),

            'year_level' => new external_value(
                PARAM_TEXT,
                'Curriculum year level'
            ),

            'course_description' => new external_value(
                PARAM_RAW,
                'Course description',
                VALUE_DEFAULT,
                ''
            ),

            'course_image_base64' => new external_value(
                PARAM_RAW,
                'Base64 encoded course image',
                VALUE_DEFAULT,
                ''
            ),
        ]);
    }

    public static function execute(
        string $school_level,
        string $subject,
        string $year_level,
        string $course_description = '',
        string $course_image_base64 = ''
    ): array {

        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'school_level' => $school_level,
                'subject' => $subject,
                'year_level' => $year_level,
                'course_description' =>
                    $course_description,
                'course_image_base64' =>
                    $course_image_base64,
            ]
        );

        $school_level = trim(
            $params['school_level']
        );

        $subject = trim(
            $params['subject']
        );

        $year_level = trim(
            $params['year_level']
        );

        $context = context_system::instance();

        self::validate_context(
            $context
        );

        require_capability(
            'moodle/course:create',
            $context
        );

        if (
            $school_level === ''
            || $subject === ''
            || $year_level === ''
        ) {
            throw new \invalid_parameter_exception(
                'School level, subject and year level are required.'
            );
        }

        /*
         * Moodle course identity.
         */

        $fullname =
            $subject
            . ' - '
            . $year_level;

        $shortname =
            strtoupper(
                preg_replace(
                    '/[^A-Za-z0-9]/',
                    '',
                    $subject
                )
            )
            . '_'
            . strtoupper(
                preg_replace(
                    '/[^A-Za-z0-9]/',
                    '',
                    $year_level
                )
            );

        /*
         * Always reuse an existing course with the
         * deterministic shortname.
         */

        $course = $DB->get_record(
            'course',
            [
                'shortname' => $shortname,
            ]
        );

        $created = false;

        $course_description = trim(
            $params['course_description']
        );

        $course_image_base64 = trim(
            $params['course_image_base64']
        );

        if (!$course) {

            $categoryid = self::get_category(
                $school_level,
                $subject,
                $year_level
            );

            $record = new \stdClass();

            $record->fullname =
                $fullname;

            $record->shortname =
                $shortname;

            $record->category =
                $categoryid;

            $record->visible =
                1;

            $record->summary =
                $course_description;

            $record->summaryformat =
                FORMAT_HTML;

            $course = create_course(
                $record
            );

            $created = true;

        } else if (
            $course_description !== ''
            && (
                (string)$course->summary
                !== $course_description
            )
        ) {
            $record = new \stdClass();
            $record->id = $course->id;
            $record->summary =
                $course_description;
            $record->summaryformat =
                FORMAT_HTML;

            update_course(
                $record
            );

            $course = $DB->get_record(
                'course',
                ['id' => $course->id],
                '*',
                MUST_EXIST
            );
        }

        /*
         * Apply the generated Moodle course overview image.
         *
         * This operation is intentionally idempotent:
         * the Curriculum Builder-owned overview image is
         * replaced whenever ensure_course() receives one.
         */
        if ($course_image_base64 !== '') {

            $decoded = base64_decode(
                $course_image_base64,
                true
            );

            if (
                $decoded === false
                || $decoded === ''
            ) {
                throw new \moodle_exception(
                    'Invalid or empty course image.'
                );
            }

            /*
             * Validate that the decoded payload is an image.
             */
            $imageinfo = @getimagesizefromstring(
                $decoded
            );

            if ($imageinfo === false) {
                throw new \moodle_exception(
                    'Decoded course image is not a valid image.'
                );
            }

            $mimetype = strtolower(
                (string)($imageinfo['mime'] ?? '')
            );

            $extensions = [
                'image/png' => 'png',
                'image/jpeg' => 'jpg',
                'image/gif' => 'gif',
                'image/webp' => 'webp',
            ];

            if (!isset($extensions[$mimetype])) {
                throw new \moodle_exception(
                    'Unsupported course image type: '
                    . $mimetype
                );
            }

            $extension =
                $extensions[$mimetype];

            $filename =
                'rono_course_overview.'
                . $extension;

            $coursecontext =
                context_course::instance(
                    $course->id
                );

            $fs = get_file_storage();

            /*
             * Remove only Curriculum Builder-owned
             * overview images. Do not delete unrelated
             * teacher/admin overview files.
             */
            foreach (
                [
                    'rono_course_overview.png',
                    'rono_course_overview.jpg',
                    'rono_course_overview.gif',
                    'rono_course_overview.webp',
                ]
                as $oldfilename
            ) {
                $oldfile = $fs->get_file(
                    $coursecontext->id,
                    'course',
                    'overviewfiles',
                    0,
                    '/',
                    $oldfilename
                );

                if ($oldfile) {
                    $oldfile->delete();
                }
            }

            $filerecord = [
                'contextid' =>
                    $coursecontext->id,

                'component' =>
                    'course',

                'filearea' =>
                    'overviewfiles',

                'itemid' =>
                    0,

                'filepath' =>
                    '/',

                'filename' =>
                    $filename,

                'mimetype' =>
                    $mimetype,
            ];

            $fs->create_file_from_string(
                $filerecord,
                $decoded
            );
        }

        return [
            'status' =>
                'SUCCESS',

            'courseid' =>
                (int)$course->id,

            'fullname' =>
                (string)$course->fullname,

            'shortname' =>
                (string)$course->shortname,

            'categoryid' =>
                (int)$course->category,

            'created' =>
                $created,
        ];
    }

    /**
     * Find or create:
     *
     * Root
     *   -> School Level
     *      -> Subject
     *         -> Year Level
     */
    protected static function get_category(
        string $school_level,
        string $subject,
        string $year_level
    ): int {

        global $DB;

        /*
         * Configured root category.
         */

        $rootid = (int)get_config(
            'local_rono_publisher',
            'rootcoursecategory'
        );

        if ($rootid < 1) {
            throw new \moodle_exception(
                'Rono Publisher root course category has not been configured.'
            );
        }

        $root = $DB->get_record(
            'course_categories',
            [
                'id' => $rootid,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * School Level.
         */

        $level = $DB->get_record(
            'course_categories',
            [
                'parent' =>
                    $root->id,

                'name' =>
                    $school_level,
            ]
        );

        if (!$level) {

            $record = new \stdClass();

            $record->name =
                $school_level;

            $record->parent =
                $root->id;

            $level =
                \core_course_category::create(
                    $record
                );
        }

        /*
         * Subject.
         */

        $area = $DB->get_record(
            'course_categories',
            [
                'parent' =>
                    $level->id,

                'name' =>
                    $subject,
            ]
        );

        if (!$area) {

            $record = new \stdClass();

            $record->name =
                $subject;

            $record->parent =
                $level->id;

            $area =
                \core_course_category::create(
                    $record
                );
        }

        /*
         * Year Level.
         */

        $year = $DB->get_record(
            'course_categories',
            [
                'parent' =>
                    $area->id,

                'name' =>
                    $year_level,
            ]
        );

        if (!$year) {

            $record = new \stdClass();

            $record->name =
                $year_level;

            $record->parent =
                $area->id;

            $year =
                \core_course_category::create(
                    $record
                );
        }

        return (int)$year->id;
    }

    public static function execute_returns(): external_single_structure {

        return new external_single_structure([

            'status' => new external_value(
                PARAM_TEXT,
                'Status'
            ),

            'courseid' => new external_value(
                PARAM_INT,
                'Moodle course ID'
            ),

            'fullname' => new external_value(
                PARAM_TEXT,
                'Course full name'
            ),

            'shortname' => new external_value(
                PARAM_TEXT,
                'Course short name'
            ),

            'categoryid' => new external_value(
                PARAM_INT,
                'Moodle category containing the course'
            ),

            'created' => new external_value(
                PARAM_BOOL,
                'Whether the course was created'
            ),
        ]);
    }
}
