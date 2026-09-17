<?php

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/externallib.php');

use external_api;
use external_function_parameters;
use external_multiple_structure;
use external_single_structure;
use external_value;

class inspect_section_order extends external_api {

    public static function execute_parameters() {
        return new external_function_parameters([
            'courseid' => new external_value(
                PARAM_INT,
                'Moodle course ID'
            ),
            'sectionid' => new external_value(
                PARAM_INT,
                'Moodle course_sections ID'
            ),
        ]);
    }

    public static function execute(
        int $courseid,
        int $sectionid
    ) {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'sectionid' => $sectionid,
            ]
        );

        $course = $DB->get_record(
            'course',
            ['id' => $params['courseid']],
            'id,fullname,shortname',
            MUST_EXIST
        );

        $context = \context_course::instance(
            $course->id
        );

        self::validate_context($context);

        require_capability(
            'local/rono_publisher:publishlesson',
            $context
        );

        $section = $DB->get_record(
            'course_sections',
            [
                'id' => $params['sectionid'],
                'course' => $course->id,
            ],
            'id,course,section,name,sequence',
            MUST_EXIST
        );

        $cmids = array_values(
            array_filter(
                array_map(
                    'intval',
                    explode(
                        ',',
                        (string)$section->sequence
                    )
                )
            )
        );

        $modules = [];

        foreach ($cmids as $position => $cmid) {
            $cm = $DB->get_record(
                'course_modules',
                [
                    'id' => $cmid,
                    'course' => $course->id,
                    'section' => $section->id,
                ],
                'id,module,instance,section',
                MUST_EXIST
            );

            $module = $DB->get_record(
                'modules',
                ['id' => $cm->module],
                'id,name',
                MUST_EXIST
            );

            $modules[] = [
                'position' => $position + 1,
                'cmid' => $cm->id,
                'modname' => $module->name,
                'instanceid' => $cm->instance,
            ];
        }

        return [
            'courseid' => $course->id,
            'fullname' => $course->fullname,
            'sectionid' => $section->id,
            'sectionnumber' => $section->section,
            'sectionname' => (string)$section->name,
            'sequence' => (string)$section->sequence,
            'modulecount' => count($modules),
            'modules' => $modules,
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'courseid' =>
                new external_value(PARAM_INT, 'Course ID'),

            'fullname' =>
                new external_value(PARAM_TEXT, 'Course fullname'),

            'sectionid' =>
                new external_value(PARAM_INT, 'Section ID'),

            'sectionnumber' =>
                new external_value(PARAM_INT, 'Section number'),

            'sectionname' =>
                new external_value(PARAM_TEXT, 'Section name'),

            'sequence' =>
                new external_value(PARAM_RAW, 'Raw CMID sequence'),

            'modulecount' =>
                new external_value(PARAM_INT, 'Module count'),

            'modules' =>
                new external_multiple_structure(
                    new external_single_structure([
                        'position' =>
                            new external_value(
                                PARAM_INT,
                                'Position'
                            ),

                        'cmid' =>
                            new external_value(
                                PARAM_INT,
                                'Course module ID'
                            ),

                        'modname' =>
                            new external_value(
                                PARAM_PLUGIN,
                                'Module type'
                            ),

                        'instanceid' =>
                            new external_value(
                                PARAM_INT,
                                'Module instance ID'
                            ),
                    ])
                ),
        ]);
    }
}
