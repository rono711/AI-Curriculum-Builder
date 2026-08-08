/**
 * Question Bank service for Rono Publisher.
 *
 * Moodle 5.2 Question Bank integration will be implemented
 * after the course structure publishing test is complete.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */


    /*
     *  responsibilities:
     *
     * 1. Create/find a dedicated Question Bank category
     *    for each lesson/elaboration.
     *
     * 2. Import generated GIFT or Moodle XML questions.
     *
     * 3. Use Moodle 5.2 Question Bank APIs rather than
     *    directly inserting question database records.
     *
     * 4. Validate the imported questions.
     *
     * 5. Return the question/bank references required by
     *    quiz_service.
     *
     */


/**
 * Question Bank service for Rono Publisher.
 *
 * Creates a dedicated Question Bank category for each lesson
 * and imports GIFT or Moodle XML questions using Moodle's
 * question-format subsystem.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

use context_course;
use moodle_exception;
use stdClass;

/**
 * Service responsible for Moodle Question Bank operations.
 */
class question_service {

    /**
     * Find or create the Question Bank category belonging to
     * one lesson/elaboration.
     *
     * @param int $courseid Moodle course ID.
     * @param string $lessonname Lesson/elaboration title.
     * @return stdClass Question category record.
     */
    public function find_or_create_lesson_category(
        int $courseid,
        string $lessonname
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->libdir . '/questionlib.php'
        );

        $lessonname = trim($lessonname);

        if ($lessonname === '') {
            throw new moodle_exception(
                'Lesson name cannot be empty when creating a Question Bank category.'
            );
        }

        $context = context_course::instance(
            $courseid
        );

        /*
         * Look only inside this course context.
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
         * Obtain the course's default question category.
         *
         * The lesson category will be created underneath it.
         */
        $defaultcategory = question_get_default_category(
            $context->id,
            true
        );

        if (!$defaultcategory) {
            throw new moodle_exception(
                'Unable to obtain the default Question Bank category for the course.'
            );
        }

        $category = new stdClass();

        $category->name = $lessonname;

        $category->info =
            'Questions automatically published for lesson: '
            . $lessonname;

        $category->infoformat = FORMAT_HTML;

        $category->contextid = $context->id;

        $category->parent = $defaultcategory->id;

        /*
         * Moodle uses sortorder for question categories.
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

        $category->id = $DB->insert_record(
            'question_categories',
            $category
        );

        return $DB->get_record(
            'question_categories',
            ['id' => $category->id],
            '*',
            MUST_EXIST
        );
    }

    /**
     * Import questions for one lesson.
     *
     * Supported initial formats:
     *
     * gift
     * xml
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $category Target Question Bank category.
     * @param string $format Question format.
     * @param string $content GIFT/XML content.
     * @return array
     */
    public function import_questions(
        int $courseid,
        stdClass $category,
        string $format,
        string $content
    ): array {
        global $CFG, $DB;

        require_once(
            $CFG->libdir . '/questionlib.php'
        );

        $format = strtolower(
            trim($format)
        );

        $content = trim($content);

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

        $context = context_course::instance(
            $courseid
        );

        /*
         * Verify that the supplied category belongs to
         * the target course context.
         */
        if (
            (int)$category->contextid !==
            (int)$context->id
        ) {
            throw new moodle_exception(
                'Question category does not belong to the target course.'
            );
        }

        /*
         * Load Moodle's actual question format implementation.
         *
         * GIFT:
         * question/format/gift/format.php
         *
         * XML:
         * question/format/xml/format.php
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

        require_once($formatfile);

        $classname = 'qformat_' . $format;

        if (!class_exists($classname)) {
            throw new moodle_exception(
                'Unable to load Moodle question format class: '
                . $classname
            );
        }

        /*
         * Write the generated question payload to Moodle's
         * temporary directory.
         *
         * qformat import implementations are designed to
         * process question files.
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

        rename(
            $tempfile,
            $importfile
        );

        $written = file_put_contents(
            $importfile,
            $content
        );

        if ($written === false) {

            if (file_exists($importfile)) {
                unlink($importfile);
            }

            throw new moodle_exception(
                'Unable to write temporary question import file.'
            );
        }

        /*
         * Record existing Question Bank entries in this
         * category before importing.
         *
         * After Moodle performs the import we compare the
         * Question Bank entries to determine which ones were
         * created by this operation.
         */
        $beforeentries = $this->get_category_bank_entries(
            (int)$category->id
        );

        try {

            /** @var \qformat_default $qformat */
            $qformat = new $classname();

            /*
             * Configure Moodle's standard question-format
             * importer.
             */
            $qformat->setCategory(
                $category
            );

            $qformat->setContext(
                $context
            );

            $qformat->setFilename(
                $importfile
            );

            /*
             * Do not allow the imported file to override
             * our dedicated lesson category.
             */
            $qformat->setCatfromfile(
                false
            );

            /*
             * Do not create contexts/categories based on
             * category declarations contained in the file.
             */
            $qformat->setContextfromfile(
                false
            );

            /*
             * Fail when unsupported grades are encountered
             * rather than silently changing question grades.
             */
            $qformat->setMatchgrades(
                'error'
            );

            /*
             * Moodle's question-format subsystem performs
             * parsing, validation and saving into the modern
             * Question Bank structures.
             */
            $success = $qformat->importprocess();

            if (!$success) {
                throw new moodle_exception(
                    'Moodle Question Bank import failed.'
                );
            }

        } finally {

            if (file_exists($importfile)) {
                unlink($importfile);
            }
        }

        /*
         * Determine which Question Bank entries were created
         * by this import.
         */
        $afterentries = $this->get_category_bank_entries(
            (int)$category->id
        );

        $newentryids = array_values(
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

        return [
            'categoryid' =>
                (int)$category->id,

            'questionbankentryids' =>
                $newentryids,

            'questioncount' =>
                count($newentryids),
        ];
    }

    /**
     * Create/find the lesson category and import questions.
     *
     * @param int $courseid Moodle course ID.
     * @param string $lessonname Lesson title.
     * @param string $format gift or xml.
     * @param string $content Question payload.
     * @return array
     */
    public function prepare_lesson_questions(
        int $courseid,
        string $lessonname,
        string $format,
        string $content
    ): array {

        $category =
            $this->find_or_create_lesson_category(
                $courseid,
                $lessonname
            );

        $result =
            $this->import_questions(
                $courseid,
                $category,
                $format,
                $content
            );

        $result['category'] = $category;

        return $result;
    }

    /**
     * Return Question Bank entry IDs belonging to a category.
     *
     * Moodle 4+ / 5.x stores the relationship as:
     *
     * question_categories
     *        |
     * question_bank_entries
     *        |
     * question_versions
     *        |
     * question
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
            array_keys($records)
        );
    }
}