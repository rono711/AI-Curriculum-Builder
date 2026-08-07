<?php
// This file is part of Moodle - http://moodle.org/
//
// Rono Curriculum Builder
//
// Library Functions
//
// Version 4.0
//

defined('MOODLE_INTERNAL') || die();

/**
 * ============================================================================
 * Extend Site Navigation
 * ============================================================================
 */

function local_rono_curriculumbuilder_extend_navigation(

    global_navigation $navigation

): void {

    if (

        !has_capability(

            'local/rono_curriculumbuilder:manage',

            context_system::instance()

        )

    ) {

        return;

    }

    $navigation->add(

        get_string(

            'pluginname',

            'local_rono_curriculumbuilder'

        ),

        new moodle_url(

            '/local/rono_curriculumbuilder/index.php'

        ),

        navigation_node::TYPE_CUSTOM,

        null,

        'local_rono_curriculumbuilder'

    );

}

/**
 * ============================================================================
 * Extend Settings Navigation
 * ============================================================================
 */

function local_rono_curriculumbuilder_extend_settings_navigation(

    settings_navigation $settingsnav,

    context $context

): void {

    if (

        !has_capability(

            'local/rono_curriculumbuilder:manage',

            $context

        )

    ) {

        return;

    }

    $node = navigation_node::create(

        get_string(

            'pluginname',

            'local_rono_curriculumbuilder'

        ),

        new moodle_url(

            '/local/rono_curriculumbuilder/index.php'

        ),

        navigation_node::TYPE_SETTING

    );

    $settingsnav->add_node(

        $node

    );

}

/**
 * ============================================================================
 * Plugin Enabled
 * ============================================================================
 */

function local_rono_curriculumbuilder_is_enabled(): bool {

    return (bool)get_config(

        'local_rono_curriculumbuilder',

        'enableplugin'

    );

}

/**
 * ============================================================================
 * Plugin Version
 * ============================================================================
 */

function local_rono_curriculumbuilder_plugin_version(): string {

    global $CFG;

    require(

        $CFG->dirroot

        . '/local/rono_curriculumbuilder/version.php'

    );

    return $plugin->release;

}

/**
 * ============================================================================
 * Publisher URL
 * ============================================================================
 */

function local_rono_curriculumbuilder_publisher_url(): string {

    return (string)get_config(

        'local_rono_curriculumbuilder',

        'publisherurl'

    );

}

/**
 * ============================================================================
 * Publisher Timeout
 * ============================================================================
 */

function local_rono_curriculumbuilder_publisher_timeout(): int {

    return (int)get_config(

        'local_rono_curriculumbuilder',

        'publishertimeout'

    );

}

/**
 * ============================================================================
 * Logging Enabled
 * ============================================================================
 */

function local_rono_curriculumbuilder_logging_enabled(): bool {

    return (bool)get_config(

        'local_rono_curriculumbuilder',

        'enablelogging'

    );

}

/**
 * ============================================================================
 * Debug Enabled
 * ============================================================================
 */

function local_rono_curriculumbuilder_debug_enabled(): bool {

    return (bool)get_config(

        'local_rono_curriculumbuilder',

        'debugmode'

    );

}

/**
 * ============================================================================
 * External Service Name
 * ============================================================================
 */

function local_rono_curriculumbuilder_service_name(): string {

    return get_config(

        'local_rono_curriculumbuilder',

        'servicename'

    ) ?: 'Rono Curriculum Builder';

}

/**
 * ============================================================================
 * External Service Short Name
 * ============================================================================
 */

function local_rono_curriculumbuilder_service_shortname(): string {

    return get_config(

        'local_rono_curriculumbuilder',

        'serviceshortname'

    ) ?: 'rono_curriculum';

}