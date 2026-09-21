const API_BASE =
        "https://api.ronosschool.com";

    /* ==========================================================
       Generic Helpers
    ========================================================== */

    function clearSelect(
        id,
        placeholder
    ) {

        document.getElementById(id).innerHTML =

            `<option value="">${placeholder}</option>`;

    }

    function clearLessons() {
        curriculumLessons = [];
        selectedCurriculumLesson = null;
        selectedCurriculumLessons = [];

        document.getElementById("lessons").innerHTML =
            "<div class='lesson'>Select a Content Description first...</div>";
    }

    function removeNan(values) {

        return values.filter(v =>

            v !== null &&

            v !== "" &&

            String(v).toLowerCase() !== "nan"
        );

    }

    async function fetchJSON(url) {

        const response = await fetch(url);

        if (!response.ok) {

            throw new Error(
                await response.text()
            );

        }

        return await response.json();

    }

    /* ==========================================================
       Learning Areas
    ========================================================== */

    async function loadLearningAreas() {

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
                item.display;

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

        clearSelect(
            "topic",
            "Loading..."
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

        const curriculumFocus =
            document.getElementById(
                "sub_strand"
            ).value;

        const topics =

            await fetchJSON(
                API_BASE +

                "/topics?" +

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

                +

                "&sub_strand=" +

                encodeURIComponent(
                    curriculumFocus
                )
            );

        const select =
            document.getElementById(
                "topic"
            );

        clearSelect(
            "topic",
            "Select Content Description"
        );

        topics.forEach(topic => {

            const option =
                document.createElement("option");

            option.value =
                topic.parent_code;

            option.textContent =
                topic.topic;

            select.appendChild(option);

        });

    }


    /* ==========================================================
       Lessons
    ========================================================== */

    let curriculumLessons = [];
    let selectedCurriculumLesson = null;
      let selectedCurriculumLessons = [];


    async function loadLessons() {

        const parentCode =
            document.getElementById("topic").value;

        curriculumLessons = [];
        selectedCurriculumLesson = null;
        selectedCurriculumLessons = [];

        const container =
            document.getElementById("lessons");

        if (!parentCode) {
            container.innerHTML =
                "<div class='lesson'>Select a Content Description first...</div>";
            return;
        }

        container.innerHTML =
            "<div class='lesson'>Loading lessons...</div>";

        curriculumLessons = await fetchJSON(
            API_BASE
            + "/lessons?parent_code="
            + encodeURIComponent(parentCode)
        );

        displaySelectedCurriculumLesson();
    }





    function displaySelectedCurriculumLesson() {

        const container =
            document.getElementById("lessons");

        container.innerHTML = "";

        selectedCurriculumLessons = [];
        selectedCurriculumLesson = null;

        curriculumLessons.forEach(lesson => {

            const div =
                document.createElement("div");

            div.className = "lesson";

            const label =
                document.createElement("label");

            if (lesson.can_build) {

                const box =
                    document.createElement("input");

                box.type = "checkbox";
                box.className =
                    "lesson-select-checkbox";

                box.dataset.curriculumCode =
                    lesson.curriculum_code;

                box.addEventListener(
                    "change",
                    syncLessonSelection
                );

                label.appendChild(box);
            }

            const code =
                document.createElement("strong");

            code.textContent =
                lesson.curriculum_code;

            label.appendChild(code);

            label.appendChild(
                document.createTextNode(
                    " — " + lesson.lesson
                )
            );

            div.appendChild(label);

if (lesson.already_built) {

            div.classList.add("lesson-published");

            const status = document.createElement("span");
            status.className = "published-status";
            status.textContent =
                "✓ Already Published — Build "
                + lesson.previous_build_id;
            div.appendChild(status);

            const button = document.createElement("button");
            button.type = "button";
            button.className = "update-elaboration";
            button.textContent = "Update / Rebuild";

            button.dataset.lessonNumber = lesson.lesson_number;
            button.dataset.topic = lesson.topic_id;
            button.dataset.curriculumCode = lesson.curriculum_code;
            button.dataset.elaborationKey = lesson.elaboration_key;
            button.dataset.previousBuildId = lesson.previous_build_id;
            button.dataset.previousPackageId =
                lesson.previous_lesson_package_id;

            div.appendChild(button);

        } else if (lesson.generated_pending) {

            div.classList.add("lesson-generated");

            const status = document.createElement("span");
            status.className = "generated-status";
            status.textContent =
                "✓ Generated — Awaiting Publication — Build "
                + lesson.pending_build_id;
            div.appendChild(status);

            const button = document.createElement("button");
            button.type = "button";
            button.className = "publish-now-button";
            button.textContent = "Publish Now";

            button.addEventListener(
                "click",
                function () {
                    publishGeneratedLesson(
                        lesson.pending_lesson_package_id,
                        button
                    );
                }
            );

            div.appendChild(button);

        } else {

            div.classList.add("lesson-available");

            const status = document.createElement("span");
            status.textContent = "Available for new build";
            div.appendChild(status);

        }



            container.appendChild(div);
        });

        syncLessonSelection();
    }


    function syncLessonSelection() {

        const selectedCodes =
            new Set(
                Array.from(
                    document.querySelectorAll(
                        ".lesson-select-checkbox:checked"
                    )
                ).map(
                    box =>
                        box.dataset.curriculumCode
                )
            );

        selectedCurriculumLessons =
            curriculumLessons.filter(
                lesson =>
                    selectedCodes.has(
                        String(lesson.curriculum_code)
                    )
            );

        selectedCurriculumLesson =
            selectedCurriculumLessons.length === 1
                ? selectedCurriculumLessons[0]
                : null;
    }


    function selectAllLessons() {

        document.querySelectorAll(
            ".lesson-select-checkbox"
        ).forEach(
            box => box.checked = true
        );

        syncLessonSelection();
    }


    function clearAllLessons() {

        document.querySelectorAll(
            ".lesson-select-checkbox"
        ).forEach(
            box => box.checked = false
        );

        syncLessonSelection();
    }





    async function publishGeneratedLesson(
        lessonPackageId,
        button
    ) {

        if (!lessonPackageId) {
            alert(
                "Generated lesson package ID is missing."
            );
            return;
        }

        const originalText =
            button.textContent;

        button.disabled = true;
        button.textContent =
            "Publishing...";

        try {

            const response = await fetch(
                "/api/publish-generated",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json"
                    },
                    body: JSON.stringify({
                        lesson_package_id:
                            lessonPackageId
                    })
                }
            );

            const result =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    result.detail
                    ||
                    "Moodle publication failed."
                );
            }

            if (result.status !== "SUCCESS") {

                throw new Error(
                    "Publisher did not return SUCCESS."
                );
            }

            showStatus(
                "Lesson published successfully.",
                true
            );

            await loadLessons();

        }
        catch (error) {

            console.error(
                "Publish generated lesson failed:",
                error
            );

            showStatus(
                "Moodle publication failed: "
                + error.message,
                false
            );

            button.disabled = false;
            button.textContent =
                originalText;
        }
    }
    /* ==========================================================
       Processing Mode UI
    ========================================================== */

    function syncProcessingModeUI() {

        const selected =
            document.querySelector(
                'input[name="processing_mode"]:checked'
            );

        const mode =
            selected
                ? selected.value
                : "IMMEDIATE";

        const immediateSelection =
            document.getElementById(
                "immediateSelection"
            );

        const queueSelection =
            document.getElementById(
                "queueMultiSelection"
            );

        const isQueue =
            mode === "QUEUE_STANDARD"
            ||
            mode === "QUEUE_BATCH";

        immediateSelection.style.display =
            isQueue
                ? "none"
                : "block";

        queueSelection.style.display =
            isQueue
                ? "block"
                : "none";

        if (isQueue) {
            loadBuildSelection();
        }
    }


    /* ==========================================================
       Event Wiring
    ========================================================== */

    window.addEventListener(
        "DOMContentLoaded",

        () => {

            loadLearningAreas();

        }
    );


    document

        .getElementById(
            "learning_area"
        )

        .addEventListener(
            "change",

            loadSubjects
        );


    document

        .getElementById(
            "subject"
        )

        .addEventListener(
            "change",

            loadYearLevels
        );


    document

        .getElementById(
            "year_level"
        )

        .addEventListener(
            "change",

            loadStrands
        );


    document

        .getElementById(
            "strand"
        )

        .addEventListener(
            "change",

            loadCurriculumFocus
        );


    document

        .getElementById(
            "sub_strand"
        )

        .addEventListener(
            "change",

            loadTopics
        );


    document

        .getElementById(
            "topic"
        )

        .addEventListener(
            "change",

            loadLessons
        );


    document
        .getElementById("selectAllLessons")
        .addEventListener(
            "click",
            selectAllLessons
        );

    document
        .getElementById("clearAllLessons")
        .addEventListener(
            "click",
            clearAllLessons
        );


    document
        .querySelectorAll(
            'input[name="processing_mode"]'
        )
        .forEach(function(radio) {

            radio.addEventListener(
                "change",
                syncProcessingModeUI
            );

        });


    /* ==========================================================
       Progress Dialog
    ========================================================== */

    function showProgress(message, percent) {

        document.getElementById(
            "progressOverlay"
        ).style.display = "block";

        document.getElementById(
            "progressMessage"
        ).textContent = message;

        document.getElementById(
            "progressFill"
        ).style.width = percent + "%";

        document.getElementById(
            "progressPercent"
        ).textContent = percent + "%";

    }


    function hideProgress() {

        document.getElementById(
            "progressOverlay"
        ).style.display = "none";

    }


    /* ==========================================================
       Build Job Polling
    ========================================================== */

    async function waitForBuildJob(jobId) {

        while (true) {

            const response =
                await fetch(
                    "/api/build-status/"
                    + encodeURIComponent(jobId),
                    {
                        cache: "no-store"
                    }
                );

            const job =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    job.detail
                    ||
                    JSON.stringify(job)
                );
            }

            showProgress(
                job.message
                || "Building lesson package...",

                Number(
                    job.percent
                    ?? 0
                )
            );

            if (job.status === "SUCCESS") {

                return job.result;
            }

            if (job.status === "FAILED") {

                throw new Error(
                    job.error
                    ||
                    "Lesson package build failed."
                );
            }

            await new Promise(
                resolve =>
                    setTimeout(
                        resolve,
                        1000
                    )
            );
        }
    }


    /* ==========================================================
       Status Panel
    ========================================================== */

    function showStatus(
        message,
        success = true
    ) {

        const status =

            document.getElementById(
                "status"
            );

        status.style.display = "block";

        status.className =

            success

                ? "success"

                : "error";

        status.innerHTML = message;

    }


    /* ==========================================================
       Build Request
    ========================================================== */

    async function submitBuild(event) {

        event.preventDefault();

        const processingMode =
            document.querySelector(
                'input[name="processing_mode"]:checked'
            ).value;

        const isQueue =
            processingMode === "QUEUE_STANDARD"
            ||
            processingMode === "QUEUE_BATCH";

        let lessonNumbers = [];
        let topicId = null;
        let queueItems = [];

        if (isQueue) {

            queueItems =
                getSelectedLessonItems();

            if (!queueItems.length) {
                alert(
                    "Please select at least one lesson / elaboration."
                );
                return;
            }

            const invalidItem =
                queueItems.find(
                    item => !item.can_build
                );

            if (invalidItem) {
                alert(
                    "One or more selected lessons cannot be built."
                );
                return;
            }

        } else {

            syncLessonSelection();

            if (!selectedCurriculumLessons.length) {
                alert(
                    "Please select at least one lesson / elaboration."
                );
                return;
            }

            const invalidLesson =
                selectedCurriculumLessons.find(
                    lesson => !lesson.can_build
                );

            if (invalidLesson) {
                alert(
                    "One or more selected lessons cannot be built."
                );
                return;
            }

            lessonNumbers =
                selectedCurriculumLessons.map(
                    lesson =>
                        parseInt(
                            lesson.lesson_number
                        )
                );

            topicId =
                selectedCurriculumLessons[0].topic_id;
        }

        const payload = {

            requested_by:

            document.getElementById(
                "requested_by"
            ).value,

            learning_area:

            document.getElementById(
                "learning_area"
            ).value,

            subject:

            document.getElementById(
                "subject"
            ).value,

            year_level:

            document.getElementById(
                "year_level"
            ).value,

            strand:

            document.getElementById(
                "strand"
            ).value,

            sub_strand:

            document.getElementById(
                "sub_strand"
            ).value,

            parent_code:
                isQueue
                    ? ""
                    : document.getElementById(
                        "topic"
                    ).value,

            topic_id:
                isQueue
                    ? ""
                    : topicId,

            lesson_numbers:
                isQueue
                    ? []
                    : lessonNumbers,

            items:
                isQueue
                    ? queueItems
                    : [],

            processing_mode:
                processingMode,

            publication_mode:
                "IMMEDIATE"

        };

        const button =

            document.getElementById(
                "buildButton"
            );

        button.disabled = true;

        if (isQueue) {
            showProgress(
                "Saving build request...",
                10
            );
        } else {
            showProgress(
                "Creating workbook...",
                10
            );
        }

        try {

            showProgress(
                isQueue
                    ? "Adding selected lessons to queue..."
                    : "Preparing lesson package...",

                25
            );

            const response =

                await fetch(
                    "/api/build",

                    {

                        method: "POST",

                        headers: {

                            "Content-Type":

                                "application/json"

                        },

                        body: JSON.stringify(
                            payload
                        )

                    }
                );

            const accepted =
                await response.json();

            if (!response.ok) {

                throw new Error(
                    accepted.detail
                    ||

                    JSON.stringify(accepted)
                );
            }

            if (accepted.status === "QUEUED") {

                hideProgress();

                showStatus(
                    `
                    <h3>Build Request Queued Successfully</h3>

                    <p>
                    <strong>Request ID:</strong>
                    ${accepted.request_id}
                    </p>

                    <p>
                    Your request has been saved.
                    You may close this page.
                    </p>

                    <p>
                    Processing mode:
                    <strong>
                    ${accepted.processing_mode === "QUEUE_BATCH"
                        ? "OpenAI Batch"
                        : "Standard Queue"}
                    </strong>
                    </p>
                    `,
                    true
                );

                button.disabled = false;

                return;
            }

            if (!accepted.job_id) {

                throw new Error(
                    "Build App did not return a job ID."
                );
            }

            const result =
                await waitForBuildJob(
                    accepted.job_id
                );

            window.buildResult = result;

            showProgress(
                "Lesson Package Complete.",

                100
            );

            await new Promise(
                resolve =>

                    setTimeout(
                        resolve,

                        700
                    )
            );

            hideProgress();

            showStatus(
                `
            <h3>✅ Lesson Package Created Successfully</h3>

            <p>

            <strong>Build Status:</strong>

            ${result.status}

            </p>

            <p>

            <strong>Lesson Package:</strong>

            ${result.lesson_package_id ?? "-"}

            </p>

            <p>

            <strong>Workbook:</strong>

            ${result.workbook_path ?? "-"}

            </p>

            <p>

            <strong>Message:</strong>

            Your lesson package has been generated successfully.

            </p>

            `,

                true
            );

        } catch (err) {

            hideProgress();

            console.error(err);

            showStatus(
                `

            <h3>❌ Build Failed</h3>

            <p>

            ${err.message}

            </p>

            `,

                false
            );

        } finally {

            button.disabled = false;

        }

    }
    /* =====================================================
       Selective Update / Rebuild Existing Elaboration
    ===================================================== */

    let selectedUpdateLesson = null;



    function closeUpdateModal(clearSelection = true) {

        const overlay =
            document.getElementById(
                "updateModalOverlay"
            );

        overlay.style.display = "none";

        if (clearSelection) {
            selectedUpdateLesson = null;
        }

        document
            .querySelectorAll(
                ".update-component"
            )
            .forEach(
                checkbox => {
                    checkbox.checked = false;
                }
            );

        document.getElementById(
            "updateSelectAll"
        ).checked = false;

    }


    document
        .getElementById("lessons")
        .addEventListener(
            "click",

            function (event) {

                const button =
                    event.target.closest(
                        ".update-elaboration"
                    );

                if (!button) {
                    return;
                }

                selectedUpdateLesson = {

                    lessonNumber:
                        parseInt(
                            button.dataset.lessonNumber
                        ),

                    topicId:
                        button.dataset.topic,

                    elaborationKey:
                        button.dataset.elaborationKey,

                    previousBuildId:
                        button.dataset.previousBuildId,

                    previousPackageId:
                        button.dataset.previousPackageId

                };

                document.getElementById(
                    "updateModalTitle"
                ).textContent =
                    "Update / Rebuild Lesson "
                    + selectedUpdateLesson.lessonNumber;

                document.getElementById(
                    "updateModalSubtitle"
                ).textContent =
                    "Previously published in Build "
                    + selectedUpdateLesson.previousBuildId
                    + ".";

                document
                    .querySelectorAll(
                        ".update-component"
                    )
                    .forEach(
                        checkbox => {
                            checkbox.checked = false;
                        }
                    );

                document.getElementById(
                    "updateSelectAll"
                ).checked = false;

                document.getElementById(
                    "updateModalOverlay"
                ).style.display = "flex";

            }
        );


    /* =====================================================
       Select All Update Components
    ===================================================== */

    document
        .getElementById(
            "updateSelectAll"
        )
        .addEventListener(
            "change",

            function () {

                const checked =
                    this.checked;

                document
                    .querySelectorAll(
                        ".update-component:not(:disabled)"
                    )
                    .forEach(
                        checkbox => {
                            checkbox.checked = checked;
                        }
                    );

            }
        );


    /* =====================================================
       Keep Select All State Synchronized
    ===================================================== */

    document
        .querySelectorAll(
            ".update-component"
        )
        .forEach(
            checkbox => {

                checkbox.addEventListener(
                    "change",

                    function () {

                        const available =
                            Array.from(
                                document.querySelectorAll(
                                    ".update-component:not(:disabled)"
                                )
                            );

                        document.getElementById(
                            "updateSelectAll"
                        ).checked =
                            available.length > 0
                            &&
                            available.every(
                                item => item.checked
                            );

                    }
                );

            }
        );


    /* =====================================================
       Cancel Selective Update
    ===================================================== */

    document
        .getElementById(
            "updateCancelButton"
        )
        .addEventListener(
            "click",
            closeUpdateModal
        );


    /* =====================================================
       Submit Selective Update
    ===================================================== */

    document
        .getElementById(
            "updateSubmitButton"
        )
        .addEventListener(
            "click",

            async function () {

                if (!selectedUpdateLesson) {

                    alert(
                        "No lesson has been selected "
                        + "for update."
                    );

                    return;
                }

                const components =
                    Array.from(
                        document.querySelectorAll(
                            ".update-component:checked"
                        )
                    ).map(
                        checkbox => checkbox.value
                    );

                if (components.length === 0) {

                    alert(
                        "Please select at least one "
                        + "component to update."
                    );

                    return;
                }

                const payload = {

                    requested_by:
                        document.getElementById(
                            "requested_by"
                        ).value,

                    learning_area:
                        document.getElementById(
                            "learning_area"
                        ).value,

                    subject:
                        document.getElementById(
                            "subject"
                        ).value,

                    year_level:
                        document.getElementById(
                            "year_level"
                        ).value,

                    strand:
                        document.getElementById(
                            "strand"
                        ).value,

                    sub_strand:
                        document.getElementById(
                            "sub_strand"
                        ).value,

                    parent_code:
                        document.getElementById(
                            "topic"
                        ).value,

                    topic_id:
                        selectedUpdateLesson.topicId,

                    lesson_numbers: [
                        selectedUpdateLesson.lessonNumber
                    ],

                    build_mode:
                        "UPDATE",

                    update_components:
                        components,

                    publication_mode: "IMMEDIATE"

                };

                const updateButton = this;

                updateButton.disabled = true;

                closeUpdateModal(false);

                showProgress(
                    "Preparing selected update...",
                    15
                );

                try {

                    showProgress(
                        "Generating selected components...",
                        35
                    );

                    const response =
                        await fetch(
                            "/api/build",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type":
                                        "application/json"
                                },

                                body:
                                    JSON.stringify(
                                        payload
                                    )
                            }
                        );

                    const accepted =
                        await response.json();

                    if (!response.ok) {

                        throw new Error(
                            accepted.detail
                            ||
                            JSON.stringify(
                                accepted
                            )
                        );
                    }

                    if (!accepted.job_id) {

                        throw new Error(
                            "Build App did not return a job ID."
                        );
                    }

                    const result =
                        await waitForBuildJob(
                            accepted.job_id
                        );

                    showProgress(
                        "Selected update complete.",
                        100
                    );

                    await new Promise(
                        resolve =>
                            setTimeout(
                                resolve,
                                700
                            )
                    );

                    hideProgress();

                    showStatus(
                        `
                        <h3>
                        Selective Update Completed
                        </h3>

                        <p>
                        <p>
                        The selected lesson components
                        were regenerated and updated
                        successfully in Moodle.
                        </p>
                        </p>
                        `,
                        true
                    );

                }

                catch (err) {

                    hideProgress();

                    console.error(err);

                    showStatus(
                        `
                        <h3>
                        Update Generation Stopped
                        </h3>

                        <p>
                        ${err.message}
                        </p>
                        `,
                        false
                    );

                }

                finally {

                    updateButton.disabled = false;

                }

            }
        );

	/* ==========================================================
       Build Button
    ========================================================== */

    document

        .getElementById(
            "buildForm"
        )

        .addEventListener(
            "submit",

            submitBuild
        );


    /* ==========================================================
       Utility
    ========================================================== */

    function resetForm() {

        document

            .getElementById(
                "buildForm"
            )

            .reset();

        clearLessons();

        clearSelect(
            "subject",

            "Select Learning Area"
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

            "Select Content Description"
        );

        clearSelect(
            "topic",

            "Select Content Description"
        );

    }


    /* ==========================================================
       Application Ready
    ========================================================== */

    console.log(
        "Rono's School AI Curriculum Builder Ready"
    );
