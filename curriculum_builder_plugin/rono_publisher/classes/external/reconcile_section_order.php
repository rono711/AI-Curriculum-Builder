<?php

namespace local_rono_publisher\external;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/course/lib.php');

use core_external\external_api;
use core_external\external_function_parameters;
use core_external\external_multiple_structure;
use core_external\external_single_structure;
use core_external\external_value;

class reconcile_section_order extends external_api {

    public static function execute_parameters(): external_function_parameters {
        return new external_function_parameters([
            'courseid' => new external_value(
                PARAM_INT,
                'Moodle course ID'
            ),
            'sectionid' => new external_value(
                PARAM_INT,
                'Moodle course_sections ID'
            ),
            'dryrun' => new external_value(
                PARAM_BOOL,
                'Validate without changing Moodle',
                VALUE_DEFAULT,
                true
            ),
            'cmids' => new external_multiple_structure(
                new external_value(
                    PARAM_INT,
                    'Curriculum Builder owned CMID'
                )
            ),
        ]);
    }

    public static function execute(
        int $courseid,
        int $sectionid,
        bool $dryrun,
        array $cmids
    ) {
        global $DB;

        $params = self::validate_parameters(
            self::execute_parameters(),
            [
                'courseid' => $courseid,
                'sectionid' => $sectionid,
                'dryrun' => $dryrun,
                'cmids' => $cmids,
            ]
        );

        $course = $DB->get_record(
            'course',
            ['id' => $params['courseid']],
            'id,fullname',
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

        $desired = array_values(
            array_map(
                'intval',
                $params['cmids']
            )
        );

        if (!$desired) {
            throw new \invalid_parameter_exception(
                'At least one CMID is required.'
            );
        }

        if (
            count($desired) !==
            count(array_unique($desired))
        ) {
            throw new \invalid_parameter_exception(
                'Duplicate CMIDs are not allowed.'
            );
        }

        foreach ($desired as $cmid) {
            $exists = $DB->record_exists(
                'course_modules',
                [
                    'id' => $cmid,
                    'course' => $course->id,
                    'section' => $section->id,
                ]
            );

            if (!$exists) {
                throw new \invalid_parameter_exception(
                    'CMID ' . $cmid .
                    ' does not belong to the requested section.'
                );
            }
        }

        $current = array_values(
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

        $owned = array_fill_keys(
            $desired,
            true
        );

        $currentowned = array_values(
            array_filter(
                $current,
                function($cmid) use ($owned) {
                    return isset($owned[$cmid]);
                }
            )
        );

        if (
            count($currentowned) !==
            count($desired)
        ) {
            throw new \invalid_parameter_exception(
                'Not all requested CMIDs are present.'
            );
        }

        $changed = (
            $currentowned !== $desired
        );

        $changedbefore = $changed;
        $applied = false;

        //
        // Preserve every non-owned module in its current slot.
        // Replace only Curriculum Builder-owned slots with
        // the desired owned CMID order.
        //
        $target = $current;
        $desiredindex = 0;

        foreach ($target as $index => $cmid) {
            if (!isset($owned[$cmid])) {
                continue;
            }

            $target[$index] = $desired[
                $desiredindex
            ];

            $desiredindex++;
        }

        //
        // Report the exact positions that differ.
        //
        $moves = [];

        foreach ($current as $index => $cmid) {
            if ($cmid === $target[$index]) {
                continue;
            }

            $moves[] = [
                'position' => $index + 1,
                'currentcmid' => $cmid,
                'targetcmid' => $target[$index],
            ];
        }

        //
        // Apply the calculated complete target only when
        // explicitly requested.
        //
        if (
            !$params['dryrun']
            && $changed
        ) {
            //
            // Re-read Moodle course information before moving.
            //
            rebuild_course_cache(
                $course->id,
                true
            );

            $modinfo = get_fast_modinfo(
                $course->id
            );

            $sectioninfo =
                $modinfo->get_section_info(
                    $section->section
                );

            if (!$sectioninfo) {
                throw new \moodle_exception(
                    'Unable to load target section.'
                );
            }

            //
            // Converge to the target from right to left.
            //
            // Only Curriculum Builder-owned CMIDs may move.
            // Non-owned modules are anchors only and are never
            // passed to moveto_module().
            //
            for (
                $index = count($target) - 1;
                $index >= 0;
                $index--
            ) {
                $cmid = $target[$index];

                if (!isset($owned[$cmid])) {
                    continue;
                }

                $modinfo = get_fast_modinfo(
                    $course->id
                );

                $cm = $modinfo->get_cm(
                    $cmid
                );

                $beforecm = null;

                if (
                    $index + 1 <
                    count($target)
                ) {
                    $beforecmid =
                        $target[$index + 1];

                    $beforecm =
                        $modinfo->get_cm(
                            $beforecmid
                        );
                }

                moveto_module(
                    $cm,
                    $sectioninfo,
                    $beforecm
                );
            }

            //
            // Verify Moodle reached the exact target.
            //
            $verifiedsection =
                $DB->get_record(
                    'course_sections',
                    ['id' => $section->id],
                    'id,sequence',
                    MUST_EXIST
                );

            $verified = array_values(
                array_filter(
                    array_map(
                        'intval',
                        explode(
                            ',',
                            (string)$verifiedsection->sequence
                        )
                    )
                )
            );

            if ($verified !== $target) {
                throw new \moodle_exception(
                    'Section ordering verification failed.'
                );
            }

            $applied = true;

            //
            // Return the verified state as current.
            //
            $current = $verified;
            $currentowned = $desired;
            $changed = false;
        }

        return [
            'courseid' => $course->id,
            'sectionid' => $section->id,
            'dryrun' => (bool)$params['dryrun'],
            'changed' => $changed,
            'changedbefore' => $changedbefore,
            'applied' => $applied,
            'movecount' => count($moves),
            'currentsequence' =>
                implode(',', $current),
            'currentownedsequence' =>
                implode(',', $currentowned),
            'desiredownedsequence' =>
                implode(',', $desired),
            'targetsequence' =>
                implode(',', $target),
            'moves' => $moves,
            'message' => $applied
                ? 'Moodle module ordering was reconciled and verified.'
                : (
                    $changed
                        ? 'Owned Moodle modules require reconciliation.'
                        : 'Owned Moodle modules are already in the requested order.'
                ),
        ];
    }

    public static function execute_returns() {
        return new external_single_structure([
            'courseid' =>
                new external_value(
                    PARAM_INT,
                    'Course ID'
                ),

            'sectionid' =>
                new external_value(
                    PARAM_INT,
                    'Section ID'
                ),

            'dryrun' =>
                new external_value(
                    PARAM_BOOL,
                    'Dry run'
                ),

            'changed' =>
                new external_value(
                    PARAM_BOOL,
                    'Reconciliation required'
                ),

            'changedbefore' =>
                new external_value(
                    PARAM_BOOL,
                    'Whether reconciliation was required before execution'
                ),

            'applied' =>
                new external_value(
                    PARAM_BOOL,
                    'Whether Moodle ordering changes were applied'
                ),

            'movecount' =>
                new external_value(
                    PARAM_INT,
                    'Move estimate'
                ),

            'currentsequence' =>
                new external_value(
                    PARAM_RAW,
                    'Complete current sequence'
                ),

            'currentownedsequence' =>
                new external_value(
                    PARAM_RAW,
                    'Current owned sequence'
                ),

            'desiredownedsequence' =>
                new external_value(
                    PARAM_RAW,
                    'Desired owned sequence'
                ),

            'targetsequence' =>
                new external_value(
                    PARAM_RAW,
                    'Calculated complete target sequence'
                ),

            'moves' =>
                new external_multiple_structure(
                    new external_single_structure([
                        'position' =>
                            new external_value(
                                PARAM_INT,
                                'Section position'
                            ),

                        'currentcmid' =>
                            new external_value(
                                PARAM_INT,
                                'Current CMID'
                            ),

                        'targetcmid' =>
                            new external_value(
                                PARAM_INT,
                                'Target CMID'
                            ),
                    ])
                ),

            'message' =>
                new external_value(
                    PARAM_TEXT,
                    'Result message'
                ),
        ]);
    }
}
