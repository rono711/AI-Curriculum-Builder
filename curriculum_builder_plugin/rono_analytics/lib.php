<?php

defined('MOODLE_INTERNAL') || die();

function local_rono_analytics_extend_navigation_course(
    navigation_node $navigation,
    stdClass $course,
    context_course $context
): void {
    if (!has_capability(
        'local/rono_analytics:viewcourse',
        $context
    )) {
        return;
    }

    $url = new moodle_url(
        '/local/rono_analytics/index.php',
        [
            'courseid' => $course->id,
        ]
    );

    $navigation->add(
        get_string(
            'dashboard',
            'local_rono_analytics'
        ),
        $url,
        navigation_node::TYPE_CUSTOM,
        null,
        'ronoanalytics'
    );
}
