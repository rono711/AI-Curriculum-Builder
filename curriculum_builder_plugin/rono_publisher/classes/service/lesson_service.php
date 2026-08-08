<?php
/**
 * Lesson service for Rono Publisher.
 *
 * Builds the Moodle Page activities belonging to one
 * curriculum elaboration (lesson).
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
 * Service responsible for assembling one lesson/elaboration.
 */
class lesson_service {

    /**
     * Page service.
     *
     * @var page_service
     */
    private $pages;

    /**
     * Constructor.
     */
    public function __construct() {
        $this->pages = new page_service();
    }

    /**
     * Create the main Lesson Content page.
     *
     * This is the main activity for one elaboration.
     * It is not indented.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $title Lesson/elaboration title.
     * @param string $content Lesson content HTML.
     * @param string $description Optional activity description.
     * @return stdClass Course module record.
     */
    public function create_lesson_content(
        int $courseid,
        stdClass $section,
        string $title,
        string $content,
        string $description = ''
    ): stdClass {

        $title = trim($title);

        if ($title === '') {
            throw new moodle_exception(
                'Lesson title cannot be empty.'
            );
        }

        return $this->pages->create_page(
            $courseid,
            $section,
            $title,
            $content,
            $description,
            0
        );
    }

    /**
     * Create the Did You Know? page.
     *
     * This page contains the Gamma slides/embed.
     * It is indented beneath the Lesson Content page.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $content Gamma embed / HTML.
     * @param string $description Optional activity description.
     * @return stdClass Course module record.
     */
    public function create_did_you_know(
        int $courseid,
        stdClass $section,
        string $content,
        string $description = ''
    ): stdClass {

        return $this->pages->create_page(
            $courseid,
            $section,
            'Did You Know?',
            $content,
            $description,
            1
        );
    }

    /**
     * Create the Let's Do It page.
     *
     * This page contains the lesson activities.
     * It is indented beneath the Lesson Content page.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $content Activities HTML.
     * @param string $description Optional activity description.
     * @return stdClass Course module record.
     */
    public function create_activities(
        int $courseid,
        stdClass $section,
        string $content,
        string $description = ''
    ): stdClass {

        return $this->pages->create_page(
            $courseid,
            $section,
            "Let's Do It",
            $content,
            $description,
            1
        );
    }

    /**
     * Create the What We Discovered recap page.
     *
     * It is indented beneath the Lesson Content page.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $content Recap HTML.
     * @param string $description Optional activity description.
     * @return stdClass Course module record.
     */
    public function create_recap(
        int $courseid,
        stdClass $section,
        string $content,
        string $description = ''
    ): stdClass {

        return $this->pages->create_page(
            $courseid,
            $section,
            'What We Discovered',
            $content,
            $description,
            1
        );
    }

    /**
     * Create the non-quiz components of one lesson.
     *
     * This method is for the initial Moodle structure test.
     *
     * Final lesson ordering will be:
     *
     * Lesson Content                  indent 0
     *     Did You Know?               indent 1
     *     Checking Your Thinking      indent 1
     *     Let's Do It                 indent 1
     *     What We Discovered          indent 1
     *
     * The quiz will be created separately by quiz_service
     * between Did You Know? and Let's Do It.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param array $lesson Lesson data.
     * @return array
     */
    public function create_without_quiz(
        int $courseid,
        stdClass $section,
        array $lesson
    ): array {

        if (empty($lesson['title'])) {
            throw new moodle_exception(
                'Lesson title is required.'
            );
        }

        // -----------------------------------------------------
        // 1. Lesson Content / Mission of the Day.
        // indent = 0.
        // -----------------------------------------------------

        $lessoncontent = $this->create_lesson_content(
            $courseid,
            $section,
            $lesson['title'],
            isset($lesson['lessoncontent'])
                ? $lesson['lessoncontent']
                : '',
            isset($lesson['lessondescription'])
                ? $lesson['lessondescription']
                : ''
        );

        // -----------------------------------------------------
        // 2. Did You Know? / Gamma Slides.
        // indent = 1.
        // -----------------------------------------------------

        $didyouknow = $this->create_did_you_know(
            $courseid,
            $section,
            isset($lesson['didyouknow'])
                ? $lesson['didyouknow']
                : '',
            isset($lesson['didyouknowdescription'])
                ? $lesson['didyouknowdescription']
                : ''
        );

        /*
         * -----------------------------------------------------
         * QUIZ WILL BE CREATED HERE IN THE FINAL PUBLISHER.
         *
         * Checking Your Thinking
         * indent = 1
         *
         * question_service:
         *     create Question Bank category
         *     import GIFT/XML
         *     return imported questions
         *
         * quiz_service:
         *     create Quiz
         *     attach questions
         *     indent = 1
         * -----------------------------------------------------
         */

        // -----------------------------------------------------
        // 3. Let's Do It.
        // indent = 1.
        // -----------------------------------------------------

        $activities = $this->create_activities(
            $courseid,
            $section,
            isset($lesson['activities'])
                ? $lesson['activities']
                : '',
            isset($lesson['activitiesdescription'])
                ? $lesson['activitiesdescription']
                : ''
        );

        // -----------------------------------------------------
        // 4. What We Discovered.
        // indent = 1.
        // -----------------------------------------------------

        $recap = $this->create_recap(
            $courseid,
            $section,
            isset($lesson['recap'])
                ? $lesson['recap']
                : '',
            isset($lesson['recapdescription'])
                ? $lesson['recapdescription']
                : ''
        );

        return [
            'lessoncontentcmid' => (int) $lessoncontent->id,
            'didyouknowcmid' => (int) $didyouknow->id,
            'activitiescmid' => (int) $activities->id,
            'recapcmid' => (int) $recap->id,
        ];
    }
}