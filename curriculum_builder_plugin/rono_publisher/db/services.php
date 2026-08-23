<?php
/**
 * External service definitions for Rono Publisher.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$functions = [

    'local_rono_publisher_publish_lesson' => [
        'classname' =>
            'local_rono_publisher\external\publish_lesson',

        'methodname' =>
            'execute',

        'description' =>
            'Publishes one complete curriculum lesson into a Moodle course.',

        'type' =>
            'write',

        'capabilities' =>
            'local/rono_publisher:publishlesson',

        'ajax' =>
            false,
    ],

    'local_rono_publisher_update_elaboration_banner' => [
        'classname' =>
            'local_rono_publisher\\external\\update_elaboration_banner',

        'methodname' =>
            'execute',

        'description' =>
            'Updates one existing elaboration Text and Media banner by exact Moodle CMID.',

        'type' =>
            'write',

        'capabilities' =>
            'local/rono_publisher:publishlesson',

        'ajax' =>
            false,
    ],

    'local_rono_publisher_update_component' => [
        'classname' =>
            'local_rono_publisher\external\update_component',

        'methodname' =>
            'execute',

        'description' =>
            'Updates one existing published lesson component by exact Moodle CMID.',

        'type' =>
            'write',

        'capabilities' =>
            'local/rono_publisher:publishlesson',

        'ajax' =>
            false,
    ],

    'local_rono_publisher_ensure_course' => [
        'classname' =>
            'local_rono_publisher\external\ensure_course',

        'methodname' =>
            'execute',

        'description' =>
            'Creates or reuses the Moodle category hierarchy and curriculum course.',

        'type' =>
            'write',

        'capabilities' =>
            'moodle/course:create',

        'ajax' =>
            false,
    ],

    'local_rono_publisher_get_quiz_questions' => [
        'classname' =>
            'local_rono_publisher\external\get_quiz_questions',

        'methodname' =>
            'execute',

        'description' =>
            'Returns authoritative read-only Question Bank mappings for a Moodle Quiz.',

        'type' =>
            'read',

        'capabilities' =>
            'local/rono_publisher:viewanalytics',

        'ajax' =>
            false,
    ],
];
$services = [

    'Rono Publisher Service' => [
        'functions' => [
            'local_rono_publisher_ensure_course',
            'local_rono_publisher_publish_lesson',
            'local_rono_publisher_update_component',
            'local_rono_publisher_update_elaboration_banner',
        ],

        'restrictedusers' => 1,
        'enabled' => 1,
    ],

];
