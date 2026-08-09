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
        'classname'   => 'local_rono_publisher\external\publish_lesson',
        'methodname'  => 'execute',
        'description' => 'Publishes one complete curriculum lesson into a Moodle course.',
        'type'        => 'write',
        'capabilities' => 'local/rono_publisher:publishlesson',
        'ajax'        => false,
    ],

];

$services = [

    'Rono Publisher Service' => [
        'functions' => [
            'local_rono_publisher_publish_lesson',
        ],
        'restrictedusers' => 1,
        'enabled' => 1,
    ],

];