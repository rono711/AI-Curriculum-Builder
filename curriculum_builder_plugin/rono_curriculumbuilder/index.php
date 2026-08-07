<?php
// This file is part of Moodle - http://moodle.org/
//
// Rono Curriculum Builder
//
// Publisher Dashboard
//
// Version 4.0
//

require_once(__DIR__ . '/../../config.php');
require_once(__DIR__ . '/lib.php');

require_login();

$context = context_system::instance();

require_capability(
    'local/rono_curriculumbuilder:manage',
    $context
);

$PAGE->set_context($context);

$PAGE->set_url(
    new moodle_url(
        '/local/rono_curriculumbuilder/index.php'
    )
);

$PAGE->set_pagelayout('admin');

$PAGE->set_title(
    'Rono Curriculum Builder'
);

$PAGE->set_heading(
    'Rono Curriculum Builder'
);

echo $OUTPUT->header();

echo $OUTPUT->heading(

    'Rono Curriculum Builder',

    2

);

echo html_writer::tag(

    'p',

    'Publisher Engine Dashboard'

);

$table = new html_table();

$table->head = [

    'Component',

    'Value'

];

global $CFG;

$table->data = [

    [

        'Plugin Version',

        local_rono_curriculumbuilder_plugin_version()

    ],

    [

        'Moodle Version',

        $CFG->release

    ],

    [

        'Plugin Enabled',

        local_rono_curriculumbuilder_is_enabled()

            ? 'Yes'

            : 'No'

    ],

    [

        'Logging',

        local_rono_curriculumbuilder_logging_enabled()

            ? 'Enabled'

            : 'Disabled'

    ],

    [

        'Debug Mode',

        local_rono_curriculumbuilder_debug_enabled()

            ? 'Enabled'

            : 'Disabled'

    ],

    [

        'Publisher Engine',

        local_rono_curriculumbuilder_publisher_url()

    ],

    [

        'Publisher Timeout',

        local_rono_curriculumbuilder_publisher_timeout()

        . ' sec'

    ],

    [

        'External Service',

        local_rono_curriculumbuilder_service_name()

    ],

    [

        'Service Short Name',

        local_rono_curriculumbuilder_service_shortname()

    ]

];

echo html_writer::table(

    $table

);

echo $OUTPUT->heading(

    'Publishing Workflow',

    3

);

echo html_writer::alist([

    'Publisher Engine generates lesson assets.',

    'Publisher Engine connects to Moodle.',

    'Plugin creates or updates the course.',

    'Plugin creates or updates sections.',

    'Plugin publishes Mission of the Day.',

    'Plugin publishes Check Your Thinking.',

    'Plugin publishes Your Turn.',

    'Plugin publishes What We Discovered.'

]);

echo html_writer::tag(

    'p',

    '<strong>Status:</strong> Ready for integration testing.'

);

echo $OUTPUT->footer();