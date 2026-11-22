"use strict";

(function () {
    const button = document.getElementById("buildButton");

    if (!button) {
        return;
    }

    function value(id) {
        const element = document.getElementById(id);
        return element ? String(element.value || "").trim() : "";
    }

    function selectedLessons() {
        if (typeof syncSelectedLessons === "function") {
            syncSelectedLessons();
        }

        return Array.isArray(window.selectedCurriculumLessons)
            ? window.selectedCurriculumLessons
            : [];
    }

    function queueItem(lesson) {
        return {
            parent_code: lesson.parent_code,
            curriculum_code: lesson.curriculum_code,
            content_description: lesson.content_description,
            topic_id: lesson.topic_id,
            lesson_number: lesson.lesson_number,
            lesson_text: lesson.lesson,
            build_status: lesson.build_status,
            can_build: Boolean(lesson.can_build),
            can_update: Boolean(lesson.can_update),
            previous_build_id: lesson.previous_build_id,
            previous_lesson_package_id:
                lesson.previous_lesson_package_id
        };
    }

    function statusPanel() {
        let panel = document.getElementById("studioBuildStatus");

        if (!panel) {
            panel = document.createElement("div");
            panel.id = "studioBuildStatus";
            panel.className = "dashboard-card studio-build-status";
            panel.setAttribute("role", "status");
            panel.setAttribute("aria-live", "polite");
            button.closest(".build-actions").insertAdjacentElement(
                "afterend",
                panel
            );
        }

        return panel;
    }

    function showStatus(title, message, kind) {
        const panel = statusPanel();
        panel.className =
            "dashboard-card studio-build-status " + (kind || "working");
        panel.replaceChildren();

        const heading = document.createElement("h3");
        heading.textContent = title;

        const body = document.createElement("p");
        body.textContent = message;

        panel.append(heading, body);
    }

    async function responseJson(response) {
        const text = await response.text();

        if (!text) {
            return {};
        }

        try {
            return JSON.parse(text);
        } catch (error) {
            throw new Error(
                "Build App returned an invalid response (HTTP " +
                response.status + ")."
            );
        }
    }

    async function waitForImmediateJob(jobId) {
        while (true) {
            const response = await fetch(
                "/api/build-status/" + encodeURIComponent(jobId),
                {cache: "no-store"}
            );
            const job = await responseJson(response);

            if (!response.ok) {
                throw new Error(job.detail || "Unable to read build status.");
            }

            showStatus(
                "Building lesson package",
                (job.message || job.stage || job.status || "Processing") +
                    " · " + Number(job.percent || 0) + "%",
                "working"
            );

            if (job.status === "SUCCESS") {
                return job.result || {};
            }

            if (job.status === "FAILED") {
                throw new Error(job.error || "Lesson build failed.");
            }

            await new Promise(function (resolve) {
                setTimeout(resolve, 1500);
            });
        }
    }

    async function submitBuild(event) {
        event.preventDefault();

        const modeNode = document.querySelector(
            'input[name="processing_mode"]:checked'
        );
        const processingMode = modeNode ? modeNode.value : "IMMEDIATE";
        const queuedMode =
            processingMode === "QUEUE_STANDARD" ||
            processingMode === "QUEUE_BATCH";
        const lessons = (
            queuedMode &&
            Array.isArray(window.processingBasket) &&
            window.processingBasket.length
        )
            ? window.processingBasket.slice()
            : selectedLessons();

        if (!lessons.length) {
            alert("Please select at least one lesson / elaboration.");
            return;
        }

        const invalid = lessons.find(function (lesson) {
            return !lesson.can_build;
        });

        if (invalid) {
            alert(
                "The selected lesson " + invalid.curriculum_code +
                " is not available for a new build. " +
                "Use its Update / Rebuild action instead."
            );
            return;
        }

        const isQueued =
            processingMode === "QUEUE_STANDARD" ||
            processingMode === "QUEUE_BATCH";

        if (!isQueued && lessons.length > 1) {
            alert(
                "Immediate mode processes one lesson at a time. " +
                "Choose Queue Processing or Batch Processing for multiple lessons."
            );
            return;
        }

        const payload = {
            requested_by: value("requested_by"),
            curriculum_framework: value("curriculum_framework"),
            learning_area: value("learning_area"),
            subject: value("subject"),
            year_level: value("year_level"),
            strand: value("strand"),
            sub_strand: value("sub_strand"),
            parent_code: isQueued ? "" : value("topic"),
            topic_id: isQueued ? "" : lessons[0].topic_id,
            lesson_numbers: isQueued
                ? []
                : [Number(lessons[0].lesson_number)],
            items: isQueued ? lessons.map(queueItem) : [],
            processing_mode: processingMode,
            publication_mode: "IMMEDIATE"
        };

        const queuedPayloads = [];
        if (isQueued) {
            const groups = new Map();

            lessons.forEach(function (lesson) {
                const metadata = {
                    learning_area: lesson.learning_area || value("learning_area"),
                    subject: lesson.subject || value("subject"),
                    year_level: lesson.year_level || value("year_level"),
                    strand: lesson.strand || value("strand"),
                    sub_strand: lesson.sub_strand || ""
                };
                const key = JSON.stringify(metadata);
                if (!groups.has(key)) groups.set(key, {metadata: metadata, lessons: []});
                groups.get(key).lessons.push(lesson);
            });

            groups.forEach(function (group) {
                queuedPayloads.push({
                    requested_by: value("requested_by"),
                    curriculum_framework: value("curriculum_framework"),
                    learning_area: group.metadata.learning_area,
                    subject: group.metadata.subject,
                    year_level: group.metadata.year_level,
                    strand: group.metadata.strand,
                    sub_strand: group.metadata.sub_strand,
                    parent_code: "",
                    topic_id: "",
                    lesson_numbers: [],
                    items: group.lessons.map(queueItem),
                    processing_mode: processingMode,
                    publication_mode: "IMMEDIATE"
                });
            });
        }

        button.disabled = true;
        showStatus(
            isQueued ? "Saving build request" : "Starting lesson build",
            isQueued
                ? "Submitting " + lessons.length + " selected lesson(s)…"
                : "Preparing the selected lesson…",
            "working"
        );

        try {
            if (isQueued) {
                const acceptedRequests = [];

                for (const queuedPayload of queuedPayloads) {
                    const response = await fetch("/api/build", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify(queuedPayload)
                    });
                    const accepted = await responseJson(response);

                    if (!response.ok) {
                        throw new Error(
                            accepted.detail || accepted.error ||
                            "Build request failed with HTTP " + response.status
                        );
                    }
                    acceptedRequests.push(accepted);
                }

                const modeLabel = processingMode === "QUEUE_BATCH"
                    ? "Batch Processing"
                    : "Queue Processing";

                showStatus(
                    "Build request queued successfully",
                    acceptedRequests.length + " " + modeLabel +
                    " request(s) created for " + lessons.length +
                    " unique lesson(s). Automatic processing will begin within 60 seconds.",
                    "success"
                );

                window.processingScopes = [];
                window.processingBasket = [];
                if (typeof renderProcessingBasket === "function") {
                    renderProcessingBasket();
                }
                return;
            }

            const response = await fetch("/api/build", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            });
            const accepted = await responseJson(response);

            if (!response.ok) {
                throw new Error(
                    accepted.detail || accepted.error ||
                    "Build request failed with HTTP " + response.status
                );
            }

            if (!accepted.job_id) {
                throw new Error("Build App did not return a job ID.");
            }

            const result = await waitForImmediateJob(accepted.job_id);
            showStatus(
                "Lesson published successfully",
                "Package: " + (result.lesson_package_id || "completed"),
                "success"
            );
        } catch (error) {
            console.error("Studio build submission failed", error);
            showStatus("Build failed", error.message, "error");
        } finally {
            button.disabled = false;
        }
    }

    button.type = "button";
    button.addEventListener("click", submitBuild);
})();
