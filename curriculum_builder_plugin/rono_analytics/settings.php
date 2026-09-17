<?php

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {
    $settings = new admin_settingpage(
        'local_rono_analytics',
        get_string(
            'pluginname',
            'local_rono_analytics'
        )
    );

    $ADMIN->add(
        'localplugins',
        $settings
    );

    $settings->add(
        new admin_setting_configtext(
            'local_rono_analytics/apiurl',
            'Analytics API URL',
            'Internal URL of the Learning Analytics service.',
            '',
            PARAM_URL
        )
    );

    $settings->add(
        new admin_setting_configpasswordunmask(
            'local_rono_analytics/apisecret',
            'Analytics API secret',
            'Shared HMAC secret for server-to-server requests.',
            ''
        )
    );
}
