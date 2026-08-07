<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Page Repository
 *
 * Version 4.0
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\repository;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/course/modlib.php');
require_once($CFG->dirroot . '/mod/page/lib.php');

class page_repository {

    /**
     * ======================================================
     * Publish Page
     * ======================================================
     */

    public function publish(

        string $lessonpackageid,

        string $activitytype,

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $content

    ): array {

        $mapping = $this->find_mapping(

            $lessonpackageid,

            $activitytype

        );

        if ($mapping) {

            return $this->update(

                $mapping,

                $title,

                $description,

                $content

            );

        }

        return $this->create(

            $lessonpackageid,

            $activitytype,

            $courseid,

            $section,

            $title,

            $description,

            $content

        );

    }

    /**
     * ======================================================
     * Find Mapping
     * ======================================================
     */

    protected function find_mapping(

        string $lessonpackageid,

        string $activitytype

    ) {

        global $DB;

        return $DB->get_record(

            "local_rono_page_map",

            [

                "lesson_package_id"=>$lessonpackageid,

                "activity_type"=>$activitytype

            ]

        );

    }
    /**
     * ======================================================
     * Create
     * ======================================================
     */

    protected function create(

        string $lessonpackageid,

        string $activitytype,

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $content

    ): array {

        //
        // We reuse create_page.php
        //

        $page =

            \local_rono_curriculumbuilder\external\create_page::execute(

                $courseid,

                $section,

                $title,

                $description,

                $content

            );

        $this->save_mapping(

            $lessonpackageid,

            $activitytype,

            $page["pageid"],

            $page["cmid"]

        );

        return $page;

    }
    /**
     * ======================================================
     * Update
     * ======================================================
     */

    protected function update(

        $mapping,

        string $title,

        string $description,

        string $content

    ): array {

        return

            \local_rono_curriculumbuilder\external\update_page::execute(

                $mapping->pageid,

                $title,

                $description,

                $content

            );

    }
    /**
     * ======================================================
     * Save Mapping
     * ======================================================
     */

    protected function save_mapping(

        string $lessonpackageid,

        string $activitytype,

        int $pageid,

        int $cmid

    ) {

        global $DB;

        $record = new \stdClass();

        $record->lesson_package_id =

            $lessonpackageid;

        $record->activity_type =

            $activitytype;

        $record->pageid =

            $pageid;

        $record->cmid =

            $cmid;

        $record->timecreated =

            time();

        $record->timemodified =

            time();

        $DB->insert_record(

            "local_rono_page_map",

            $record

        );

    }

}