<?php

namespace local_rono_analytics;

defined('MOODLE_INTERNAL') || die();

class analytics_client {

    /** @var string */
    private $apiurl;

    /** @var string */
    private $secret;

    public function __construct(
        ?string $apiurl = null,
        ?string $secret = null
    ) {
        $this->apiurl = rtrim(
            $apiurl
                ?? (string)get_config(
                    'local_rono_analytics',
                    'apiurl'
                ),
            '/'
        );

        $this->secret = $secret
            ?? (string)get_config(
                'local_rono_analytics',
                'apisecret'
            );

        if ($this->apiurl === '') {
            throw new \moodle_exception(
                'Analytics API URL is not configured.'
            );
        }

        if ($this->secret === '') {
            throw new \moodle_exception(
                'Analytics API secret is not configured.'
            );
        }
    }

    public function signature(
        string $method,
        string $path,
        string $query,
        int $userid,
        int $timestamp,
        bool $issiteadmin = false
    ): string {
        $message = implode("\n", [
            strtoupper($method),
            $path,
            $query,
            (string)$userid,
            (string)$timestamp,
            $issiteadmin ? '1' : '0',
        ]);

        return hash_hmac(
            'sha256',
            $message,
            $this->secret
        );
    }

    public function get(
        string $path,
        array $params,
        int $userid
    ): array {
        global $CFG;

        require_once(
            $CFG->libdir . '/filelib.php'
        );

        $query = http_build_query(
            $params,
            '',
            '&',
            PHP_QUERY_RFC3986
        );

        $timestamp = time();

        $issiteadmin = is_siteadmin(
            $userid
        );

        $signature = $this->signature(
            'GET',
            $path,
            $query,
            $userid,
            $timestamp,
            $issiteadmin
        );

        $url = (
            $this->apiurl
            . $path
            . (
                $query !== ''
                    ? '?' . $query
                    : ''
            )
        );

        $curl = new \curl();

        $curl->setHeader([
            'Accept: application/json',
            'X-Rono-User-Id: ' . $userid,
            'X-Rono-Timestamp: ' . $timestamp,
            'X-Rono-Is-Site-Admin: '
                . ($issiteadmin ? '1' : '0'),
            'X-Rono-Signature: ' . $signature,
        ]);

        $body = $curl->get($url);

        $info = $curl->get_info();

        $status = (int)(
            $info['http_code']
            ?? 0
        );

        if ($status !== 200) {
            throw new \moodle_exception(
                'Analytics API request failed '
                . 'with HTTP '
                . $status
                . '.'
            );
        }

        $data = json_decode(
            $body,
            true
        );

        if (!is_array($data)) {
            throw new \moodle_exception(
                'Analytics API returned invalid JSON.'
            );
        }

        return $data;
    }

    public function course_overview(
        int $courseid,
        int $userid,
        ?string $datefrom = null,
        ?string $dateto = null
    ): array {
        $params = [];

        if ($datefrom !== null) {
            $params['date_from'] = $datefrom;
        }

        if ($dateto !== null) {
            $params['date_to'] = $dateto;
        }

        return $this->get(
            '/dashboard/course/'
                . $courseid
                . '/overview',
            $params,
            $userid
        );
    }

    public function course_topics(
        int $courseid,
        int $userid,
        ?string $datefrom = null,
        ?string $dateto = null
    ): array {
        $params = [];

        if ($datefrom !== null) {
            $params['date_from'] = $datefrom;
        }

        if ($dateto !== null) {
            $params['date_to'] = $dateto;
        }

        return $this->get(
            '/dashboard/course/'
                . $courseid
                . '/topics',
            $params,
            $userid
        );
    }

    public function topic_history(
        int $courseid,
        int $userid,
        string $datefrom,
        string $dateto,
        int $bucketdays = 7
    ): array {
        return $this->get(
            '/dashboard/course/'
                . $courseid
                . '/topics/history',
            [
                'date_from' =>
                    $datefrom,

                'date_to' =>
                    $dateto,

                'bucket_days' =>
                    $bucketdays,
            ],
            $userid
        );
    }
}
