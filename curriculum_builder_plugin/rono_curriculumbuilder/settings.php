<?php
// This file is part of Moodle - http://moodle.org/
//
// Rono Curriculum Builder
//
// Plugin Settings
//
// Version 4.0
//

defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig) {

    $settings = new admin_settingpage(

        'local_rono_curriculumbuilder',

        get_string(

            'pluginname',

            'local_rono_curriculumbuilder'

        )

    );

    /*
     * ==========================================================
     * General
     * ==========================================================
     */

    $settings->add(

        new admin_setting_heading(

            'local_rono_curriculumbuilder/general',

            'General',

            'General plugin settings.'

        )

    );

    $settings->add(

        new admin_setting_configcheckbox(

            'local_rono_curriculumbuilder/enableplugin',

            'Enable Plugin',

            'Enable the Rono Curriculum Builder.',

            1

        )

    );

    /*
     * ==========================================================
     * Moodle Publishing
     * ==========================================================
     */

    $settings->add(

        new admin_setting_heading(

            'local_rono_curriculumbuilder/publishing',

            'Publishing',

            'Publishing defaults.'

        )

    );

    $settings->add(

        new admin_setting_configtext(

            'local_rono_curriculumbuilder/defaultcoursecategory',

            'Default Root Course Category',

            'Category used when Rono\'s School category does not yet exist.',

            1,

            PARAM_INT

        )

    );

    $settings->add(

        new admin_setting_configcheckbox(

            'local_rono_curriculumbuilder/autocreatesections',

            'Automatically Create Sections',

            'Automatically create Strand sections.',

            1

        )

    );

    $settings->add(

        new admin_setting_configcheckbox(

            'local_rono_curriculumbuilder/overwritepages',

            'Overwrite Existing Pages',

            'Update an existing page when republishing.',

            1

        )

    );

    /*
     * ==========================================================
     * Publisher Engine
     * ==========================================================
     */

    $settings->add(

        new admin_setting_heading(

            'local_rono_curriculumbuilder/publisher',

            'Publisher Engine',

            'Publisher Engine configuration.'

        )

    );

    $settings->add(

        new admin_setting_configtext(

            'local_rono_curriculumbuilder/publisherurl',

            'Publisher Engine URL',

            'Future use.',

            '',

            PARAM_URL

        )

    );

    $settings->add(

        new admin_setting_configtext(

            'local_rono_curriculumbuilder/publishertimeout',

            'Publisher Timeout (seconds)',

            'Future use.',

            300,

            PARAM_INT

        )

    );

    /*
     * ==========================================================
     * Logging
     * ==========================================================
     */

    $settings->add(

        new admin_setting_heading(

            'local_rono_curriculumbuilder/logging',

            'Logging',

            'Logging options.'

        )

    );

    $settings->add(

        new admin_setting_configcheckbox(

            'local_rono_curriculumbuilder/enablelogging',

            'Enable Logging',

            'Enable plugin logging.',

            1

        )

    );

    $settings->add(

        new admin_setting_configcheckbox(

            'local_rono_curriculumbuilder/debugmode',

            'Debug Mode',

            'Enable debug output.',

            0

        )

    );

    /*
     * ==========================================================
     * External Service
     * ==========================================================
     */

    $settings->add(

        new admin_setting_heading(

            'local_rono_curriculumbuilder/service',

            'External Web Service',

            'Web service configuration.'

        )

    );

    $settings->add(

        new admin_setting_configtext(

            'local_rono_curriculumbuilder/servicename',

            'Service Name',

            '',

            'Rono Curriculum Builder',

            PARAM_TEXT

        )

    );

    $settings->add(

        new admin_setting_configtext(

            'local_rono_curriculumbuilder/serviceshortname',

            'Service Short Name',

            '',

            'rono_curriculum',

            PARAM_ALPHANUMEXT

        )

    );

    $ADMIN->add(

        'localplugins',

        $settings

    );

}