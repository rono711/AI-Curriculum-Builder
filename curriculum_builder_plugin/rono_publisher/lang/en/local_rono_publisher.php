<?php
/**
 * Language strings for Rono Publisher.
 *
 * @package     local_rono_publisher
 * @copyright   2026 Rono's School
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

/**
 * Plugin name.
 */
$string['pluginname'] = 'Rono Publisher';

/**
 * Capabilities.
 */
$string['rono_publisher:publishlesson'] = 'Publish curriculum lessons';

/**
 * General publishing strings.
 */
$string['publishlesson'] = 'Publish lesson';
$string['publishinglesson'] = 'Publishing lesson';
$string['publishsuccess'] = 'Lesson published successfully';
$string['publishfailed'] = 'Lesson publishing failed';

/**
 * Curriculum structure.
 */
$string['strand'] = 'Strand';
$string['substrand'] = 'Sub-strand';
$string['contentdescription'] = 'Content description';
$string['lesson'] = 'Lesson';

/**
 * Lesson activity titles.
 */
$string['missionoftheday'] = 'Mission of the Day';
$string['didyouknow'] = 'Did You Know?';
$string['checkingyourthinking'] = 'Checking Your Thinking';
$string['letsdoit'] = "Let's Do It";
$string['whatwediscovered'] = 'What We Discovered';

/**
 * Question Bank and Quiz.
 */
$string['questionbankcategory'] = 'Question Bank category';
$string['questionimport'] = 'Question import';
$string['quizcreation'] = 'Quiz creation';

/**
 * Error messages.
 */
$string['errorinvalidcourse'] = 'The target Moodle course is invalid.';
$string['erroremptystrand'] = 'The curriculum strand cannot be empty.';
$string['erroremptysubstrand'] = 'The curriculum sub-strand cannot be empty.';
$string['erroremptycontentdescription'] = 'The content description cannot be empty.';
$string['erroremptylesson'] = 'The lesson title cannot be empty.';
$string['errorsubsection'] = 'Unable to create the Moodle subsection.';
$string['errorquestionimport'] = 'Unable to import questions into the Moodle Question Bank.';
$string['errorquizcreation'] = 'Unable to create the Moodle quiz.';