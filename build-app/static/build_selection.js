"use strict";

let buildSelectionData = [];

function safeText(value) {
    if (value === null || value === undefined) {
        return "";
    }
    return String(value);
}


async function loadBuildSelection() {

    const learningArea = document.getElementById("learning_area").value;
    const subject = document.getElementById("subject").value;
    const yearLevel = document.getElementById("year_level").value;
    const strand = document.getElementById("strand").value;
    const subStrand = document.getElementById("sub_strand").value;
    const container = document.getElementById("queueLessons");

    buildSelectionData = [];

    document.getElementById("selection_summary").textContent =
        "Selected: 0 Content Descriptions / 0 Lessons";

    if (!learningArea || !subject || !yearLevel || !strand) {
        container.textContent =
            "Complete the curriculum selections above.";
        return;
    }

    container.textContent =
        "Loading Content Descriptions and Lessons...";

    const params = new URLSearchParams();

    params.set("learning_area", learningArea);
    params.set("subject", subject);
    params.set("year_level", yearLevel);
    params.set("strand", strand);

    if (subStrand) {
        params.set("sub_strand", subStrand);
    }

    const url = API_BASE + "/build-selection?" + params.toString();

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("HTTP " + response.status);
        }

        buildSelectionData = await response.json();
        renderBuildSelection();

    } catch (error) {
        console.error("Build selection failed:", error);
        container.textContent =
            "Unable to load Content Descriptions and Lessons.";
    }
}


function renderBuildSelection() {
    const container = document.getElementById("queueLessons");
    container.replaceChildren();

    if (!Array.isArray(buildSelectionData) || buildSelectionData.length === 0) {
        const empty = document.createElement("div");
        empty.className = "lesson";
        empty.textContent = "No Content Descriptions found.";
        container.appendChild(empty);
        updateSelectionSummary();
        return;
    }

    buildSelectionData.forEach(function(group, groupIndex) {
        const groupBox = document.createElement("div");
        groupBox.className = "content-group";

        const heading = document.createElement("div");
        heading.className = "content-heading";

        const headingLabel = document.createElement("label");
        const parentBox = document.createElement("input");
        parentBox.type = "checkbox";
        parentBox.className = "content-checkbox";
        parentBox.dataset.groupIndex = String(groupIndex);

        const headingText = document.createElement("span");
        headingText.textContent =
            safeText(group.curriculum_code) +
            " - " +
            safeText(group.content_description);

        headingLabel.appendChild(parentBox);
        headingLabel.appendChild(headingText);
        heading.appendChild(headingLabel);
        groupBox.appendChild(heading);

        const lessonList = document.createElement("div");
        lessonList.className = "lesson-list";

        group.lessons.forEach(function(lesson, lessonIndex) {
            const row = document.createElement("div");
            row.className = "lesson-row";

            const label = document.createElement("label");
            const lessonBox = document.createElement("input");
            lessonBox.type = "checkbox";
            lessonBox.className = "lesson-checkbox";
            lessonBox.dataset.groupIndex = String(groupIndex);
            lessonBox.dataset.lessonIndex = String(lessonIndex);

            const text = document.createElement("span");
            const code = document.createElement("strong");
            code.textContent = safeText(lesson.curriculum_code);

            const description = document.createTextNode(
                " - " + safeText(lesson.lesson) + " "
            );

            const status = document.createElement("span");
            status.className = "lesson-status";
            status.textContent = safeText(
                lesson.build_status || "NOT_BUILT"
            );

            text.appendChild(code);
            text.appendChild(description);
            text.appendChild(status);

            label.appendChild(lessonBox);
            label.appendChild(text);
            row.appendChild(label);
            lessonList.appendChild(row);
        });

        groupBox.appendChild(lessonList);
        container.appendChild(groupBox);
    });

    attachSelectionEvents();
    updateSelectionState();
}


function attachSelectionEvents() {
    document.querySelectorAll(".content-checkbox").forEach(function(parent) {
        parent.addEventListener("change", function() {
            const groupIndex = parent.dataset.groupIndex;
            const children = document.querySelectorAll(
                ".lesson-checkbox[data-group-index=" + groupIndex + "]"
            );

            children.forEach(function(child) {
                child.checked = parent.checked;
            });

            updateSelectionState();
        });
    });

    document.querySelectorAll(".lesson-checkbox").forEach(function(child) {
        child.addEventListener("change", updateSelectionState);
    });
}


function updateSelectionState() {
    document.querySelectorAll(".content-checkbox").forEach(function(parent) {
        const groupIndex = parent.dataset.groupIndex;
        const children = Array.from(document.querySelectorAll(
            ".lesson-checkbox[data-group-index=" + groupIndex + "]"
        ));

        const checkedCount = children.filter(function(child) {
            return child.checked;
        }).length;

        parent.checked =
            children.length > 0 && checkedCount === children.length;

        parent.indeterminate =
            checkedCount > 0 && checkedCount < children.length;
    });

    updateSelectionSummary();
}


function updateSelectionSummary() {
    const selectedLessons = document.querySelectorAll(
        ".lesson-checkbox:checked"
    ).length;

    let selectedGroups = 0;

    document.querySelectorAll(".content-checkbox").forEach(function(parent) {
        if (parent.checked || parent.indeterminate) {
            selectedGroups += 1;
        }
    });

    document.getElementById("selection_summary").textContent =
        "Selected: " +
        selectedGroups +
        " Content Description" +
        (selectedGroups === 1 ? "" : "s") +
        " / " +
        selectedLessons +
        " Lesson" +
        (selectedLessons === 1 ? "" : "s");
}


function getSelectedLessonItems() {
    const items = [];

    document.querySelectorAll(".lesson-checkbox:checked").forEach(function(box) {
        const groupIndex = Number(box.dataset.groupIndex);
        const lessonIndex = Number(box.dataset.lessonIndex);

        const group = buildSelectionData[groupIndex];
        const lesson = group.lessons[lessonIndex];

        items.push({
            parent_code: lesson.parent_code,
            curriculum_code: lesson.curriculum_code,
            content_description: lesson.content_description,
            topic_id: lesson.topic_id,
            lesson_number: lesson.lesson_number,
            lesson_text: lesson.lesson,
            build_status: lesson.build_status,
            can_build: lesson.can_build,
            can_update: lesson.can_update,
            previous_build_id: lesson.previous_build_id,
            previous_lesson_package_id: lesson.previous_lesson_package_id
        });
    });

    return items;
}


function selectAllBuildLessons() {
    document.querySelectorAll(".lesson-checkbox").forEach(function(box) {
        box.checked = true;
    });
    updateSelectionState();
}

function clearAllBuildLessons() {
    document.querySelectorAll(".lesson-checkbox").forEach(function(box) {
        box.checked = false;
    });
    updateSelectionState();
}


document.getElementById("sub_strand").addEventListener(
    "change",
    function() {
        const selectedMode =
            document.querySelector(
                'input[name="processing_mode"]:checked'
            );

        if (
            selectedMode &&
            selectedMode.value !== "IMMEDIATE"
        ) {
            loadBuildSelection();
        }
    }
);

document.getElementById("queueSelectAll").addEventListener(
    "click",
    selectAllBuildLessons
);

document.getElementById("queueClearAll").addEventListener(
    "click",
    clearAllBuildLessons
);



/* Queue V1 - initialize processing-mode UI after this script loads. */
syncProcessingModeUI();
