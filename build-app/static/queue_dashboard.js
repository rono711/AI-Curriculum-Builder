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
