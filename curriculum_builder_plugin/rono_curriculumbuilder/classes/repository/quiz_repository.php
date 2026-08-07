<?php
/**
 * ============================================================================
 * Rono Curriculum Builder
 *
 * Quiz Repository
 *
 * Version 4.0
 * ============================================================================
 */

namespace local_rono_curriculumbuilder\repository;

defined('MOODLE_INTERNAL') || die();

require_once($CFG->dirroot . '/mod/quiz/lib.php');

class quiz_repository {

    /**
     * ======================================================
     * Publish
     * ======================================================
     */

    public function publish(

        string $lessonpackageid,

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $giftfile

    ): array {

        $mapping = $this->find_mapping(

            $lessonpackageid

        );

        if ($mapping) {

            return $this->update(

                $mapping,

                $title,

                $description,

                $giftfile

            );

        }

        return $this->create(

            $lessonpackageid,

            $courseid,

            $section,

            $title,

            $description,

            $giftfile

        );

    }

    /**
     * ======================================================
     * Mapping
     * ======================================================
     */

    protected function find_mapping(

        string $lessonpackageid

    ) {

        global $DB;

        return $DB->get_record(

            "local_rono_quiz_map",

            [

                "lesson_package_id"=>$lessonpackageid

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

        int $courseid,

        int $section,

        string $title,

        string $description,

        string $giftfile

    ): array {

        //
        // Version 4
        //
        // Moodle Quiz Creation
        // will be implemented here.
        //

        $quizid = 0;

        $cmid = 0;

        //
        // Import GIFT
        //

        $this->import_gift(

            $quizid,

            $giftfile

        );

        //
        // Mapping
        //

        $this->save_mapping(

            $lessonpackageid,

            $quizid,

            $cmid

        );

        return [

            "status"=>"SUCCESS",

            "quizid"=>$quizid,

            "cmid"=>$cmid,

            "url"=>""

        ];

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

        string $giftfile

    ): array {

        //
        // Replace Questions
        //

        $this->replace_questions(

            $mapping->quizid,

            $giftfile

        );

        return [

            "status"=>"SUCCESS",

            "quizid"=>$mapping->quizid,

            "cmid"=>$mapping->cmid,

            "url"=>""

        ];

    }

    /**
     * ======================================================
     * Import GIFT
     * ======================================================
     */

    protected function import_gift(

        int $quizid,

        string $giftfile

    ) {

        //
        // Moodle Question Bank
        // implementation.
        //

    }

    /**
     * ======================================================
     * Replace Questions
     * ======================================================
     */

    protected function replace_questions(

        int $quizid,

        string $giftfile

    ) {

        //
        // Delete old questions.
        //
        // Import new GIFT.
        //

    }

    /**
     * ======================================================
     * Mapping
     * ======================================================
     */

    protected function save_mapping(

        string $lessonpackageid,

        int $quizid,

        int $cmid

    ) {

        global $DB;

        $record = new \stdClass();

        $record->lesson_package_id =

            $lessonpackageid;

        $record->quizid =

            $quizid;

        $record->cmid =

            $cmid;

        $record->timecreated =

            time();

        $record->timemodified =

            time();

        $DB->insert_record(

            "local_rono_quiz_map",

            $record

        );

    }

}