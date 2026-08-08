<?php
/**
 * Capabilities for the Rono Publisher plugin.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$capabilities = [

    'local/rono_publisher:publishlesson' => [
        'riskbitmask' => RISK_XSS,

        'captype' => 'write',

        'contextlevel' => CONTEXT_COURSE,

        'archetypes' => [
            'editingteacher' => CAP_ALLOW,
            'manager' => CAP_ALLOW,
        ],
    ],

];