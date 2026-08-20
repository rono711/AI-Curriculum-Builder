<?php
/**
 * Administration settings for Rono Publisher.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {

    $settings = new admin_settingpage(
        'local_rono_publisher_settings',
        get_string('pluginname', 'local_rono_publisher')
    );

    $settings->add(
        new admin_setting_configtext(
            'local_rono_publisher/rootcoursecategory',
            'Root Course Category ID',
            'Moodle category under which curriculum categories and courses are automatically created.',
            '25',
            PARAM_INT
        )
    );

    $ADMIN->add(
        'localplugins',
        $settings
    );
}
