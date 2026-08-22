<?php
/**
 * Page and Text & Media service for Rono Publisher.
 *
 * Creates:
 * - Text & Media activities for curriculum content descriptions.
 * - Moodle Page activities for lesson components.
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
 * Service responsible for Text & Media and Page activities.
 */
class page_service {

    /**
     * Find or create the Content Description Text & Media activity.
     *
     * This activity is placed as the first curriculum item inside
     * the delegated subsection.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $contentdescription Curriculum content description.
     * @return stdClass Created or existing course module record.
     */
    public function find_or_create_content_description(
        int $courseid,
        stdClass $section,
        string $contentdescription,
        string $parentcode,
        string $contentdescriptionimagename,
        string $contentdescriptionimage
    ): stdClass {
        global $DB;

        $contentdescription = trim($contentdescription);
        $parentcode = trim($parentcode);

        if ($contentdescription === '') {
            throw new moodle_exception(
                'Content description cannot be empty.'
            );
        }

        if ($parentcode === '') {
            throw new moodle_exception(
                'Parent curriculum code cannot be empty.'
            );
        }

        /*
         * Moodle still uses the internal module name "label"
         * for the activity presented as Text & Media.
         */
        $labelmodule = $DB->get_record(
            'modules',
            ['name' => 'label'],
            '*',
            MUST_EXIST
        );

        /*
         * Look for the existing Content Description Text & Media
         * inside this exact delegated subsection.
         *
         * Compare only the visible H3 text. The image and other
         * HTML must not cause a duplicate Content Description.
         */
        $sql = "
            SELECT
                cm.id,
                cm.instance,
                l.name,
                l.intro
            FROM {course_modules} cm
            JOIN {label} l
              ON l.id = cm.instance
            WHERE cm.course = :courseid
              AND cm.section = :sectionid
              AND cm.module = :moduleid
        ";

        $records = $DB->get_records_sql(
            $sql,
            [
                'courseid' => $courseid,
                'sectionid' => $section->id,
                'moduleid' => $labelmodule->id,
            ]
        );

        /*
         * Each lesson/elaboration has its own Text & Media activity.
         * The curriculum code is the stable lesson-level identity.
         */
        $targettext = trim(
            $parentcode
        );

        foreach ($records as $record) {

            $existingname = trim(
                (string)$record->name
            );

            /*
             * Curriculum code is the stable lesson-level identity.
             * Use an exact case-insensitive match so E1 cannot
             * accidentally match E10.
             */
            if (
                $targettext !== ''
                &&
                mb_strtolower(
                    $existingname,
                    'UTF-8'
                )
                ===
                mb_strtolower(
                    $targettext,
                    'UTF-8'
                )
            ) {
				
				
		return $this->update_text_and_media(
                    $courseid,
                    $record,
                    $contentdescription,
                    $parentcode,
                    $contentdescriptionimagename,
                    $contentdescriptionimage
                );
            }
        }

        return $this->create_text_and_media(
            $courseid,
            $section,
            $contentdescription,
            $parentcode,
            $contentdescriptionimagename,
            $contentdescriptionimage
        );
	}

    /**
     * Create the curriculum Content Description as Text & Media.
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $contentdescription Content description HTML/text.
     * @return stdClass Course module record.
     */
    private function create_text_and_media(
        int $courseid,
        stdClass $section,
        string $contentdescription,
        string $parentcode,
        string $contentdescriptionimagename,
        string $contentdescriptionimage
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        $module = $DB->get_record(
            'modules',
            ['name' => 'label'],
            '*',
            MUST_EXIST
        );

        /*
         * Capitalise first visible character.
         */
        $contentdescription = $this->capitalise_first(
            $contentdescription
        );

        /*
         * First create the Text & Media activity.
         * We need its module context before storing the image.
         */
        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'label';
        $moduleinfo->module = $module->id;
        $moduleinfo->course = $course->id;
        $moduleinfo->section = $section->section;

        /*
         * Stable internal identity for this lesson banner.
         */
        $moduleinfo->name =
            $parentcode;

        /*
         * Temporary H3 only.
         * The image is attached immediately after creation.
         */
        $moduleinfo->intro =
            '<h3 style="' .
            'margin: 0 0 14px 0; ' .
            'color: #1F4E5F; ' .
            'font-weight: 600; ' .
            'line-height: 1.4;' .
            '">' .
            s($contentdescription) .
            '</h3>';

        $moduleinfo->introformat = FORMAT_HTML;

        $moduleinfo->visible = 1;
        $moduleinfo->groupmode = 0;
        $moduleinfo->groupingid = 0;
        $moduleinfo->completion = 0;

        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created)
            ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Content Description Text & Media activity.'
            );
        }

        $cm = $DB->get_record(
            'course_modules',
            [
                'id' =>
                    (int)$created->coursemodule
            ],
            '*',
            MUST_EXIST
        );

        $label = $DB->get_record(
            'label',
            [
                'id' =>
                    (int)$cm->instance
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Store image and build final Text & Media HTML.
         */
        $intro = $this->build_content_description_html(
            $courseid,
            (int)$cm->id,
            $contentdescription,
            $parentcode,
            $contentdescriptionimagename,
            $contentdescriptionimage
        );

        $label->intro = $intro;
        $label->introformat = FORMAT_HTML;

        $DB->update_record(
            'label',
            $label
        );

        rebuild_course_cache(
            $courseid,
            true
        );

        return $cm;
    }
	
	    private function update_text_and_media(
        int $courseid,
        stdClass $record,
        string $contentdescription,
        string $parentcode,
        string $contentdescriptionimagename,
        string $contentdescriptionimage
    ): stdClass {
        global $DB;

        $cm = $DB->get_record(
            'course_modules',
            ['id' => (int)$record->id],
            '*',
            MUST_EXIST
        );

        $label = $DB->get_record(
            'label',
            ['id' => (int)$cm->instance],
            '*',
            MUST_EXIST
        );

        $contentdescription = $this->capitalise_first(
            $contentdescription
        );

        /*
         * Preserve the curriculum code as the stable internal
         * identity when this lesson banner is updated.
         */
        $label->name =
            $parentcode;

        $label->intro =
            $this->build_content_description_html(
                $courseid,
                (int)$cm->id,
                $contentdescription,
                $parentcode,
                $contentdescriptionimagename,
                $contentdescriptionimage
            );

        $label->introformat = FORMAT_HTML;

        $DB->update_record(
            'label',
            $label
        );

        rebuild_course_cache(
            $courseid,
            true
        );

        return $cm;
		}

	    private function capitalise_first(
        string $text
    ): string {

        $text = trim($text);

        if ($text === '') {
            return '';
        }

        return
            mb_strtoupper(
                mb_substr(
                    $text,
                    0,
                    1,
                    'UTF-8'
                ),
                'UTF-8'
            )
            .
            mb_substr(
                $text,
                1,
                null,
                'UTF-8'
            );
		}


	private function build_content_description_html(
        int $courseid,
        int $cmid,
        string $contentdescription,
        string $parentcode,
        string $contentdescriptionimagename,
        string $contentdescriptionimage
     ): string {
        

        $context = \context_module::instance(
            $cmid
        );

        $decoded = base64_decode(
            $contentdescriptionimage,
            true
        );

        if ($decoded === false || $decoded === '') {
            throw new moodle_exception(
                'Unable to decode Content Description image.'
            );
        }

        /*
         * Enforce our own safe filename.
         * Do not trust the incoming filename for identity.
         */
        $filename =
            clean_param(
                $parentcode,
                PARAM_ALPHANUMEXT
            )
            .
            '_content_description.png';

        /*
         * Confirm incoming name represents the expected PNG.
         */
        if (
            strtolower(
                pathinfo(
                    $contentdescriptionimagename,
                    PATHINFO_EXTENSION
                )
            ) !== 'png'
        ) {
            throw new moodle_exception(
                'Content Description image must be a PNG.'
            );
        }

        $fs = get_file_storage();

        /*
         * Replace the previous generated image if this
         * Content Description is being updated.
         */
        $oldfile = $fs->get_file(
            $context->id,
            'mod_label',
            'intro',
            0,
            '/',
            $filename
        );

        if ($oldfile) {
            $oldfile->delete();
        }

        $filerecord = [
            'contextid' =>
                $context->id,

            'component' =>
                'mod_label',

            'filearea' =>
                'intro',

            'itemid' =>
                0,

            'filepath' =>
                '/',

            'filename' =>
                $filename,
        ];

        $fs->create_file_from_string(
            $filerecord,
            $decoded
        );

        $heading =
            '<h3 style="' .
            'margin: 0 0 14px 0; ' .
            'color: #1F4E5F; ' .
            'font-weight: 600; ' .
            'line-height: 1.4;' .
            '">' .
            '<strong>' .
            s($parentcode) .
            '</strong> — ' .
            s($contentdescription) .
            '</h3>';

        $image =
            '<p>' .
            '<img src="@@PLUGINFILE@@/' .
            s($filename) .
            '" alt="" ' .
            'style="max-width: 100%; height: auto;">' .
            '</p>';

        return $heading . $image;
			}


	
	
	
	
	
	/**
     * Create a Moodle Page activity.
     *
     * Used for:
     *
     * Lesson Content / Mission of the Day
     * Did You Know?
     * Let's Do It
     * What We Discovered
     *
     * @param int $courseid Moodle course ID.
     * @param stdClass $section Delegated subsection section.
     * @param string $name Page activity title.
     * @param string $content Page HTML.
     * @param string $description Activity description.
     * @param int $indent Moodle course-page indentation level.
     * @return stdClass Course module record.
     */
    public function create_page(
        int $courseid,
        stdClass $section,
        string $name,
        string $content,
        string $description = '',
        int $indent = 0
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        $name = trim($name);

        if ($name === '') {
            throw new moodle_exception(
                'Page activity name cannot be empty.'
            );
        }

        if ($indent < 0) {
            $indent = 0;
        }

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        $module = $DB->get_record(
            'modules',
            ['name' => 'page'],
            '*',
            MUST_EXIST
        );

        $moduleinfo = new stdClass();

        $moduleinfo->modulename = 'page';
        $moduleinfo->module = $module->id;

        $moduleinfo->course = $course->id;
        $moduleinfo->section = $section->section;

        $moduleinfo->name = $name;

        /*
         * Activity description.
         */
       $moduleinfo->intro = $description;
       $moduleinfo->introformat = FORMAT_HTML;

        /*
         * Display the generated activity description
         * directly on the Moodle course page.
       */
        $moduleinfo->showdescription = 1;

        /*
         * Actual Page body.
         */
        $moduleinfo->content = $content;
        $moduleinfo->contentformat = FORMAT_HTML;

        /*
         * Page display settings.
         *
         * 5 = Display page name.
         * 10 = Display page description.
         */
        $moduleinfo->display = 5;

        $moduleinfo->visible = 1;

        $moduleinfo->groupmode = 0;
        $moduleinfo->groupingid = 0;
        $moduleinfo->completion = 0;

        $created = add_moduleinfo(
            $moduleinfo,
            $course
        );

        if (
            empty($created) ||
            empty($created->coursemodule)
        ) {
            throw new moodle_exception(
                'Unable to create Moodle Page activity.'
            );
        }

        $cmid = (int)$created->coursemodule;

        /*
         * Moodle stores activity indentation on course_modules.
         *
         * Lesson Content:
         *     indent = 0
         *
         * Did You Know?
         * Quiz
         * Let's Do It
         * What We Discovered:
         *     indent = 1
         */
        if ($indent > 0) {
            $DB->set_field(
                'course_modules',
                'indent',
                $indent,
                ['id' => $cmid]
            );
        }

        

        return $DB->get_record(
            'course_modules',
            ['id' => $cmid],
            '*',
            MUST_EXIST
        );
    }
    /**
     * Update an existing Moodle Page activity in place.
     *
     * Safety:
     * - Exact CMID is required.
     * - CMID must belong to the supplied course.
     * - CMID must be mod_page.
     * - Existing Page instance is updated.
     * - No new course module is created.
     *
     * @param int $courseid Moodle course ID.
     * @param int $cmid Existing Page course-module ID.
     * @param string $content Replacement Page HTML.
     * @param string|null $description Optional replacement description.
     * @return stdClass Existing course module.
     */
    /**
     * Update an existing elaboration Text & Media banner in place.
     *
     * Uses the exact existing CMID and preserves the curriculum
     * code as the internal label identity.
     *
     * NEW and UPDATE share build_content_description_html(),
     * ensuring identical learner-facing heading/image layout.
     */
    public function update_elaboration_banner(
        int $courseid,
        int $cmid,
        string $curriculumcode,
        string $parentcode,
        string $contentdescription,
        string $elaboration,
        string $imagename,
        string $image
    ): stdClass {
        global $DB;

        $curriculumcode = trim($curriculumcode);
        $parentcode = trim($parentcode);
        $contentdescription = trim($contentdescription);
        $elaboration = trim($elaboration);

        if ($courseid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course ID.'
            );
        }

        if ($cmid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course module ID.'
            );
        }

        if ($curriculumcode === '') {
            throw new moodle_exception(
                'Curriculum code cannot be empty.'
            );
        }

        if ($parentcode === '') {
            throw new moodle_exception(
                'Parent code cannot be empty.'
            );
        }

        if ($contentdescription === '') {
            throw new moodle_exception(
                'Content Description cannot be empty.'
            );
        }

        if ($elaboration === '') {
            throw new moodle_exception(
                'Curriculum elaboration cannot be empty.'
            );
        }

        $course = $DB->get_record(
            'course',
            ['id' => $courseid],
            '*',
            MUST_EXIST
        );

        $cm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
            ],
            '*',
            MUST_EXIST
        );

        $module = $DB->get_record(
            'modules',
            ['id' => $cm->module],
            '*',
            MUST_EXIST
        );

        if ($module->name !== 'label') {
            throw new moodle_exception(
                'Target course module is not Text & Media.'
            );
        }

        $label = $DB->get_record(
            'label',
            ['id' => $cm->instance],
            '*',
            MUST_EXIST
        );

        $currentidentity = mb_strtolower(
            trim((string)$label->name),
            'UTF-8'
        );

        $parentidentity = mb_strtolower(
            $parentcode,
            'UTF-8'
        );

        $curriculumidentity = mb_strtolower(
            $curriculumcode,
            'UTF-8'
        );

        /*
         * Legacy banners stored the shortened Content Description
         * in label.name before parent-code identities were introduced.
         */
        $legacyidentity = mb_strtolower(
            shorten_text(
                trim(strip_tags($contentdescription)),
                100
            ),
            'UTF-8'
        );

        /*
         * Moodle may derive a legacy label name from the rendered HTML.
         * Confirm the exact expected Content Description is present
         * before treating that banner as the requested curriculum item.
         */
        $legacyintro = mb_strtolower(
            trim(
                preg_replace(
                    '/\s+/u',
                    ' ',
                    html_entity_decode(
                        strip_tags((string)$label->intro),
                        ENT_QUOTES | ENT_HTML5,
                        'UTF-8'
                    )
                )
            ),
            'UTF-8'
        );

        $legacydescription = mb_strtolower(
            trim(preg_replace('/\s+/u', ' ', $contentdescription)),
            'UTF-8'
        );

        $legacyintromatch =
            $legacydescription !== ''
            &&
            mb_strpos(
                $legacyintro,
                $legacydescription,
                0,
                'UTF-8'
            ) !== false;

        if (
            $currentidentity !== $parentidentity
            &&
            $currentidentity !== $curriculumidentity
            &&
            $currentidentity !== $legacyidentity
            &&
            !$legacyintromatch
        ) {
            throw new moodle_exception(
                'Text & Media curriculum identity does not match.'
            );
        }

        /*
         * Preserve the specific elaboration Curriculum ID.
         */
        $label->name = $curriculumcode;

        $elaboration =
            $this->capitalise_first(
                $elaboration
            );

        /*
         * Use exactly the same renderer as NEW publication.
         */
        $label->intro =
            $this->build_content_description_html(
                $courseid,
                $cmid,
                $elaboration,
                $parentcode,
                $imagename,
                $image
            );

        $label->introformat = FORMAT_HTML;

        $DB->update_record(
            'label',
            $label
        );

        rebuild_course_cache(
            $courseid,
            true
        );

        return $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
                'instance' => $label->id,
            ],
            '*',
            MUST_EXIST
        );
    }


    public function update_page(
        int $courseid,
        int $cmid,
        string $content,
        ?string $description = null
    ): stdClass {
        global $CFG, $DB;

        require_once(
            $CFG->dirroot . '/course/modlib.php'
        );

        if ($courseid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course ID.'
            );
        }

        if ($cmid <= 0) {
            throw new moodle_exception(
                'Invalid Moodle course module ID.'
            );
        }

        /*
         * Exact target course.
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
         * Exact target course module.
         */
        $cm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Verify target is really mod_page.
         */
        $module = $DB->get_record(
            'modules',
            [
                'id' => $cm->module,
            ],
            '*',
            MUST_EXIST
        );

        if ($module->name !== 'page') {
            throw new moodle_exception(
                'Target course module is not a Moodle Page.'
            );
        }

        /*
         * Verify the underlying Page instance.
         */
        $page = $DB->get_record(
            'page',
            [
                'id' => $cm->instance,
                'course' => $course->id,
            ],
            '*',
            MUST_EXIST
        );

        /*
         * Ask Moodle for the existing module information.
         */
        [
            $existingcm,
            $context,
            $existingmodule,
            $moduleinfo,
            $section
        ] = get_moduleinfo_data(
            $cm,
            $course
        );

        /*
         * Defensive identity checks.
         */
        if ((int)$existingcm->id !== $cmid) {
            throw new moodle_exception(
                'Moodle returned an unexpected course module.'
            );
        }

        if ($existingmodule->name !== 'page') {
            throw new moodle_exception(
                'Validated Moodle module is not a Page.'
            );
        }

        /*
         * Preserve existing Page name.
         */
        $moduleinfo->name =
            $page->name;

        /*
         * Moodle 5.2 mod_page update contract.
         *
         * page_update_instance() reads the Page body from:
         *
         * $data->page['itemid']
         * $data->page['text']
         * $data->page['format']
         */
        $moduleinfo->page = [
            'itemid' => 0,
            'text' => $content,
            'format' => FORMAT_HTML,
        ];

        /*
         * Keep direct content fields populated too.
         */
        $moduleinfo->content =
            $content;

        $moduleinfo->contentformat =
            FORMAT_HTML;

        /*
         * Preserve existing Page-specific display options.
         */
        $displayoptions = [];

        if (!empty($page->displayoptions)) {
            $decodedoptions =
                unserialize($page->displayoptions);

            if (is_array($decodedoptions)) {
                $displayoptions =
                    $decodedoptions;
            }
        }

        $moduleinfo->display =
            $page->display;

        $moduleinfo->printintro =
            $displayoptions['printintro']
            ?? 0;

        $moduleinfo->printlastmodified =
            $displayoptions['printlastmodified']
            ?? 0;

        $moduleinfo->popupwidth =
            $displayoptions['popupwidth']
            ?? 620;

        $moduleinfo->popupheight =
            $displayoptions['popupheight']
            ?? 450;

        /*
         * Preserve existing description unless a replacement
         * description was explicitly supplied.
         */
        if ($description !== null) {

            if (
                isset($moduleinfo->introeditor) &&
                is_array($moduleinfo->introeditor)
            ) {
                $moduleinfo->introeditor['text'] =
                    $description;

                $moduleinfo->introeditor['format'] =
                    FORMAT_HTML;
            }

            $moduleinfo->intro =
                $description;

            $moduleinfo->introformat =
                FORMAT_HTML;
        }

        /*
         * Critical existing Moodle identity.
         */
        $moduleinfo->coursemodule =
            $cmid;

        $moduleinfo->instance =
            $page->id;

        $moduleinfo->course =
            $course->id;

        $moduleinfo->module =
            $module->id;

        $moduleinfo->modulename =
            'page';
        /*
         * update_moduleinfo() triggers course_module_updated
         * using the $cm object.
         *
         * Because $cm was loaded directly from the
         * course_modules table, Moodle's derived "modname"
         * property is not present automatically.
         */
        $cm->modname =
            'page';
		
		/*
         * Update the EXISTING Moodle activity.
         *
         * No add_moduleinfo() call occurs here.
         */
        update_moduleinfo(
            $cm,
            $moduleinfo,
            $course
        );

        /*
         * Verify the same CMID still points to the same
         * Page instance after the update.
         */
        $updatedcm = $DB->get_record(
            'course_modules',
            [
                'id' => $cmid,
                'course' => $course->id,
                'instance' => $page->id,
            ],
            '*',
            MUST_EXIST
        );

        return $updatedcm;
    }

}
