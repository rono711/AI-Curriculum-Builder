"use strict";

let queueRequests = [];
let currentFilter = "active";


function escapeHtml(value) {
    const div = document.createElement("div");
    div.textContent = value === null || value === undefined
        ? ""
        : String(value);

    return div.innerHTML;
}


function localTime(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString();
}


function isPublished(request) {
    return String(
        request.status || ""
    ).toUpperCase() === "PUBLISHED";
}


function isFailed(request) {
    const status = String(
        request.status || ""
    ).toUpperCase();

    return (
        status === "FAILED"
        || status.endsWith("_FAILED")
    );
}


function isActive(request) {
    return (
        !isPublished(request)
        && !isFailed(request)
    );
}


function matchesFilter(request) {
    if (currentFilter === "completed") {
        return isPublished(request);
    }

    if (currentFilter === "failed") {
        return isFailed(request);
    }

    if (currentFilter === "active") {
        return isActive(request);
    }

    return true;
}


function badgeClass(request) {
    if (isPublished(request)) {
        return "published";
    }

    if (isFailed(request)) {
        return "failed";
    }

    if (
        request.processing_mode === "QUEUE_BATCH"
    ) {
        return "batch";
    }

    return "";
}


function updateSummary() {
    const active = queueRequests.filter(
        isActive
    ).length;

    const published = queueRequests.filter(
        isPublished
    ).length;

    const failed = queueRequests.filter(
        isFailed
    ).length;

    document.getElementById(
        "activeCount"
    ).textContent = active;

    document.getElementById(
        "publishedCount"
    ).textContent = published;

    document.getElementById(
        "failedCount"
    ).textContent = failed;

    document.getElementById(
        "totalCount"
    ).textContent = queueRequests.length;
}


function requestCard(request) {
    const percent = Math.max(
        0,
        Math.min(
            100,
            Number(request.percent || 0)
        )
    );

    const liveIndicator = request.live

        ? (

            '<span class="queue-live-indicator" role="status">'

            + '<span class="queue-live-dot"></span>'

            + 'Live processing'

            + '</span>'

        )

        : "";


    const error = request.error
        ? (
            '<div class="error-box">'
            + escapeHtml(request.error)
            + "</div>"
        )
        : "";

    return `
        <article class="request-card">
            <div class="request-header">
                <div>
                    <h2 class="request-title">
                        ${escapeHtml(request.subject)}
                        ·
                        ${escapeHtml(request.year_level)}
                        ·
                        ${escapeHtml(request.strand)}
                    </h2>

                    <div class="request-id">
                        ${escapeHtml(request.request_id)}
                    </div>

                    <div class="badges">
                        ${liveIndicator}
<span class="badge ${
                            request.processing_mode ===
                            "QUEUE_BATCH"
                                ? "batch"
                                : ""
                        }">
                            ${escapeHtml(
                                request.processing_mode_label
                            )}
                        </span>

                        <span class="badge ${badgeClass(request)}">
                            ${escapeHtml(
                                request.status_label
                            )}
                        </span>
                    </div>
                </div>
            </div>

            <div class="progress-row">
                <div class="progress-track">
                    <div
                        class="progress-fill"
                        style="width:${percent}%"
                    ></div>
                </div>

                <div class="progress-value">
                    ${percent}%
                </div>
            </div>

            <div class="request-grid">
                <div class="metric">
                    <span class="metric-label">
                        Lessons
                    </span>
                    <span class="metric-value">
                        ${request.lesson_count}
                    </span>
                </div>

                <div class="metric">
                    <span class="metric-label">
                        Published
                    </span>
                    <span class="metric-value">
                        ${request.published_count}
                    </span>
                </div>

                <div class="metric">
                    <span class="metric-label">
                        Failed
                    </span>
                    <span class="metric-value">
                        ${request.failed_count}
                    </span>
                </div>

                <div class="metric">
                    <span class="metric-label">
                        Current stage
                    </span>
                    <span class="metric-value">
                        ${escapeHtml(
                            request.status_label
                        )}
                    </span>
                </div>
            </div>

            ${error}

            <div class="request-footer">
                <div class="timestamp">
                    Submitted:
                    ${escapeHtml(
                        localTime(request.created_at)
                    )}
                    <br>
                    Updated:
                    ${escapeHtml(
                        localTime(request.updated_at)
                    )}
                </div>

                <button
                    class="button detail-button"
                    type="button"
                    data-request-id="${
                        escapeHtml(request.request_id)
                    }"
                >
                    View Details
                </button>
            </div>
        </article>
    `;
}



function renderRequests() {
    const container = document.getElementById(
        "requestList"
    );

    const visible = queueRequests.filter(
        matchesFilter
    );

    if (!visible.length) {
        container.innerHTML = `
            <div class="empty">
                No requests in this view.
            </div>
        `;
        return;
    }

    container.innerHTML = visible
        .map(requestCard)
        .join("");

    document.querySelectorAll(
        ".detail-button"
    ).forEach(function(button) {
        button.addEventListener(
            "click",
            function() {
                openDetails(
                    button.dataset.requestId
                );
            }
        );
    });
}


async function refreshQueue() {
    const response = await fetch(
        "/api/queue/requests",
        {
            cache: "no-store"
        }
    );

    if (!response.ok) {
        throw new Error(
            "Queue API returned HTTP "
            + response.status
        );
    }

    const data = await response.json();

    queueRequests = Array.isArray(
        data.requests
    )
        ? data.requests
        : [];

    updateSummary();
    renderRequests();

    document.getElementById(
        "lastRefresh"
    ).textContent =
        "Last refreshed: "
        + new Date().toLocaleTimeString();
}


function metricBlock(label, value) {
    const box = document.createElement("div");
    box.className = "metric";

    const labelNode = document.createElement("span");
    labelNode.className = "metric-label";
    labelNode.textContent = label;

    const valueNode = document.createElement("span");
    valueNode.className = "metric-value";
    valueNode.textContent =
        value === null || value === undefined || value === ""
            ? "-"
            : String(value);

    box.appendChild(labelNode);
    box.appendChild(valueNode);

    return box;
}


function lessonCard(item, parent) {
    const card = document.createElement("article");
    card.className = "lesson-card";

    const title = document.createElement("h3");
    title.className = "lesson-title";
    title.textContent =
        item.curriculum_code || "Lesson";

    const text = document.createElement("div");
    text.className = "lesson-text";
    text.textContent =
        item.lesson_text || item.content_description || "";

    let stageLabel = item.status_label || item.stage || item.status;

    if (
        parent.processing_mode === "QUEUE_BATCH"
        && String(item.stage || "").toUpperCase() === "QUEUED"
        && String(parent.status || "").toUpperCase() !== "QUEUED"
    ) {
        stageLabel =
            parent.status_label
            + " (request-level stage)";
    }

    const meta = document.createElement("div");
    meta.className = "lesson-meta";

    meta.appendChild(
        metricBlock("Stage", stageLabel)
    );

    meta.appendChild(
        metricBlock(
            "Progress",
            String(item.percent || 0) + "%"
        )
    );

    meta.appendChild(
        metricBlock(
            "Lesson package",
            item.lesson_package_id
        )
    );

    meta.appendChild(
        metricBlock(
            "Build ID",
            item.build_id
        )
    );

    meta.appendChild(
        metricBlock(
            "Updated",
            localTime(item.updated_at)
        )
    );

    meta.appendChild(
        metricBlock(
            "Status",
            item.status
        )
    );

    card.appendChild(title);
    card.appendChild(text);
    card.appendChild(meta);

    if (item.error) {
        const error = document.createElement("div");
        error.className = "error-box";
        error.textContent = item.error;
        card.appendChild(error);
    }

    return card;
}


async function openDetails(requestId) {
    const modal = document.getElementById(
        "detailModal"
    );

    const content = document.getElementById(
        "detailContent"
    );

    content.textContent = "Loading lesson details...";

    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");

    try {
        const response = await fetch(
            "/api/queue/requests/"
            + encodeURIComponent(requestId),
            {
                cache: "no-store"
            }
        );

        if (!response.ok) {
            throw new Error(
                "Request detail API returned HTTP "
                + response.status
            );
        }

        const data = await response.json();
        const parent = data.request;

        document.getElementById(
            "detailTitle"
        ).textContent =
            parent.subject
            + " · "
            + parent.year_level;

        document.getElementById(
            "detailSubtitle"
        ).textContent =
            parent.request_id
            + " · "
            + parent.processing_mode_label
            + " · "
            + parent.status_label;

        content.replaceChildren();

        if (!data.items || !data.items.length) {
            content.textContent =
                "No lesson records found.";
            return;
        }

        data.items.forEach(function(item) {
            content.appendChild(
                lessonCard(item, parent)
            );
        });

    } catch (error) {
        content.textContent =
            "Unable to load request details: "
            + error.message;
    }
}


function closeDetails() {
    const modal = document.getElementById(
        "detailModal"
    );

    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
}


document.querySelectorAll(
    ".filter"
).forEach(function(button) {
    button.addEventListener(
        "click",
        function() {
            currentFilter =
                button.dataset.filter;

            document.querySelectorAll(
                ".filter"
            ).forEach(function(other) {
                other.classList.remove(
                    "active"
                );
            });

            button.classList.add("active");

            renderRequests();
        }
    );
});


document.getElementById(
    "refreshButton"
).addEventListener(
    "click",
    function() {
        refreshQueue().catch(
            console.error
        );
    }
);


document.getElementById(
    "closeModal"
).addEventListener(
    "click",
    closeDetails
);


document.getElementById(
    "modalBackdrop"
).addEventListener(
    "click",
    closeDetails
);


document.addEventListener(
    "keydown",
    function(event) {
        if (event.key === "Escape") {
            closeDetails();
        }
    }
);


refreshQueue().catch(function(error) {
    document.getElementById(
        "requestList"
    ).textContent =
        "Unable to load queue: "
        + error.message;
});


setInterval(function() {
    refreshQueue().catch(
        console.error
    );
}, 15000);


// ==========================================================
// All-curriculum Lesson Build History
// ==========================================================

let buildHistory = [];
let historyPageNumber = 1;
const historyPageSize = 25;

function historyInput(id) {
    return document.getElementById(id).value.trim();
}

function filteredHistory() {
    const search = historyInput("historySearch").toLowerCase();
    const status = historyInput("historyStatus");
    const curriculum = historyInput("historyCurriculum");
    const from = historyInput("historyFrom");
    const to = historyInput("historyTo");

    return buildHistory.filter(function(item) {
        const text = [
            item.curriculum_code,
            item.parent_code,
            item.lesson_title,
            item.content_description,
            item.moodle_title,
            item.subject,
            item.year_level
        ].join(" ").toLowerCase();
        const date = String(item.request_date || "").slice(0, 10);

        return (!search || text.includes(search))
            && (!status || item.display_status === status)
            && (!curriculum || item.curriculum === curriculum)
            && (!from || date >= from)
            && (!to || date <= to);
    });
}

function statusClass(value) {
    return String(value || "").toLowerCase().replace(/[^a-z0-9]+/g, "-");
}

function moodleTitleCell(item) {
    if (item.moodle_title) {
        return escapeHtml(item.moodle_title);
    }
    if (item.moodle_quiz_id) {
        return '<span class="history-muted">Title not historically recorded<br>Quiz ID '
            + escapeHtml(item.moodle_quiz_id) + "</span>";
    }
    return '<span class="history-muted">Not published</span>';
}

function renderHistorySummary() {
    function count(label) {
        return buildHistory.filter(function(item) {
            return item.display_status === label;
        }).length;
    }
    document.getElementById("historyTotal").textContent = buildHistory.length;
    document.getElementById("historyPublished").textContent = count("Published");
    document.getElementById("historyGenerated").textContent =
        count("Generated") + count("Update ready");
    document.getElementById("historyUpdated").textContent = count("Updated");
    document.getElementById("historyRebuilt").textContent = count("Rebuilt");
}

function populateHistorySelect(id, values, allLabel) {
    const select = document.getElementById(id);
    const current = select.value;
    const unique = Array.from(new Set(values.filter(Boolean))).sort();
    select.innerHTML = '<option value="">' + escapeHtml(allLabel) + "</option>"
        + unique.map(function(value) {
            return '<option value="' + escapeHtml(value) + '">'
                + escapeHtml(value) + "</option>";
        }).join("");
    if (unique.includes(current)) {
        select.value = current;
    }
}

function renderHistory() {
    const records = filteredHistory();
    const pages = Math.max(1, Math.ceil(records.length / historyPageSize));
    historyPageNumber = Math.min(historyPageNumber, pages);
    const start = (historyPageNumber - 1) * historyPageSize;
    const visible = records.slice(start, start + historyPageSize);
    const body = document.getElementById("historyBody");

    if (!visible.length) {
        body.innerHTML = '<tr><td colspan="7" class="history-empty">'
            + "No lesson records match these filters.</td></tr>";
    } else {
        body.innerHTML = visible.map(function(item) {
            return "<tr>"
                + '<td class="history-date">' + escapeHtml(localTime(item.request_date)) + "</td>"
                + '<td><span class="history-status ' + statusClass(item.display_status) + '">'
                + escapeHtml(item.display_status) + "</span></td>"
                + "<td><strong>" + escapeHtml(item.curriculum) + "</strong>"
                + "<small>" + escapeHtml(item.subject || "") + "</small></td>"
                + "<td><code>" + escapeHtml(item.curriculum_code || item.parent_code) + "</code></td>"
                + '<td class="history-lesson"><strong>' + escapeHtml(item.lesson_title || "")
                + "</strong><small>" + escapeHtml(item.content_description || "") + "</small></td>"
                + "<td>" + moodleTitleCell(item) + "</td>"
                + '<td class="history-date">' + escapeHtml(localTime(item.modified_date)) + "</td>"
                + "</tr>";
        }).join("");
    }

    document.getElementById("historyShowing").textContent =
        records.length + " record" + (records.length === 1 ? "" : "s");
    document.getElementById("historyPage").textContent =
        "Page " + historyPageNumber + " of " + pages;
    document.getElementById("historyPrevious").disabled = historyPageNumber <= 1;
    document.getElementById("historyNext").disabled = historyPageNumber >= pages;
}

async function refreshHistory() {
    const response = await fetch("/api/queue/history", {cache: "no-store"});
    if (!response.ok) {
        throw new Error("History API returned HTTP " + response.status);
    }
    const data = await response.json();
    buildHistory = Array.isArray(data.history) ? data.history : [];
    renderHistorySummary();
    populateHistorySelect(
        "historyStatus",
        buildHistory.map(function(item) { return item.display_status; }),
        "All statuses"
    );
    populateHistorySelect(
        "historyCurriculum",
        buildHistory.map(function(item) { return item.curriculum; }),
        "All curricula"
    );
    renderHistory();
}

function csvCell(value) {
    return '"' + String(value === null || value === undefined ? "" : value)
        .replace(/"/g, '""') + '"';
}

function exportHistory() {
    const lines = [[
        "Request date", "Status", "Curriculum", "Curriculum code",
        "Elaboration / lesson title", "Moodle title", "Modified date",
        "Moodle course ID", "Moodle quiz ID", "Moodle CMID"
    ].map(csvCell).join(",")];

    filteredHistory().forEach(function(item) {
        lines.push([
            item.request_date, item.display_status, item.curriculum,
            item.curriculum_code, item.lesson_title, item.moodle_title,
            item.modified_date, item.moodle_course_id,
            item.moodle_quiz_id, item.moodle_quiz_cmid
        ].map(csvCell).join(","));
    });

    const blob = new Blob([lines.join("\n")], {type: "text/csv;charset=utf-8"});
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "all-curriculum-lesson-build-history.csv";
    link.click();
    URL.revokeObjectURL(link.href);
}

["historySearch", "historyStatus", "historyCurriculum", "historyFrom", "historyTo"]
    .forEach(function(id) {
        document.getElementById(id).addEventListener("input", function() {
            historyPageNumber = 1;
            renderHistory();
        });
    });

document.getElementById("clearHistoryFilters").addEventListener("click", function() {
    ["historySearch", "historyStatus", "historyCurriculum", "historyFrom", "historyTo"]
        .forEach(function(id) { document.getElementById(id).value = ""; });
    historyPageNumber = 1;
    renderHistory();
});
document.getElementById("historyPrevious").addEventListener("click", function() {
    if (historyPageNumber > 1) { historyPageNumber -= 1; renderHistory(); }
});
document.getElementById("historyNext").addEventListener("click", function() {
    historyPageNumber += 1;
    renderHistory();
});
document.getElementById("exportHistory").addEventListener("click", exportHistory);
document.getElementById("refreshButton").addEventListener("click", function() {
    refreshHistory().catch(console.error);
});

refreshHistory().catch(function(error) {
    document.getElementById("historyBody").innerHTML =
        '<tr><td colspan="7" class="history-empty">Unable to load history: '
        + escapeHtml(error.message) + "</td></tr>";
});
