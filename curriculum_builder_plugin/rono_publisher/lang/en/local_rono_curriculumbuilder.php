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
// English Language Strings
//
// Version 4.0
//

defined('MOODLE_INTERNAL') || die();

//
// Plugin
//

$string['pluginname'] = 'Rono Curriculum Builder';
$string['pluginadministration'] = 'Rono Curriculum Builder';

$string['privacy:metadata'] =
'The Rono Curriculum Builder plugin publishes AI-generated lessons into Moodle and stores Moodle publishing mappings.';

//
// General Settings
//

$string['settings'] = 'Settings';

$string['generalsettings'] = 'General Settings';

$string['enableplugin'] = 'Enable Plugin';

$string['enableplugin_desc'] =
'Enable or disable the Rono Curriculum Builder plugin.';

//
// Publisher
//

$string['publisherengine'] = 'Publisher Engine';

$string['publisherengineurl'] = 'Publisher Engine URL';

$string['publishertimeout'] = 'Publisher Timeout';

//
// Publishing
//

$string['publishsettings'] = 'Publishing Settings';

$string['defaultcoursecategory'] = 'Default Course Category';

$string['defaultcoursecategory_desc'] =
    "Root Moodle course category used when creating Rono's School categories.";

$string['autocreatesections'] = 'Automatically Create Sections';

$string['overwritepages'] = 'Overwrite Existing Pages';

//
// External Service
//

$string['apisettings'] = 'External Web Service';

$string['servicename'] = 'Rono Curriculum Builder';

$string['serviceshortname'] = 'rono_curriculum';

//
// Logging
//

$string['loggingsettings'] = 'Logging Settings';

$string['enablelogging'] = 'Enable Logging';

$string['enablelogging_desc'] =
'Enable detailed publishing logs.';

$string['debugmode'] = 'Debug Mode';

$string['debugmode_desc'] =
'Enable debug logging.';

//
// Capabilities
//

$string['rono_curriculumbuilder:publish'] =
'Publish lessons to Moodle';

$string['rono_curriculumbuilder:manage'] =
'Manage Rono Curriculum Builder';

//
// External API
//

$string['publishlesson'] = 'Publish Lesson';

$string['publishcourse'] = 'Publish Course';

$string['publishsection'] = 'Publish Section';

$string['publishpage'] = 'Publish Page';

$string['publishquiz'] = 'Publish Quiz';

$string['ping'] = 'Ping';

$string['health'] = 'Health Check';

//
// Messages
//

$string['publishsuccess'] =
'Lesson published successfully.';

$string['publishfailed'] =
'Lesson publishing failed.';

$string['permissiondenied'] =
'Permission denied.';

$string['serviceunavailable'] =
'Service unavailable.';

$string['invalidpayload'] =
'Invalid publish payload.';

$string['invalidcourse'] =
'Invalid Moodle course.';

$string['invalidsection'] =
'Invalid Moodle section.';

$string['invalidlesson'] =
'Invalid lesson package.';

$string['lessonnotfound'] =
'Lesson package not found.';

//
// Status
//

$string['statusdraft'] = 'Draft';

$string['statusqueued'] = 'Queued';

$string['statusready'] = 'Ready';

$string['statuspublishing'] = 'Publishing';

$string['statuspublished'] = 'Published';

$string['statusfailed'] = 'Failed';

//
// Assets
//

$string['assetlesson'] = 'Lesson';

$string['assetgoogleslides'] = 'Google Slides';

$string['assetpptx'] = 'PowerPoint';

$string['assetquiz'] = 'Quiz';

$string['assetworksheet'] = 'Worksheet';

$string['assetteacherguide'] = 'Teacher Guide';

$string['assethomework'] = 'Homework';

$string['assetnotebooklm'] = 'NotebookLM';

$string['assetpdf'] = 'PDF';

$string['assetthumbnail'] = 'Thumbnail';

//
// Integrations
//

$string['integrationpublisher'] = 'Publisher Engine';

$string['integrationmoodle'] = 'Moodle';

$string['integrationgamma'] = 'Gamma';

$string['integrationgoogledrive'] = 'Google Drive';

$string['integrationgoogleslides'] = 'Google Slides';

$string['integrationnotebooklm'] = 'NotebookLM';

$string['integrationn8n'] = 'n8n';

//
// Logging Messages
//

$string['logpublishstarted'] =
'Lesson publishing started.';

$string['logcoursecreated'] =
'Course created.';

$string['logsectioncreated'] =
'Section created.';

$string['logpagepublished'] =
'Page published.';

$string['logquizpublished'] =
'Quiz published.';

$string['logpublishcompleted'] =
'Lesson publishing completed.';

$string['logpublishfailed'] =
'Lesson publishing failed.';

$string['logsyncstarted'] =
'Synchronisation started.';

$string['logsynccompleted'] =
'Synchronisation completed.';

$string['logsyncfailed'] =
'Synchronisation failed.';