<?php
/**
 * Question Bank service for Rono Publisher.
 *
 * Creates a dedicated Question Bank category inside the
 * Moodle Quiz module context and imports GIFT or Moodle XML
 * questions using Moodle 5.2's question-format subsystem.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

use context_module;
use moodle_exception;
use stdClass;

/**
 * Service responsible for Moodle Question Bank operations.
 */
class question_service {

    /**
     * Find or create the Question Bank category for one lesson.
     *
     * The category belongs to the module context of the lesson's
     * Checking Your Thinking Quiz.
     *
     * @param int $quizcmid Moodle Quiz course-module ID.
     * @param string $lessonname Lesson/elaboration title.
     * @return stdClass
     */
    public function find_or_create_lesson_category(
        int $quizcmid,
        string $lessonname
    ): stdClass {
        global $DB;

        $lessonname = trim($lessonname);

        if ($lessonname === '') {
            throw new moodle_exception(
                'Lesson name cannot be empty when creating a Question Bank category.'
            );
        }

        /*
         * Moodle 5.2 question-format imports require the target
         * question category to belong to CONTEXT_MODULE.
         */
        $context = context_module::instance(
            $quizcmid
        );

        /*
         * Look for an existing category belonging to this
         * exact Quiz module context.
         */
        $existing = $DB->get_record(
            'question_categories',
            [
                'contextid' => $context->id,
                'name' => $lessonname,
            ]
        );

        if ($existing) {
            return $existing;
        }

        /*
         * Create the lesson Question Bank category.
         */
        $category = new stdClass();

        $category->name =
            $lessonname;

        $category->info =
            'Questions automatically published for lesson: '
            . $lessonname;

        $category->infoformat =
            FORMAT_HTML;

        $category->contextid =
            (int)$context->id;

        /*
         * Top-level category inside the Quiz module context.
         */
        $category->parent = 0;

        /*
         * Determine next category sort order.
         */
        $maxsortorder = $DB->get_field_sql(
            "
                SELECT MAX(sortorder)
                  FROM {question_categories}
                 WHERE contextid = :contextid
            ",
            [
                'contextid' => $context->id,
            ]
        );

        $category->sortorder =
            ((int)$maxsortorder) + 1;

        $category->id =
            $DB->insert_record(
                'question_categories',
                $category
            );

        return $DB->get_record(
            'question_categories',
            [
                'id' => $category->id,
            ],
            '*',
            MUST_EXIST
        );
    }

    /**
     * Import GIFT or Moodle XML questions.
     *
     * @param int $courseid Moodle course ID.
     * @param int $quizcmid Moodle Quiz course-module ID.
     * @param stdClass $category Target Question Bank category.
     * @param string $format gift or xml.
     * @param string $content Question content.
     * @return array
     */
    public function import_questions(
        int $courseid,
        int $quizcmid,
        stdClass $category,
        string $format,
        string $content
    ): array {
        global $CFG, $DB;

        /*
         * Moodle Question API.
         */
        require_once(
            $CFG->libdir . '/questionlib.php'
        );

        /*
         * qformat_default.
         */
        require_once(
            $CFG->dirroot . '/question/format.php'
        );

        $format = strtolower(
            trim($format)
        );

        $content = trim(
            $content
        );

        if ($content === '') {
            throw new moodle_exception(
                'Question content cannot be empty.'
            );
        }

        if (
            $format !== 'gift' &&
            $format !== 'xml'
        ) {
            throw new moodle_exception(
                'Unsupported question format. Supported formats are gift and xml.'
            );
        }

        /*
         * Obtain target course.
         *
         * Moodle's own question importer calls setCourse().
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
         * Obtain Quiz module context.
         */
        $context = context_module::instance(
            $quizcmid
        );

        /*
         * Verify that the category belongs to this exact
         * module context.
         */
        if (
            (int)$category->contextid !==
            (int)$context->id
        ) {
            throw new moodle_exception(
                'Question category does not belong to the target Quiz module context.'
            );
        }

        /*
         * Load requested Moodle question-format plugin.
         */
        $formatfile =
            $CFG->dirroot
            . '/question/format/'
            . $format
            . '/format.php';

        if (!file_exists($formatfile)) {
            throw new moodle_exception(
                'Moodle question format plugin is not available: '
                . $format
            );
        }

        require_once(
            $formatfile
        );

        $classname =
            'qformat_' . $format;

        if (!class_exists($classname)) {
            throw new moodle_exception(
                'Unable to load Moodle question format class: '
                . $classname
            );
        }

        /*
         * Create temporary import file.
         */
        $extension =
            ($format === 'xml')
                ? '.xml'
                : '.gift';

        $tempfile = tempnam(
            $CFG->tempdir,
            'rono_question_import_'
        );

        if ($tempfile === false) {
            throw new moodle_exception(
                'Unable to create temporary question import file.'
            );
        }

        $importfile =
            $tempfile . $extension;

        if (!rename(
            $tempfile,
            $importfile
        )) {
            @unlink($tempfile);

            throw new moodle_exception(
                'Unable to prepare temporary question import file.'
            );
        }

        $written = file_put_contents(
            $importfile,
            $content
        );

        if ($written === false) {

            @unlink(
                $importfile
            );

            throw new moodle_exception(
                'Unable to write temporary question import file.'
            );
        }

        /*
         * Record existing Question Bank entries before import.
         */
        $beforeentries =
            $this->get_category_bank_entries(
                (int)$category->id
            );
        /*
 * Suppress Moodle question importer HTML so the
 * Web Service response remains pure JSON.
 */
$originaloblevel = ob_get_level();
ob_start();
        try {

            /*
             * Instantiate Moodle's format importer.
             */
            $qformat =
                new $classname();

            /*
             * Moodle 5.2 configuration.
             *
             * These calls mirror the API exposed by the
             * installed question/format.php.
             */

            $qformat->setCategory(
                $category
            );

            /*
             * IMPORTANT:
             *
             * Moodle 5.2 uses setContexts(), plural.
             *
             * setContext() does not exist.
             */
            $qformat->setContexts(
                [
                    $context,
                ]
            );

            /*
             * Moodle's own importer supplies the course.
             */
            $qformat->setCourse(
                $course
            );

            $qformat->setFilename(
                $importfile
            );

            /*
             * Real filename is used by the question-format
             * subsystem for reporting/display purposes.
             */
            $qformat->setRealfilename(
                basename($importfile)
            );

            /*
             * Keep generated questions in our dedicated
             * lesson category.
             */
            $qformat->setCatfromfile(
                false
            );

            /*
             * Do not allow imported content to change
             * the target context.
             */
            $qformat->setContextfromfile(
                false
            );

            /*
             * Reject unsupported grades rather than
             * silently altering them.
             */
            $qformat->setMatchgrades(
                'error'
            );

            /*
             * Stop when a question import error occurs.
             */
            $qformat->setStoponerror(
                true
            );

            /*
             * Moodle import preprocessing.
             */
            if (!$qformat->importpreprocess()) {
                throw new moodle_exception(
                    'Moodle Question Bank import preprocessing failed.'
                );
            }

            /*
             * IMPORTANT:
             *
             * Moodle 5.2 importprocess() accepts NO category
             * parameter.
             *
             * The target category was already supplied through
             * setCategory().
             */
            $success =
                $qformat->importprocess();

            if (!$success) {

                $importoutput = '';

                if (ob_get_level() > $originaloblevel) {
                    $importoutput = ob_get_contents();
                }

                $importoutput = trim(
                    strip_tags(
                        (string)$importoutput
                    )
                );

                if ($importoutput === '') {
                    $importoutput =
                        'No detailed importer output was returned.';
                }

                throw new moodle_exception(
                    'Moodle Question Bank import failed: ' .
                    $importoutput
                );
            }
            /*
             * Moodle import postprocessing.
             */
            if (!$qformat->importpostprocess()) {
                throw new moodle_exception(
                    'Moodle Question Bank import postprocessing failed.'
                );
            }

        } finally {
            /*
            * Suppress all HTML/progress output generated
            * by Moodle's question importer.
            */
            while (ob_get_level() > $originaloblevel) {
               ob_end_clean();
            }
            /*
             * Always remove temporary import file.
             */
            if (file_exists($importfile)) {
                @unlink(
                    $importfile
                );
            }
        }

        /*
         * Determine which Question Bank entries were created.
         */
        $afterentries =
            $this->get_category_bank_entries(
                (int)$category->id
            );

        $newentryids =
            array_values(
                array_diff(
                    $afterentries,
                    $beforeentries
                )
            );

        if (empty($newentryids)) {
            throw new moodle_exception(
                'Question import completed but no new Question Bank entries were found.'
            );
        }

        /*
         * Resolve latest usable Moodle question IDs.
         */
        $questionids =
            $this->get_latest_question_ids(
                $newentryids
            );

        /*
         * Build authoritative Moodle question mappings.
         */
        $questionmappings =
            $this->get_question_mappings(
                $newentryids,
                $questionids
            );

        return [

            'categoryid' =>
                (int)$category->id,

            'contextid' =>
                (int)$context->id,

            'questionbankentryids' =>
                array_values(
                    array_map(
                        'intval',
                        $newentryids
                    )
                ),

            'questionids' =>
                array_values(
                    array_map(
                        'intval',
                        $questionids
                    )
                ),

            'questions' =>
                $questionmappings,

            'questioncount' =>
                count($newentryids),
        ];
    }

    /**
     * Prepare all questions for one lesson.
     *
     * @param int $courseid Moodle course ID.
     * @param int $quizcmid Quiz course-module ID.
     * @param string $lessonname Lesson title.
     * @param string $format gift or xml.
     * @param string $content Question content.
     * @return array
     */
    public function prepare_lesson_questions(
        int $courseid,
        int $quizcmid,
        string $lessonname,
        string $format,
        string $content
    ): array {

        /*
         * Create/find category in Quiz module context.
         */
        $category =
            $this->find_or_create_lesson_category(
                $quizcmid,
                $lessonname
            );

        /*
         * Import questions.
         */
        $result =
            $this->import_questions(
                $courseid,
                $quizcmid,
                $category,
                $format,
                $content
            );

        $result['category'] =
            $category;

        return $result;
    }

    /**
     * Return Question Bank entry IDs belonging to a category.
     *
     * @param int $categoryid Question category ID.
     * @return array
     */
    private function get_category_bank_entries(
        int $categoryid
    ): array {
        global $DB;

        $records = $DB->get_records(
            'question_bank_entries',
            [
                'questioncategoryid' =>
                    $categoryid,
            ],
            'id ASC',
            'id'
        );

        return array_map(
            'intval',
            array_keys(
                $records
            )
        );
    }

    /**
     * Build authoritative mappings for imported questions.
     *
     * @param array $entryids Question Bank entry IDs.
     * @param array $questionids Moodle question IDs.
     * @return array
     */
    private function get_question_mappings(
        array $entryids,
        array $questionids
    ): array {
        global $DB;

        if (count($entryids) !== count($questionids)) {
            throw new moodle_exception(
                'Question Bank entry count does not match question ID count.'
            );
        }

        $mappings = [];

        foreach ($questionids as $index => $questionid) {
            $question =
                $DB->get_record(
                    'question',
                    [
                        'id' => (int)$questionid,
                    ],
                    'id,name,qtype',
                    MUST_EXIST
                );

            $questionkey =
                trim(
                    (string)$question->name
                );

            if ($questionkey === '') {
                throw new moodle_exception(
                    'Imported Moodle question has an empty name: '
                    . (int)$questionid
                );
            }

            $mappings[] = [
                'questionkey' =>
                    $questionkey,

                'questionid' =>
                    (int)$question->id,

                'questionbankentryid' =>
                    (int)$entryids[$index],

                'qtype' =>
                    (string)$question->qtype,
            ];
        }

        return $mappings;
    }

    /**
     * Resolve latest usable question IDs.
     *
     * @param array $entryids Question Bank entry IDs.
     * @return array
     */
    private function get_latest_question_ids(
        array $entryids
    ): array {
        global $DB;

        $questionids = [];

        foreach ($entryids as $entryid) {

            $sql = "
                SELECT qv.id,
                       qv.questionid,
                       qv.version,
                       qv.status
                  FROM {question_versions} qv
                 WHERE qv.questionbankentryid = :entryid
                   AND qv.status <> :draftstatus
              ORDER BY qv.version DESC
            ";

            $versions =
                $DB->get_records_sql(
                    $sql,
                    [
                        'entryid' =>
                            (int)$entryid,

                        'draftstatus' =>
                            'draft',
                    ],
                    0,
                    1
                );

            if (empty($versions)) {
                throw new moodle_exception(
                    'Unable to resolve a usable question version for Question Bank entry '
                    . (int)$entryid
                );
            }

            $version =
                reset($versions);

            $questionids[] =
                (int)$version->questionid;
        }

        return $questionids;
    }
}
