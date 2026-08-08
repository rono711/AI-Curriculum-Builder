<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
//
// See the GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle. If not, see <https://www.gnu.org/licenses/>.

/**
 * External services definition.
 *
 * @package     local_rono_curriculumbuilder
 * @copyright   2026 Mohammad Hassan
 * @author      Mohammad Hassan
 * @license     https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */


// This file is part of Moodle - http://moodle.org/
//
// Rono Curriculum Builder
//
// Web Services
//
// Version 4.1
//

defined('MOODLE_INTERNAL') || die();

$functions = [

    // ==========================================================
    // Health
    // ==========================================================

    'local_rono_curriculumbuilder_health' => [

        'classname'   => 'local_rono_curriculumbuilder\external\health',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Plugin health check.',
        'type'        => 'read',
        'ajax'        => true,
        'capabilities'=> 'moodle/site:config'

    ],

    // ==========================================================
    // Ping
    // ==========================================================

    'local_rono_curriculumbuilder_ping' => [

        'classname'   => 'local_rono_curriculumbuilder\external\ping',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Simple connectivity test.',
        'type'        => 'read',
        'ajax'        => true

    ],

    // ==========================================================
    // Publish Course
    // ==========================================================

    'local_rono_curriculumbuilder_publish_course' => [

        'classname'   => 'local_rono_curriculumbuilder\external\publish_course',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Create or reuse a Moodle course.',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:create'

    ],

    // ==========================================================
    // Publish Section
    // ==========================================================

    'local_rono_curriculumbuilder_publish_section' => [

        'classname'   => 'local_rono_curriculumbuilder\external\publish_section',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Create or reuse a course section.',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:update'

    ],

    // ==========================================================
    // Publish Page
    // ==========================================================

    'local_rono_curriculumbuilder_publish_page' => [

        'classname'   => 'local_rono_curriculumbuilder\external\publish_page',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Create or update a Moodle Page.',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:update'

    ],

    // ==========================================================
    // Publish Quiz
    // ==========================================================

    'local_rono_curriculumbuilder_publish_quiz' => [

        'classname'   => 'local_rono_curriculumbuilder\external\publish_quiz',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Create or update a Moodle Quiz.',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:update'

    ],

    // ==========================================================
    // Publish Lesson
    // ==========================================================

    'local_rono_curriculumbuilder_publish_lesson' => [

        'classname'   => 'local_rono_curriculumbuilder\external\publish_lesson',
        'methodname'  => 'execute',
        'classpath'   => '',
        'description' => 'Publish an entire lesson package.',
        'type'        => 'write',
        'ajax'        => true,
        'capabilities'=> 'moodle/course:update'

    ]

];


// ==========================================================
// External Service
// ==========================================================

$services = [

    'Rono Curriculum Builder' => [

        'functions' => [

            'local_rono_curriculumbuilder_health',

            'local_rono_curriculumbuilder_ping',

            'local_rono_curriculumbuilder_publish_course',

            'local_rono_curriculumbuilder_publish_section',

            'local_rono_curriculumbuilder_publish_page',

            'local_rono_curriculumbuilder_publish_quiz',

            'local_rono_curriculumbuilder_publish_lesson'

        ],

        'enabled' => 1,

        'restrictedusers' => 0,

        'shortname' => 'rono_curriculum'

    ]

];