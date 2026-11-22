/* Curriculum Studio bridge + whole-scope basket */
"use strict";

window.processingScopes = [];
window.processingBasket = [];

document.addEventListener("DOMContentLoaded", async function () {
    console.log("Curriculum Studio Started");
    try {
        await window.initialiseSelection();
        console.log("Curriculum Studio Selection Ready");
    } catch (error) {
        console.error("Curriculum Studio initialisation failed", error);
    }
});

function studioValue(id) {
    const node = document.getElementById(id);
    return node ? String(node.value || "").trim() : "";
}

function scopeLabel(level) {
    const labels = {
        year_level: "Year Level",
        strand: "Strand",
        sub_strand: "Sub-strand",
        topic: "Curriculum Topic"
    };
    return labels[level] || level;
}

function scopeParams(level) {
    const params = new URLSearchParams({
        learning_area: studioValue("learning_area"),
        subject: studioValue("subject")
    });

    if (["year_level", "strand", "sub_strand", "topic"].includes(level)) {
        params.set("year_level", studioValue("year_level"));
    }
    if (["strand", "sub_strand", "topic"].includes(level)) {
        params.set("strand", studioValue("strand"));
    }
    if (["sub_strand", "topic"].includes(level)) {
        params.set("sub_strand", studioValue("sub_strand"));
    }
    if (level === "topic") {
        params.set("parent_code", studioValue("topic"));
    }

    return params;
}

function rebuildProcessingBasket() {
    const unique = new Map();

    window.processingScopes.forEach(function (scope) {
        scope.items.forEach(function (lesson) {
            unique.set(String(lesson.curriculum_code), lesson);
        });
    });

    window.processingBasket = Array.from(unique.values());
    window.selectedCurriculumLessons = window.processingBasket.slice();
    renderProcessingBasket();
}

function renderProcessingBasket() {
    const box = document.getElementById("basketItems");
    const total = document.getElementById("basketTotal");

    if (!box || !total) return;

    box.replaceChildren();

    if (!window.processingScopes.length) {
        box.textContent = "No curriculum scopes added yet.";
    } else {
        window.processingScopes.forEach(function (scope) {
            const row = document.createElement("div");
            row.className = "processing-basket-item";

            const text = document.createElement("span");
            text.textContent = scope.label + " · " + scope.items.length +
                " eligible lesson(s)" +
                (scope.skipped
                    ? " · " + scope.skipped + " already built/generated skipped"
                    : "");

            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "btn btn-sm btn-outline-secondary";
            remove.textContent = "Remove";
            remove.addEventListener("click", function () {
                window.processingScopes = window.processingScopes.filter(
                    function (entry) { return entry.id !== scope.id; }
                );
                rebuildProcessingBasket();
            });

            row.append(text, remove);
            box.appendChild(row);
        });
    }

    total.textContent = String(window.processingBasket.length);

    const set = function (id, value) {
        const node = document.getElementById(id);
        if (node) node.textContent = value;
    };
    set("summaryLessons", window.processingBasket.length);
    set("summaryNew", window.processingBasket.length);
    set("summaryRebuild", 0);
}

document.addEventListener("click", async function (event) {
    const button = event.target.closest(".bulk-action");
    if (!button) return;

    const mode = document.querySelector(
        'input[name="processing_mode"]:checked'
    )?.value || "IMMEDIATE";

    if (mode !== "QUEUE_STANDARD" && mode !== "QUEUE_BATCH") {
        alert("Whole-level processing requires Queue Processing or Batch Processing.");
        return;
    }

    const level = button.dataset.scope;
    if (!["year_level", "strand", "sub_strand", "topic"].includes(level)) {
        return;
    }

    const params = scopeParams(level);
    const required = ["learning_area", "subject", "year_level"];
    if (level === "strand") required.push("strand");
    if (level === "sub_strand") required.push("strand", "sub_strand");
    if (level === "topic") required.push("strand", "sub_strand", "parent_code");

    const missing = required.find(function (key) { return !params.get(key); });
    if (missing) {
        alert("Complete the curriculum selection before processing this scope.");
        return;
    }

    button.disabled = true;
    const original = button.textContent;
    button.textContent = "Loading lessons…";

    try {
        const result = await apiGet("/scope-items?" + params.toString());
        const items = Array.isArray(result.items) ? result.items : [];

        if (!items.length) {
            alert(
                "This scope has no lessons available for a new build. " +
                "Published or generated lessons must use Update / Rebuild or Publish."
            );
            return;
        }

        const id = level + "|" + params.toString();
        const selectedName = level === "topic"
            ? studioValue("topic")
            : studioValue(level);

        const entry = {
            id: id,
            label: scopeLabel(level) + ": " + selectedName,
            items: items,
            skipped: Number(result.published || 0) + Number(result.generated || 0)
        };

        const existing = window.processingScopes.findIndex(
            function (scope) { return scope.id === id; }
        );

        if (existing >= 0) {
            window.processingScopes[existing] = entry;
        } else {
            window.processingScopes.push(entry);
        }

        rebuildProcessingBasket();
    } catch (error) {
        console.error("Whole-scope selection failed", error);
        alert("Unable to load the whole curriculum scope: " + error.message);
    } finally {
        button.disabled = false;
        button.textContent = original;
    }
});
