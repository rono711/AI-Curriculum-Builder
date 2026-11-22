/* ==========================================================
   Curriculum Studio
   Module : selection.js
   Migrated from curriculum_studio_original.js
========================================================== */

    async function loadLearningAreas() {

    console.log("=== loadLearningAreas() ===");
    console.log("API_BASE =", API_BASE);
    console.log("URL =", API_BASE + "/learning-areas");


        try {

            const areas = removeNan(
                await fetchJSON(
                    API_BASE +

                    "/learning-areas"
                )
            );

            const select =

                document.getElementById(
                    "learning_area"
                );

            clearSelect(
                "learning_area",

                "Select Learning Area"
            );

            areas.forEach(area => {

                const option =

                    document.createElement("option");

                option.value = area;

                option.textContent = area;

                select.appendChild(option);

            });

        } catch (err) {

            console.error(err);

            alert(
                "Unable to load Learning Areas."
            );

        }

    }

    /* ==========================================================
       Subjects
    ========================================================== */

    async function loadSubjects() {

        clearSelect(
            "subject",

            "Loading..."
        );

        clearSelect(
            "year_level",

            "Select Subject"
        );

        clearSelect(
            "strand",

            "Select Year Level"
        );

        clearSelect(
            "sub_strand",

            "Select Strand"
        );

        clearSelect(
            "topic",

            "Select Content Description"
        );

        clearLessons();

        const learningArea =

            document.getElementById(
                "learning_area"
            ).value;

        const subjects = removeNan(
            await fetchJSON(
                API_BASE +

                "/subjects?" +

                "learning_area=" +

                encodeURIComponent(
                    learningArea
                )
            )
        );

        const select =

            document.getElementById(
                "subject"
            );

        clearSelect(
            "subject",

            "Select Subject"
        );

        subjects.forEach(subject => {

            const option =

                document.createElement("option");

            option.value = subject;

            option.textContent = subject;

            select.appendChild(option);

        });

    }

    /* ==========================================================
       Year Levels
    ========================================================== */

    async function loadYearLevels() {

        clearSelect(
            "year_level",

            "Loading..."
        );

        clearSelect(
            "strand",

            "Select Year Level"
        );

        clearSelect(
            "sub_strand",

            "Select Strand"
        );

        clearSelect(
            "topic",

            "Select Content Description"
        );

        clearLessons();

        const learningArea =

            document.getElementById(
                "learning_area"
            ).value;

        const subject =

            document.getElementById(
                "subject"
            ).value;

        const years = removeNan(
            await fetchJSON(
                API_BASE +

                "/year-levels?" +

                "learning_area=" +

                encodeURIComponent(
                    learningArea
                )

                +

                "&subject=" +

                encodeURIComponent(
                    subject
                )
            )
        );

        const select =

            document.getElementById(
                "year_level"
            );

        clearSelect(
            "year_level",

            "Select Year Level"
        );

        years.forEach(year => {

            const option =

                document.createElement("option");

            option.value = year;

            option.textContent = year;

            select.appendChild(option);

        });

    }

    /* ==========================================================
       Strands
    ========================================================== */

    async function loadStrands() {

        clearSelect(
            "strand",
            "Loading..."
        );

        clearSelect(
            "sub_strand",
            "Select Content Description"
        );

        clearSelect(
            "topic",
            "Select Content Description"
        );

        clearLessons();

        const learningArea =
            document.getElementById(
                "learning_area"
            ).value;

        const subject =
            document.getElementById(
                "subject"
            ).value;

        const yearLevel =
            document.getElementById(
                "year_level"
            ).value;

        const strands = removeNan(
            await fetchJSON(
                API_BASE +

                "/strands?" +

                "learning_area=" +

                encodeURIComponent(
                    learningArea
                )

                +

                "&subject=" +

                encodeURIComponent(
                    subject
                )

                +

                "&year_level=" +

                encodeURIComponent(
                    yearLevel
                )
            )
        );

        const select =
            document.getElementById(
                "strand"
            );

        clearSelect(
            "strand",
            "Select Strand"
        );

        strands.forEach(strand => {

            const option =
                document.createElement("option");

            option.value = strand;

            option.textContent = strand;

            select.appendChild(option);

        });

    }


    /* ==========================================================
       Curriculum Focus
       (Sub-Strand OR Content Description)
    ========================================================== */

    async function loadCurriculumFocus() {

        clearSelect(
            "sub_strand",
            "Loading..."
        );

        clearSelect(
            "topic",
            "Select Content Description"
        );

        clearLessons();

        const learningArea =
            document.getElementById(
                "learning_area"
            ).value;

        const subject =
            document.getElementById(
                "subject"
            ).value;

        const yearLevel =
            document.getElementById(
                "year_level"
            ).value;

        const strand =
            document.getElementById(
                "strand"
            ).value;

        const values =
            await fetchJSON(
                API_BASE +

                "/curriculum-focuses?" +

                "learning_area=" +

                encodeURIComponent(
                    learningArea
                )

                +

                "&subject=" +

                encodeURIComponent(
                    subject
                )

                +

                "&year_level=" +

                encodeURIComponent(
                    yearLevel
                )

                +

                "&strand=" +

                encodeURIComponent(
                    strand
                )
            );

        const select =
            document.getElementById(
                "sub_strand"
            );

        clearSelect(
            "sub_strand",
            "Select Content Description"
        );

        values.forEach(item => {

            const option =
                document.createElement("option");

            option.value =
                item.focus;

            option.textContent =
                item.focus;

            option.dataset.parentCode =
                item.parent_code;

            select.appendChild(option);

        });

    }


    /* ==========================================================
       Content Descriptions
       (Elaborations)
    ========================================================== */

    async function loadTopics() {

    clearSelect("topic", "Loading...");
    clearLessons();

    const area =
        document.getElementById("learning_area").value;

    const subject =
        document.getElementById("subject").value;

    const year =
        document.getElementById("year_level").value;

    const strand =
        document.getElementById("strand").value;

    const subStrand =
        document.getElementById("sub_strand").value;

    const values =
        await fetchJSON(
            API_BASE +
            "/build-selection?" +
            "learning_area=" + encodeURIComponent(area) +
            "&subject=" + encodeURIComponent(subject) +
            "&year_level=" + encodeURIComponent(year) +
            "&strand=" + encodeURIComponent(strand) +
            "&sub_strand=" + encodeURIComponent(subStrand)
        );

    const select =
        document.getElementById("topic");

    clearSelect(
        "topic",
        "Select Curriculum Topic"
    );

    values.forEach(item => {

        const option =
            document.createElement("option");

        option.value =
            item.parent_code;

        let description =
            String(
                item.content_description || ""
            ).trim();

        if (description) {
            description =
                description.charAt(0).toUpperCase() +
                description.slice(1);
        }

        option.textContent =
            item.curriculum_code +
            " — " +
            description;

        select.appendChild(option);
    });
}


    /* ==========================================================
       Lessons
    ========================================================== */


window.loadCurriculumFocus = loadCurriculumFocus;
window.loadTopics = loadTopics;
window.loadLessons = loadLessons;

async function handleYearLevelChange() {
    await loadStrands();

    if (window.loadCourseProgress) {
        await window.loadCourseProgress();
    }
}


window.initialiseSelection = async function() {

    document.getElementById("learning_area")
        ?.addEventListener("change", loadSubjects);

    document.getElementById("subject")
        ?.addEventListener("change", loadYearLevels);

    document.getElementById("year_level")
        ?.addEventListener(
            "change",
            handleYearLevelChange
        );

    document.getElementById("strand")
        ?.addEventListener("change", loadCurriculumFocus);

    document.getElementById("sub_strand")
        ?.addEventListener("change", loadTopics);

    await loadLearningAreas();
};


/* Topic -> Lessons */
document.addEventListener("DOMContentLoaded", function () {

    const topic =
        document.getElementById("topic");

    if (topic) {
        topic.addEventListener(
            "change",
            loadLessons
        );
    }

});

async function loadLessons() {

    const parentCode =
        document.getElementById("topic")?.value || "";

    const box =
        document.getElementById("lessons");

    if (!parentCode) {
        clearLessons();
        return;
    }

    box.innerHTML =
        "<div class='lesson'>Loading lessons...</div>";

    const lessons =
        await apiGet(
            "/lessons?parent_code=" +
            encodeURIComponent(parentCode)
        );

    box.innerHTML = "";

    const toolbar = document.createElement("div");
    toolbar.className = "lesson-selection-toolbar";

    const selectAll = document.createElement("button");
    selectAll.type = "button";
    selectAll.textContent = "Select All";

    const clearAll = document.createElement("button");
    clearAll.type = "button";
    clearAll.textContent = "Clear All";

    selectAll.addEventListener("click", () => {
        box.querySelectorAll(".lesson-select-checkbox:not(:disabled)")
            .forEach(cb => cb.checked = true);

        syncSelectedLessons();
        updateLessonSummary();
    });

    clearAll.addEventListener("click", () => {
        box.querySelectorAll(".lesson-select-checkbox")
            .forEach(cb => cb.checked = false);

        syncSelectedLessons();
        updateLessonSummary();
    });

    toolbar.append(selectAll, clearAll);
    box.appendChild(toolbar);

    lessons.forEach(lesson => {

        const row =
            document.createElement("div");

        row.className = "lesson";

        const checkbox =
            document.createElement("input");

        checkbox.type = "checkbox";
        checkbox.className =
            "lesson-select-checkbox";

        checkbox.dataset.curriculumCode =
            lesson.curriculum_code;

        let text =
            String(lesson.lesson || "").trim();

        if (text) {
            text =
                text.charAt(0).toUpperCase() +
                text.slice(1);
        }

        const label =
            document.createElement("span");

        const displayStatus = String(
            lesson.display_status || lesson.build_status || "NOT_BUILT"
        ).toUpperCase();

        const statusPresentation = {
            NOT_BUILT: ["Generate + Publish", "new-status"],
            GENERATING: ["Generating", "generating-status"],
            GENERATED: ["Resume: Publish", "generated-status"],
            PUBLISHING: ["Publishing", "publishing-status"],
            PUBLISHED: ["✓ Published · Update / Rebuild", "published-status"],
            UPDATING: ["Updating", "updating-status"],
            UPDATED: ["✓ Updated · Update / Rebuild", "updated-status"],
            REBUILDING: ["Rebuilding", "rebuilding-status"],
            REBUILT: ["✓ Rebuilt · Update / Rebuild", "rebuilt-status"],
            FAILED: ["Failed · Retry", "failed-status"]
        };

        const presentation =
            statusPresentation[displayStatus] ||
            [displayStatus.replaceAll("_", " "), "new-status"];

        const action = presentation[0];
        const actionClass = presentation[1];

        row.classList.add(
            "lesson-state-" +
            displayStatus.toLowerCase().replaceAll("_", "-")
        );

        const status =
            ' <button type="button"' +
            ' class="lesson-status lesson-action ' +
            actionClass + '"' +
            ' data-curriculum-code="' +
            lesson.curriculum_code + '"' +
            ' data-build-status="' +
            (lesson.build_status || "NOT_BUILT") + '"' +
            ' data-display-status="' +
            displayStatus + '"' +
            ' data-lesson-number="' +
            lesson.lesson_number + '"' +
            ' data-topic-id="' +
            (lesson.topic_id || "") + '"' +
            ' data-elaboration-key="' +
            encodeURIComponent(
                lesson.elaboration_key || ""
            ) + '"' +
            ' data-previous-build-id="' +
            (lesson.previous_build_id || "") + '"' +
            ' data-previous-package-id="' +
            (lesson.previous_lesson_package_id || "") + '"' +
            (lesson.build_status === "PUBLISHED"
                ? " disabled"
                : "") +
            '>' +
            action +
            '</button>';

        label.innerHTML =
            "<strong>" +
            lesson.curriculum_code +
            "</strong> — " +
            text +
            status;

        row.append(
            checkbox,
            label
        );

        box.appendChild(row);
    });

    window.curriculumLessons = lessons;
    window.selectedCurriculumLessons = [];
}

document
    .getElementById("topic")
    ?.addEventListener(
        "change",
        loadLessons
    );


function syncSelectedLessons() {

    const lessons =
        window.curriculumLessons || [];

    const selectedCodes =
        new Set(
            Array.from(
                document.querySelectorAll(
                    ".lesson-select-checkbox:checked"
                )
            ).map(cb =>
                cb.dataset.curriculumCode
            )
        );

    window.selectedCurriculumLessons =
        lessons.filter(lesson =>
            selectedCodes.has(
                String(lesson.curriculum_code)
            )
        );
}

document.addEventListener("change", event => {

    if (
        event.target.classList.contains(
            "lesson-select-checkbox"
        )
    ) {
        syncSelectedLessons();
    }

});

function updateLessonSummary() {

    const selected =
        window.selectedCurriculumLessons || [];

    const total = selected.length;

    const rebuild =
        selected.filter(
            lesson => lesson.already_built
        ).length;

    const fresh =
        total - rebuild;

    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    set("summaryLessons", total);
    set("summaryNew", fresh);
    set("summaryRebuild", rebuild);

    const mode =
        document.querySelector(
            'input[name="processing_mode"]:checked'
        )?.value || "IMMEDIATE";

    set(
        "summaryMode",
        mode === "QUEUE_STANDARD"
            ? "Queue"
            : mode === "QUEUE_BATCH"
                ? "Batch"
                : "Immediate"
    );
}

document.addEventListener("change", event => {

    if (
        event.target.classList.contains(
            "lesson-select-checkbox"
        )
    ) {
        setTimeout(updateLessonSummary, 0);
    }

    if (
        event.target.matches(
            'input[name="processing_mode"]'
        )
    ) {
        updateLessonSummary();
    }

});


function syncWholeLevelButtons() {

    const mode = document.querySelector(
        'input[name="processing_mode"]:checked'
    )?.value || "IMMEDIATE";

    const bulk =
        mode === "QUEUE_STANDARD" ||
        mode === "QUEUE_BATCH";

    const levels = [
        ["subject", "Subject"],
        ["year_level", "Year Level"],
        ["strand", "Strand"],
        ["sub_strand", "Sub-strand"],
        ["topic", "Curriculum Topic"]
    ];

    levels.forEach(([id, label]) => {

        const select =
            document.getElementById(id);

        if (!select) return;

        let button =
            document.getElementById(
                "whole_" + id
            );

        if (!bulk) {
            if (button) button.remove();
            return;
        }

        if (button) return;

        button =
            document.createElement("button");

        button.type = "button";
        button.id = "whole_" + id;
        button.className =
            "btn btn-sm btn-outline-primary bulk-action";

        button.dataset.scope = id;

        button.textContent =
            "Process Whole " + label;

        button.style.display = "block";
        button.style.width = "100%";
        button.style.marginTop = "7px";

        select.insertAdjacentElement(
            "afterend",
            button
        );
    });
}


document.addEventListener(
    "DOMContentLoaded",
    function () {

        document.querySelectorAll(
            'input[name="processing_mode"]'
        ).forEach(input => {

            input.addEventListener(
                "change",
                syncWholeLevelButtons
            );

        });

        syncWholeLevelButtons();
    }
);


function resetProcessingSelection() {

    /* Clear individual lesson selection */
    document
        .querySelectorAll(".lesson-select-checkbox")
        .forEach(cb => cb.checked = false);

    window.selectedCurriculumLessons = [];
    window.selectedProcessingScope = null;

    /* Reset summary */
    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    set("summaryLessons", "0");
    set("summaryNew", "0");
    set("summaryRebuild", "0");

    const mode = document.querySelector(
        'input[name="processing_mode"]:checked'
    )?.value || "IMMEDIATE";

    set(
        "summaryMode",
        mode === "QUEUE_STANDARD"
            ? "Queue"
            : mode === "QUEUE_BATCH"
                ? "Batch"
                : "Immediate"
    );

    /* Remove any previous whole-scope result */
    const timing =
        document.getElementById("scopeTiming");

    if (timing) {
        timing.style.display = "none";
    }
}


document.addEventListener("change", event => {

    if (
        event.target.matches(
            'input[name="processing_mode"]'
        )
    ) {
        resetProcessingSelection();

        if (
            typeof syncWholeLevelButtons === "function"
        ) {
            syncWholeLevelButtons();
        }
    }

});

function syncProcessingBasketVisibility() {

    const mode = document.querySelector(
        'input[name="processing_mode"]:checked'
    )?.value || "IMMEDIATE";

    const basket =
        document.getElementById("processingBasket");

    if (!basket) return;

    basket.style.display =
        mode === "IMMEDIATE"
            ? "none"
            : "block";
}

document.addEventListener("DOMContentLoaded", () => {

    document.querySelectorAll(
        'input[name="processing_mode"]'
    ).forEach(input => {

        input.addEventListener(
            "change",
            syncProcessingBasketVisibility
        );

    });

    syncProcessingBasketVisibility();
});


function resetUncommittedScopeSummary() {

    /* Do not clear an established basket */
    if (
        window.processingBasket &&
        window.processingBasket.length
    ) {
        return;
    }

    window.selectedProcessingScope = null;

    const set = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    };

    set("summaryLessons", "0");
    set("summaryNew", "0");
    set("summaryRebuild", "0");

    const mode = document.querySelector(
        'input[name="processing_mode"]:checked'
    )?.value || "IMMEDIATE";

    set(
        "summaryMode",
        mode === "QUEUE_BATCH"
            ? "Batch"
            : mode === "QUEUE_STANDARD"
                ? "Queue"
                : "Immediate"
    );
}

document.addEventListener("change", event => {

    if (
        [
            "learning_area",
            "subject",
            "year_level",
            "strand",
            "sub_strand",
            "topic"
        ].includes(event.target.id)
    ) {
        resetUncommittedScopeSummary();
    }

});
