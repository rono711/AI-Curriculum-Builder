<?php
/**
 * External API for updating one existing elaboration banner.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

use context_course;
use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_single_structure;
use core_external\external_value;
use local_rono_publisher\service\page_service;
use moodle_exception;

class update_elaboration_banner extends external_api {

    public static function execute_parameters():
        external_function_parameters {

        return new external_function_parameters([

            'courseid' => new external_value(
                PARAM_INT,
                'Target Moodle course ID'
            ),

            'cmid' => new external_value(
                PARAM_INT,
                'Existing Text and Media course-module ID'
            ),

            'curriculumcode' => new external_value(
                PARAM_TEXT,
                'Stable elaboration curriculum code'
            ),

            'parentcode' => new external_value(
                PARAM_TEXT,
                'Stable Content Description parent code'
            ),

            'elaboration' => new external_value(
                PARAM_RAW,
                'Learner-facing curriculum elaboration'
            ),

            'imagename' => new external_value(
                PARAM_FILE,
                'Generated elaboration image filename'
            ),

            'image' => new external_value(
                PARAM_RAW,
                'Base64 encoded elaboration PNG'
            ),
        ]);
    }

    public static function execute(
        int $courseid,
        int $cmid,
        string $curriculumcode,
        string $parentcode,
        string $elaboration,
        string $imagename,
        string $image
    ): array {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'cmid' => $cmid,
                'curriculumcode' => $curriculumcode,
                'parentcode' => $parentcode,
                'elaboration' => $elaboration,
                'imagename' => $imagename,
                'image' => $image,
            ]
        );

        $course = $DB->get_record(
            'course',
            ['id' => $params['courseid']],
            '*',
            MUST_EXIST
        );

        $context = context_course::instance(
            $course->id
        );

        self::validate_context(
            $context
        );

        require_capability(
            'local/rono_publisher:publishlesson',
            $context
        );

        $pages = new page_service();

        $updatedcm =
            $pages->update_elaboration_banner(
                (int)$course->id,
                (int)$params['cmid'],
                $params['curriculumcode'],
                $params['parentcode'],
                $params['elaboration'],
                $params['imagename'],
                $params['image']
            );

        if (
            (int)$updatedcm->id
            !==
            (int)$params['cmid']
        ) {
            throw new moodle_exception(
                'Updated banner CMID does not match requested CMID.'
            );
        }

        return [
            'status' => 'success',
            'message' =>
                'Existing elaboration banner updated successfully.',
            'courseid' => (int)$course->id,
            'cmid' => (int)$updatedcm->id,
            'instanceid' => (int)$updatedcm->instance,
        ];
    }

    public static function execute_returns():
        external_single_structure {

        return new external_single_structure([

            'status' => new external_value(
                PARAM_TEXT,
                'Update status'
            ),

            'message' => new external_value(
                PARAM_TEXT,
                'Update result message'
            ),

            'courseid' => new external_value(
                PARAM_INT,
                'Moodle course ID'
            ),

            'cmid' => new external_value(
                PARAM_INT,
                'Updated Text and Media CMID'
            ),

            'instanceid' => new external_value(
                PARAM_INT,
                'Existing Text and Media instance ID'
            ),
        ]);
    }
}
