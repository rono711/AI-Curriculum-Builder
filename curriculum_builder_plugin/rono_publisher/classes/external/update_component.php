<?php
/**
 * External API for updating one existing lesson component.
 *
 * Initial implementation:
 * - Recap / What We Discovered only.
 * - Updates an existing Moodle Page by exact CMID.
 * - Does not create any new Moodle activity.
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


/**
 * Update one existing lesson component.
 */
class update_component extends external_api {

    /**
     * External parameters.
     *
     * @return external_function_parameters
     */
    public static function execute_parameters():
        external_function_parameters {

        return new external_function_parameters([

            'courseid' => new external_value(
                PARAM_INT,
                'Target Moodle course ID'
            ),

            'component' => new external_value(
                PARAM_ALPHAEXT,
                'Lesson component to update'
            ),

            'cmid' => new external_value(
                PARAM_INT,
                'Existing Moodle course-module ID'
            ),

            'content' => new external_value(
                PARAM_RAW,
                'Replacement component HTML'
            ),

            'description' => new external_value(
                PARAM_RAW,
                'Optional replacement activity description',
                VALUE_DEFAULT,
                ''
            ),

        ]);
    }


    /**
     * Update one existing component.
     *
     * Initial safety restriction:
     * only recap is supported.
     *
     * @param int $courseid
     * @param string $component
     * @param int $cmid
     * @param string $content
     * @param string $description
     * @return array
     */
    public static function execute(
        int $courseid,
        string $component,
        int $cmid,
        string $content,
        string $description = ''
    ): array {
        global $DB;

        /*
         * =====================================================
         * Validate external parameters
         * =====================================================
         */

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'component' => $component,
                'cmid' => $cmid,
                'content' => $content,
                'description' => $description,
            ]
        );

        $component = strtolower(
            trim($params['component'])
        );

        /*
         * =====================================================
         * Component safety barrier
         * =====================================================
         *
         * Do not allow the generic endpoint to update arbitrary
         * Moodle activities during this development stage.
         */

        if ($component !== 'recap') {
            throw new moodle_exception(
                'Only recap UPDATE is currently enabled.'
            );
        }

        if ((int)$params['courseid'] <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course ID.'
            );
        }

        if ((int)$params['cmid'] <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course module ID.'
            );
        }

        if (trim($params['content']) === '') {
            throw new moodle_exception(
                'Replacement recap content cannot be empty.'
            );
        }

        /*
         * =====================================================
         * Verify course
         * =====================================================
         */

        $course = $DB->get_record(
            'course',
            [
                'id' => $params['courseid'],
            ],
            '*',
            MUST_EXIST
        );

        /*
         * =====================================================
         * Course context / capability
         * =====================================================
         */

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

        /*
         * =====================================================
         * Update existing Page
         * =====================================================
         */

        $pages = new page_service();

        $updatedcm = $pages->update_page(
            (int)$course->id,
            (int)$params['cmid'],
            $params['content'],
            $params['description']
        );

        /*
         * =====================================================
         * Post-update identity verification
         * =====================================================
         */

        if (
            (int)$updatedcm->id
            !==
            (int)$params['cmid']
        ) {
            throw new moodle_exception(
                'Updated Moodle CMID does not match requested CMID.'
            );
        }

        /*
         * =====================================================
         * Result
         * =====================================================
         */

        return [
            'status' => 'success',
            'message' =>
                'Existing lesson component updated successfully.',
            'component' => $component,
            'courseid' => (int)$course->id,
            'cmid' => (int)$updatedcm->id,
            'instanceid' => (int)$updatedcm->instance,
        ];
    }


    /**
     * External return structure.
     *
     * @return external_single_structure
     */
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

            'component' => new external_value(
                PARAM_TEXT,
                'Updated lesson component'
            ),

            'courseid' => new external_value(
                PARAM_INT,
                'Moodle course ID'
            ),

            'cmid' => new external_value(
                PARAM_INT,
                'Updated existing course-module ID'
            ),

            'instanceid' => new external_value(
                PARAM_INT,
                'Existing Moodle Page instance ID'
            ),

        ]);
    }
}
