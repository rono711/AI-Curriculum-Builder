<?php
/**
 * Rono Publisher.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_rono_publisher';

/*
 * Plugin build number.
 *
 * 2026080900
 *
 * 2026-08-09
 * Question Bank test integration.
 */
$plugin->version = 2026080900;

/*
 * Minimum supported Moodle version.
 *
 * Keep the same Moodle requirement that was used for the
 * successfully installed structural-test version.
 */
$plugin->requires = 2025100600;

$plugin->maturity = MATURITY_ALPHA;

$plugin->release = '1.1.0-questionbank-test';