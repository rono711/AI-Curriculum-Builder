<?php
/**
 * Rono Publisher status page.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

require_once(__DIR__ . '/../../config.php');

require_login();

$context = context_system::instance();

$PAGE->set_context($context);

$PAGE->set_url(
    new moodle_url('/local/rono_publisher/index.php')
);

$PAGE->set_pagelayout('admin');

$PAGE->set_title(
    get_string('pluginname', 'local_rono_publisher')
);

$PAGE->set_heading(
    get_string('pluginname', 'local_rono_publisher')
);

echo $OUTPUT->header();

echo $OUTPUT->heading(
    get_string('pluginname', 'local_rono_publisher'),
    2
);

echo html_writer::tag(
    'p',
    'AI Curriculum Lesson Publisher for Moodle.'
);

$table = new html_table();

$table->head = [
    'Component',
    'Status',
];

$table->data = [
    [
        'Plugin',
        'Rono Publisher',
    ],
    [
        'External Function',
        'local_rono_publisher_publish_lesson',
    ],
    [
        'Strand',
        'Moodle Section',
    ],
    [
        'Sub-strand',
        'Moodle Subsection',
    ],
    [
        'Content Description',
        'Text & Media',
    ],
    [
        'Lesson Content',
        'Page Activity',
    ],
    [
        'Did You Know?',
        'Page Activity / Gamma Slides',
    ],
    [
        'Checking Your Thinking',
        'Quiz Activity - pending structural test',
    ],
    [
        "Let's Do It",
        'Page Activity',
    ],
    [
        'What We Discovered',
        'Page Activity',
    ],
];

echo html_writer::table($table);

echo $OUTPUT->heading(
    'Publishing Structure',
    3
);

echo html_writer::alist([
    'Strand becomes a Moodle Section.',
    'Sub-strand becomes a Moodle Subsection.',
    'Content Description becomes the first Text & Media activity.',
    'Each elaboration becomes a Lesson Content Page.',
    'Did You Know? is indented beneath the Lesson Content Page.',
    'Checking Your Thinking will be an indented Quiz Activity.',
    "Let's Do It is an indented Page Activity.",
    'What We Discovered is an indented Page Activity.',
]);

echo html_writer::tag(
    'p',
    '<strong>Current development stage:</strong> '
    . 'Structural publishing test before Question Bank and Quiz integration.'
);

echo $OUTPUT->footer();