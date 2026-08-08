<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Rono Curriculum Builder
//
// Capability Definitions
//
// Version 4.0
//

defined('MOODLE_INTERNAL') || die();

$capabilities = [

    /*
     * -------------------------------------------------------------------------
     * Publish Lessons
     * -------------------------------------------------------------------------
     */

    'local/rono_curriculumbuilder:publish' => [

        'riskbitmask' => RISK_CONFIG,

        'captype' => 'write',

        'contextlevel' => CONTEXT_SYSTEM,

        'archetypes' => [

            'manager' => CAP_ALLOW,

        ],

    ],

    /*
     * -------------------------------------------------------------------------
     * Manage Plugin
     * -------------------------------------------------------------------------
     */

    'local/rono_curriculumbuilder:manage' => [

        'riskbitmask' => RISK_CONFIG,

        'captype' => 'write',

        'contextlevel' => CONTEXT_SYSTEM,

        'archetypes' => [

            'manager' => CAP_ALLOW,

        ],

    ],

];