<?php

defined('MOODLE_INTERNAL') || die();

$THEME->name = 'rono';

$THEME->parents = ['trema'];

$THEME->sheets = [];

$THEME->editor_sheets = [];

$THEME->scss = function($theme) {
    return theme_config::load('trema')->get_main_scss_content($theme);
};

$THEME->layouts = theme_config::load('trema')->layouts;

$THEME->enable_dock = false;

$THEME->rendererfactory = 'theme_overridden_renderer_factory';
