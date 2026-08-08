<?php
/**
 * Cache service for Rono Publisher.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

namespace local_rono_publisher\service;

defined('MOODLE_INTERNAL') || die();

/**
 * Service responsible for rebuilding Moodle course caches.
 */
class cache_service {

    /**
     * Rebuild the Moodle course cache.
     *
     * @param int $courseid Moodle course ID.
     * @return void
     */
    public function rebuild_course(int $courseid): void {

        rebuild_course_cache(
            $courseid,
            true
        );
    }
}