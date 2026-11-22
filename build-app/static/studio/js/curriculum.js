console.log("Curriculum Studio Core Loaded");

(function () {
    const greeting = document.getElementById("timeGreeting");
    const localTime = document.getElementById("localTime");
    const userLocalTime = document.getElementById("userLocalTime");

    if (!greeting) {
        return;
    }

    function updateUserTime() {
        const now = new Date();
        const hour = now.getHours();

        const timeText = now.toLocaleTimeString([], {
            hour: "numeric",
            minute: "2-digit"
        });

        if (hour < 12) {
            greeting.childNodes[0].nodeValue = "Good Morning ";
        } else if (hour < 17) {
            greeting.childNodes[0].nodeValue = "Good Afternoon ";
        } else {
            greeting.childNodes[0].nodeValue = "Good Evening ";
        }

        if (localTime) {
            localTime.textContent = timeText;
        }

        if (userLocalTime) {
            userLocalTime.textContent = timeText;
        }
    }

    updateUserTime();
    setInterval(updateUserTime, 30000);
})();


(function () {
    async function loadDashboardCourseProgress() {
        const cards = Array.from(document.querySelectorAll(".dashboard-card"));
        const progressCard = cards.find(card => card.textContent.includes("Curriculum Progress"));
        const queueCard = cards.find(card => card.textContent.includes("Active Queue"));

        try {
            const response = await fetch("/api/dashboard/course-progress?subject=English&year_level=Year%203");
            if (!response.ok) return;

            const data = await response.json();
            const course = data.course;
            const queue = data.queue;

            document.querySelectorAll(".studio-stat").forEach((item) => {
                const label = item.textContent;
                const number = item.querySelector("strong");
                if (!number) return;

                if (label.includes("Unpublished")) number.textContent = course.remaining;
                else if (label.includes("Batch publishing")) {
                    number.textContent = queue.active
                        ? Math.max(
                            Number(queue.total || 0)
                            - Number(queue.completed || 0),
                            0
                        )
                        : 0;
                }
                else if (label.includes("rebuilding")) number.textContent = course.update_ready;
                else if (label.includes("Failed")) number.textContent = course.failed;
            });

            document.querySelectorAll(".lesson-summary-strip strong").forEach((item) => {
                const parentText = item.parentElement.textContent;
                if (parentText.includes("Last Completed")) item.textContent = course.last_completed || "None yet";
                else if (parentText.includes("Next Lesson")) item.textContent = course.next_lesson || "Complete";
                else if (parentText.includes("Subject Area")) item.textContent = course.label;
            });

            if (progressCard) {
                const titleText = progressCard.querySelector(".framework-name");
                const fill = progressCard.querySelector(".progress-fill");
                const value = progressCard.querySelector(".progress-value");
                const stats = progressCard.querySelectorAll(".stat-number");

                if (titleText) titleText.textContent = course.label;
                if (fill) fill.style.width = `${course.progress}%`;
                if (value) value.textContent = `${course.progress}%`;
                if (stats[0]) stats[0].textContent = course.published;
                if (stats[1]) stats[1].textContent = course.remaining;
            }

            if (queueCard) {
                const liveBadge = document.getElementById("queueLiveBadge");
                const stage = queueCard.querySelector(".queue-stage");
                const fill = queueCard.querySelector(".queue-fill");
                const currentLesson = queueCard.querySelector(".current-lesson strong");
                const stats = queueCard.querySelectorAll(".stat-number");
                const processingPill = queueCard.querySelector(".processing-pill");

                if (liveBadge) liveBadge.style.display = queue.active ? "inline-flex" : "none";
                if (processingPill) {
                    processingPill.textContent = queue.active
                        ? queue.processing_mode
                        : "No active processing";
                }
                if (stage) stage.textContent = queue.active ? queue.status : "No active processing";
                if (fill) fill.style.width = `${queue.percent}%`;
                if (currentLesson) currentLesson.textContent = queue.current_lesson || "No active lesson";
                if (stats[0]) stats[0].textContent = `${queue.completed} / ${queue.total}`;
                if (stats[1]) stats[1].textContent = queue.eta;
            }
        } catch (error) {
            console.warn("Dashboard progress unavailable", error);
        }
    }

    loadDashboardCourseProgress();
    setInterval(loadDashboardCourseProgress, 5000);
})();

(function () {
    const frameworkSelect = document.getElementById("curriculum_framework");
    const frameworkNotice = document.getElementById("curriculumFrameworkNotice");

    if (!frameworkSelect || !frameworkNotice) {
        return;
    }

    function updateCurriculumFrameworkNotice() {
        const selected = frameworkSelect.options[frameworkSelect.selectedIndex];
        const status = selected.dataset.status || "planned";
        const name = selected.value;

        frameworkNotice.classList.remove("is-active", "is-planned");

        if (status === "active") {
            frameworkNotice.classList.add("is-active");
            frameworkNotice.textContent = `${name} is connected to the current course builder data.`;
            return;
        }

        frameworkNotice.classList.add("is-planned");
        frameworkNotice.textContent = `${name} is listed for selection. Course data needs to be added before lessons can load for this framework.`;
    }

    frameworkSelect.addEventListener("change", updateCurriculumFrameworkNotice);
    updateCurriculumFrameworkNotice();
})();

(function () {
    function iconForType(type) {
        if (type === "success") {
            return "✓";
        }

        if (type === "warning") {
            return "!";
        }

        if (type === "danger") {
            return "!";
        }

        return "i";
    }

    function classForType(type) {
        if (type === "success") {
            return "is-success";
        }

        if (type === "warning") {
            return "is-warning";
        }

        if (type === "danger") {
            return "is-danger";
        }

        return "is-info";
    }

    function findPanelByHeading(text) {
        return Array.from(document.querySelectorAll(".dashboard-card, .studio-card, section, div"))
            .find((item) => {
                const heading = item.querySelector("h2, h3, .card-title");
                return heading && heading.textContent.trim() === text;
            });
    }

    async function loadDashboardActivity() {
        try {
            const response = await fetch("/api/dashboard/activity");

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            const notificationsPanel = findPanelByHeading("Notifications");
            if (notificationsPanel) {
                const items = data.notifications.map((item) => `
                    <div class="activity-row">
                        <span class="activity-icon ${classForType(item.type)}">${iconForType(item.type)}</span>
                        <span>
                            <strong>${item.title}</strong>
                            <small>${item.time}</small>
                        </span>
                    </div>
                `).join("");

                const viewAll = notificationsPanel.querySelector("a");
                notificationsPanel.innerHTML = `
                    <h2>Notifications</h2>
                    ${viewAll ? '<a href="/queue">View All</a>' : ''}
                    <div class="activity-list">${items}</div>
                `;
            }

            const recentPanel = findPanelByHeading("Recent Publications");
            if (recentPanel) {
                recentPanel.innerHTML = `
                    <h2>Recent Publications</h2>
                    <div class="activity-list">
                        ${data.recent_publications.map((item) => `
                            <div class="publication-row">
                                <span class="activity-icon is-success">✓</span>
                                <span>
                                    <strong>${item.course}</strong>
                                    <small>${item.lessons} lessons</small>
                                </span>
                                <em>${item.status}</em>
                            </div>
                        `).join("")}
                    </div>
                `;
            }

            const statusPanel = findPanelByHeading("Platform Status");
            if (statusPanel) {
                statusPanel.innerHTML = `
                    <h2>Platform Status</h2>
                    <div class="activity-list">
                        ${data.platform_status.map((item) => `
                            <div class="status-row">
                                <span>${item.name}</span>
                                <strong><i></i>${item.status}</strong>
                            </div>
                        `).join("")}
                    </div>
                `;
            }
        } catch (error) {
            console.warn("Dashboard activity unavailable", error);
        }
    }

    loadDashboardActivity();
    setInterval(loadDashboardActivity, 30000);
})();

(function () {
    const courseSelect = document.getElementById("dashboardCourseSelect");

    if (!courseSelect) {
        return;
    }

    async function loadDashboardCourses() {
        const response = await fetch("/api/dashboard/courses");

        if (!response.ok) {
            return;
        }

        const data = await response.json();
        const courses = data.courses || [];

        courseSelect.innerHTML = "";

        courses.forEach((course, index) => {
            const option = document.createElement("option");
            option.value = JSON.stringify({
                framework: course.framework,
                subject: course.subject,
                year_level: course.year_level
            });
            option.textContent = course.label;

            if (index === 0) {
                option.selected = true;
            }

            courseSelect.appendChild(option);
        });

        if (courses.length) {
            await loadSelectedCourseProgress();
        }
    }

    async function loadSelectedCourseProgress() {
        if (!courseSelect.value) {
            return;
        }

        const selected = JSON.parse(courseSelect.value);
        const params = new URLSearchParams({
            framework: selected.framework,
            subject: selected.subject,
            year_level: selected.year_level
        });

        const response = await fetch(`/api/dashboard/course-progress?${params.toString()}`);

        if (!response.ok) {
            return;
        }

        const data = await response.json();
        const course = data.course;

        const framework = document.getElementById("dashboardProgressFramework");
        const label = document.getElementById("dashboardProgressCourse");
        const fill = document.getElementById("dashboardProgressFill");
        const value = document.getElementById("dashboardProgressValue");
        const published = document.getElementById("dashboardPublishedCount");
        const remaining = document.getElementById("dashboardRemainingCount");

        if (framework) {
            framework.textContent = course.framework;
        }

        if (label) {
            label.textContent = course.label;
        }

        if (fill) {
            fill.style.width = `${course.progress}%`;
        }

        if (value) {
            value.textContent = `${course.progress}%`;
        }

        if (published) {
            published.textContent = course.published;
        }

        if (remaining) {
            remaining.textContent = course.remaining;
        }
    }

    courseSelect.addEventListener("change", loadSelectedCourseProgress);

    loadDashboardCourses();
})();
