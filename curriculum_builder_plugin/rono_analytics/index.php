<?php

require_once(__DIR__ . '/../../config.php');

use local_rono_analytics\analytics_client;

$courseid = required_param(
    'courseid',
    PARAM_INT
);

$datefrom = optional_param(
    'date_from',
    '',
    PARAM_TEXT
);

$dateto = optional_param(
    'date_to',
    '',
    PARAM_TEXT
);

$course = get_course($courseid);

require_login($course);

$context = context_course::instance(
    $courseid
);

require_capability(
    'local/rono_analytics:viewcourse',
    $context
);

$PAGE->set_context($context);

$PAGE->set_url(
    new moodle_url(
        '/local/rono_analytics/index.php',
        [
            'courseid' => $courseid,
        ]
    )
);

$PAGE->set_pagelayout('incourse');

$PAGE->set_title(
    get_string(
        'dashboard',
        'local_rono_analytics'
    )
);

$PAGE->set_heading(
    format_string($course->fullname)
);

if ($datefrom === '') {
    $datefrom = gmdate(
        'Y-m-d',
        strtotime('-28 days')
    );
}

if ($dateto === '') {
    $dateto = gmdate('Y-m-d');
}

$datefromapi = (
    $datefrom
    . 'T00:00:00+00:00'
);

$datetoapi = (
    $dateto
    . 'T23:59:59+00:00'
);

$client = new analytics_client();

try {
    $overview = $client->course_overview(
        $courseid,
        (int)$USER->id,
        $datefromapi,
        $datetoapi
    );

    $topics = $client->course_topics(
        $courseid,
        (int)$USER->id,
        $datefromapi,
        $datetoapi
    );

    $history = $client->topic_history(
        $courseid,
        (int)$USER->id,
        $datefromapi,
        $datetoapi,
        7
    );

} catch (Throwable $exception) {
    echo $OUTPUT->header();

    echo $OUTPUT->notification(
        s($exception->getMessage()),
        'notifyproblem'
    );

    echo $OUTPUT->footer();
    exit;
}

echo $OUTPUT->header();

echo html_writer::tag(
    'h2',
    get_string(
        'dashboard',
        'local_rono_analytics'
    )
);

/*
 * Date range.
 */
echo html_writer::start_tag(
    'form',
    [
        'method' => 'get',
        'class' => 'mb-4',
    ]
);

echo html_writer::empty_tag(
    'input',
    [
        'type' => 'hidden',
        'name' => 'courseid',
        'value' => $courseid,
    ]
);

echo html_writer::label(
    'From',
    'rono-date-from',
    false,
    ['class' => 'mr-2']
);

echo html_writer::empty_tag(
    'input',
    [
        'id' => 'rono-date-from',
        'type' => 'date',
        'name' => 'date_from',
        'value' => $datefrom,
        'class' => 'mr-3',
    ]
);

echo html_writer::label(
    'To',
    'rono-date-to',
    false,
    ['class' => 'mr-2']
);

echo html_writer::empty_tag(
    'input',
    [
        'id' => 'rono-date-to',
        'type' => 'date',
        'name' => 'date_to',
        'value' => $dateto,
        'class' => 'mr-3',
    ]
);

echo html_writer::empty_tag(
    'input',
    [
        'type' => 'submit',
        'value' => 'Apply',
        'class' => 'btn btn-primary',
    ]
);

echo html_writer::end_tag('form');


/*
 * Overview cards.
 */
$cards = [
    'Enrolled students' =>
        $overview['enrolled_students']
        ?? 0,

    'Students with activity' =>
        $overview['students_with_activity']
        ?? 0,

    'Quiz attempts' =>
        $overview['attempt_count']
        ?? 0,

    'Average attempt score' =>
        (
            isset(
                $overview[
                    'average_attempt_score'
                ]
            )
            && $overview[
                'average_attempt_score'
            ] !== null
        )
            ? (
                $overview[
                    'average_attempt_score'
                ]
                . '%'
            )
            : 'No data',
];

echo html_writer::start_div(
    'row mb-4'
);

foreach ($cards as $label => $value) {
    echo html_writer::start_div(
        'col-md-3 mb-3'
    );

    echo html_writer::start_div(
        'card h-100'
    );

    echo html_writer::start_div(
        'card-body'
    );

    echo html_writer::tag(
        'div',
        s($label),
        [
            'class' =>
                'text-muted small',
        ]
    );

    echo html_writer::tag(
        'div',
        s((string)$value),
        [
            'class' =>
                'h3 mb-0',
        ]
    );

    echo html_writer::end_div();
    echo html_writer::end_div();
    echo html_writer::end_div();
}

echo html_writer::end_div();



/*
 * Topics needing attention.
 */
echo html_writer::tag(
    'h3',
    'Topics needing attention'
);

$topicrows = $topics['topics'] ?? [];

if (!$topicrows) {
    echo $OUTPUT->notification(
        'No topic evidence is available for this date range.',
        'notifymessage'
    );
} else {
    foreach ($topicrows as $topic) {
        $evidence = (int)(
            $topic['students_with_evidence'] ?? 0
        );

        $struggling = (int)(
            $topic['students_struggling'] ?? 0
        );

        $rate = (float)(
            $topic['difficulty_rate'] ?? 0
        );

        echo html_writer::start_div(
            'card mb-3'
        );

        echo html_writer::start_div(
            'card-body'
        );

        echo html_writer::tag(
            'h4',
            s($topic['parent_code'] ?? 'Topic')
        );

        echo html_writer::tag(
            'p',
            s(
                $struggling
                . ' of '
                . $evidence
                . ' students with evidence need attention ('
                . round($rate, 1)
                . '%).'
            )
        );

        $students = (
            $topic['struggling_students']
            ?? []
        );

        if ($students) {
            echo html_writer::tag(
                'strong',
                'Affected students'
            );

            echo html_writer::start_tag('ul');

            foreach ($students as $student) {
                echo html_writer::tag(
                    'li',
                    s(
                        $student['fullname']
                        ?? ''
                    )
                );
            }

            echo html_writer::end_tag('ul');
        }

        $lessons = (
            $topic['problem_lessons']
            ?? []
        );

        if ($lessons) {
            echo html_writer::tag(
                'strong',
                'Lessons needing attention'
            );

            echo html_writer::start_tag('ul');

            foreach ($lessons as $lesson) {
                $label = (
                    ($lesson['curriculum_code'] ?? '')
                    . ' - '
                    . ($lesson['lesson_title'] ?? '')
                );

                echo html_writer::tag(
                    'li',
                    s($label)
                );
            }

            echo html_writer::end_tag('ul');
        }

        echo html_writer::end_div();
        echo html_writer::end_div();
    }
}

/*
 * Weekly topic history.
 */
echo html_writer::tag(
    'h3',
    'Weekly topic history'
);

$historytopics = $history['topics'] ?? [];

if (!$historytopics) {
    echo $OUTPUT->notification(
        'No historical topic evidence is available.',
        'notifymessage'
    );
} else {
    foreach ($historytopics as $topic) {
        echo html_writer::start_div(
            'card mb-3'
        );

        echo html_writer::start_div(
            'card-body'
        );

        echo html_writer::tag(
            'h4',
            s(
                $topic['parent_code']
                ?? 'Topic'
            )
        );

        echo html_writer::tag(
            'p',
            'Trend: '
            . s(
                $topic['trend']
                ?? 'NO_COMPARISON'
            )
        );

        echo html_writer::start_tag('ul');

        foreach (
            ($topic['points'] ?? [])
            as $point
        ) {
            $pointrate = (
                $point['difficulty_rate']
                ?? null
            );

            if ($pointrate === null) {
                $ratelabel = 'No data';
            } else {
                $ratelabel = (
                    round(
                        (float)$pointrate,
                        1
                    )
                    . '%'
                );
            }

            $date = substr(
                (string)(
                    $point['from']
                    ?? ''
                ),
                0,
                10
            );

            $evidence = (int)(
                $point[
                    'students_with_evidence'
                ]
                ?? 0
            );

            $label = (
                $date
                . ': '
                . $ratelabel
                . ' - evidence '
                . $evidence
            );

            echo html_writer::tag(
                'li',
                s($label)
            );
        }

        echo html_writer::end_tag('ul');

        echo html_writer::end_div();
        echo html_writer::end_div();
    }
}

echo $OUTPUT->footer();
