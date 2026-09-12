/*
 * PrivEsc Explorer
 * ----------------
 * Interactive Windows and Linux privilege escalation reference.
 *
 * Expected pages:
 *   /privesc/windows/
 *   /privesc/linux/
 *
 * Expected data:
 *   /data/privesc/windows.json
 *   /data/privesc/linux.json
 *
 * Supported proof object:
 * {
 *   mode: "controlled" | "validation-only" | "lab",
 *   objective: "...",
 *   steps: [],
 *   expected: [],
 *   cleanup: [],
 *   safety: "..."
 * }
 */

(() => {
    "use strict";

    const EXPLORER_ID = "privesc-explorer";

    const SEVERITY_ORDER = {
        critical: 5,
        high: 4,
        medium: 3,
        low: 2,
        informational: 1
    };

    const state = {
        platform: null,
        data: null,
        techniques: [],
        query: "",
        category: "all",
        severity: "all",
        sort: "name"
    };

    let explorer = null;
    let searchInput = null;
    let categoryFilter = null;
    let severityFilter = null;
    let resetButton = null;
    let sortSelect = null;
    let resultsContainer = null;
    let resultCount = null;
    let emptyState = null;
    let activeFilters = null;

    /*
     * -------------------------------------------------------------------------
     * Initialisation
     * -------------------------------------------------------------------------
     */

    async function initialisePrivEscExplorer() {
        explorer = document.getElementById(EXPLORER_ID);

        if (!explorer) {
            return;
        }

        state.platform = normalisePlatform(explorer.dataset.platform);

        /*
         * /privesc/ is the cross-platform landing page.
         * It deliberately has no data-platform value and should not attempt
         * to load either JSON database.
         */
        if (!state.platform) {
            return;
        }

        cacheElements();

        if (!requiredElementsExist()) {
            console.error(
                "[PrivEsc Explorer] Required explorer elements are missing."
            );
            return;
        }

        bindEvents();
        setLoadingState();

        try {
            const data = await loadTechniqueData(state.platform);

            validateData(data);

            state.data = data;
            state.techniques = Array.isArray(data.techniques)
                ? data.techniques
                : [];

            populateCategoryFilter();
            restoreStateFromUrl();
            addExplorerActions();
            render();
        } catch (error) {
            console.error("[PrivEsc Explorer]", error);

            renderFatalError(
                "The privilege escalation technique database could not be loaded."
            );
        }
    }

    function cacheElements() {
        searchInput = document.getElementById("privesc-search");
        categoryFilter = document.getElementById("privesc-category");
        severityFilter = document.getElementById("privesc-severity");
        resetButton = document.getElementById("privesc-reset");
        sortSelect = document.getElementById("privesc-sort");
        resultsContainer = document.getElementById("privesc-results");
        resultCount = document.getElementById("privesc-result-count");
        emptyState = document.getElementById("privesc-empty");
        activeFilters = document.getElementById("privesc-active-filters");
    }

    function requiredElementsExist() {
        return Boolean(
            searchInput &&
            categoryFilter &&
            severityFilter &&
            resetButton &&
            sortSelect &&
            resultsContainer &&
            resultCount &&
            emptyState &&
            activeFilters
        );
    }

    function normalisePlatform(platform) {
        if (!platform) {
            return null;
        }

        const value = String(platform).trim().toLowerCase();

        if (value === "windows" || value === "linux") {
            return value;
        }

        return null;
    }

    /*
     * -------------------------------------------------------------------------
     * Data Loading
     * -------------------------------------------------------------------------
     */

    async function loadTechniqueData(platform) {
        const dataUrl = resolveDataUrl(platform);

        const response = await fetch(dataUrl, {
            method: "GET",
            headers: {
                Accept: "application/json"
            },
            cache: "no-cache"
        });

        if (!response.ok) {
            throw new Error(
                `Unable to load ${dataUrl}: HTTP ${response.status}`
            );
        }

        return response.json();
    }

    function resolveDataUrl(platform) {
        return new URL(
            `../../data/privesc/${platform}.json`,
            document.baseURI
        ).href;
    }

    function validateData(data) {
        if (!data || typeof data !== "object") {
            throw new Error("Technique data is not a JSON object.");
        }

        if (!Array.isArray(data.techniques)) {
            throw new Error(
                "Technique database does not contain a techniques array."
            );
        }

        if (
            data.platform &&
            normalisePlatform(data.platform) !== state.platform
        ) {
            throw new Error(
                `Technique database platform does not match ${state.platform}.`
            );
        }
    }

    /*
     * -------------------------------------------------------------------------
     * Event Handling
     * -------------------------------------------------------------------------
     */

    function bindEvents() {
        searchInput.addEventListener(
            "input",
            debounce(() => {
                state.query = searchInput.value.trim();
                render();
            }, 100)
        );

        categoryFilter.addEventListener("change", () => {
            state.category = categoryFilter.value;
            render();
        });

        severityFilter.addEventListener("change", () => {
            state.severity = severityFilter.value;
            render();
        });

        sortSelect.addEventListener("change", () => {
            state.sort = sortSelect.value;
            render();
        });

        resetButton.addEventListener("click", resetFilters);

        resultsContainer.addEventListener(
            "click",
            handleResultsClick
        );

        resultsContainer.addEventListener(
            "keydown",
            handleResultsKeydown
        );
    }

    function handleResultsClick(event) {
        const copyButton = event.target.closest(
            "[data-copy-command]"
        );

        if (copyButton) {
            copyCommand(copyButton);
            return;
        }

        const toggle = event.target.closest(
            "[data-technique-toggle]"
        );

        if (toggle) {
            toggleTechnique(toggle);
        }
    }

    function handleResultsKeydown(event) {
        if (
            event.key !== "Enter" &&
            event.key !== " "
        ) {
            return;
        }

        const toggle = event.target.closest(
            "[data-technique-toggle]"
        );

        if (!toggle) {
            return;
        }

        event.preventDefault();
        toggleTechnique(toggle);
    }

    /*
     * -------------------------------------------------------------------------
     * Filtering and Searching
     * -------------------------------------------------------------------------
     */

    function getFilteredTechniques() {
        const queryTokens = tokenise(state.query);

        const filtered = state.techniques.filter(
            (technique) => {
                if (!matchesPlatform(technique)) {
                    return false;
                }

                if (!matchesCategory(technique)) {
                    return false;
                }

                if (!matchesSeverity(technique)) {
                    return false;
                }

                if (!matchesSearch(technique, queryTokens)) {
                    return false;
                }

                return true;
            }
        );

        return sortTechniques(filtered);
    }

    function matchesPlatform(technique) {
        if (!technique.platform) {
            return true;
        }

        return (
            String(technique.platform).toLowerCase() ===
            state.platform
        );
    }

    function matchesCategory(technique) {
        if (state.category === "all") {
            return true;
        }

        return (
            String(technique.category || "").toLowerCase() ===
            state.category.toLowerCase()
        );
    }

    function matchesSeverity(technique) {
        if (state.severity === "all") {
            return true;
        }

        return (
            String(technique.severity || "").toLowerCase() ===
            state.severity.toLowerCase()
        );
    }

    function matchesSearch(technique, tokens) {
        if (tokens.length === 0) {
            return true;
        }

        const haystack = buildSearchText(technique);

        return tokens.every(
            (token) => haystack.includes(token)
        );
    }

    function tokenise(value) {
        if (!value) {
            return [];
        }

        return value
            .toLowerCase()
            .split(/\s+/)
            .map((token) => token.trim())
            .filter(Boolean);
    }

    function buildSearchText(technique) {
        const proof = technique.proof || {};

        const mitreText = (technique.mitre || [])
            .map((entry) => {
                if (typeof entry === "string") {
                    return entry;
                }

                return [
                    entry.id,
                    entry.name,
                    entry.url
                ].filter(Boolean).join(" ");
            });

        const values = [
            technique.id,
            technique.name,
            technique.platform,
            technique.category,
            technique.severity,
            technique.confidence,
            technique.summary,

            ...(technique.tags || []),
            ...(technique.found || []),
            ...(technique.requires || []),
            ...(technique.commands || []),
            ...(technique.validation || []),
            ...(technique.detection || []),
            ...(technique.remediation || []),
            ...(technique.related || []),

            proof.mode,
            proof.objective,
            ...(proof.steps || []),
            ...(proof.expected || []),
            ...(proof.cleanup || []),
            proof.safety,

            ...mitreText
        ];

        return values
            .filter(Boolean)
            .join(" ")
            .toLowerCase();
    }

    /*
     * -------------------------------------------------------------------------
     * Sorting
     * -------------------------------------------------------------------------
     */

    function sortTechniques(techniques) {
        return [...techniques].sort((a, b) => {
            switch (state.sort) {
                case "severity":
                    return sortBySeverity(a, b);

                case "category":
                    return sortByCategory(a, b);

                case "name":
                default:
                    return sortByName(a, b);
            }
        });
    }

    function sortByName(a, b) {
        return String(a.name || "").localeCompare(
            String(b.name || ""),
            undefined,
            {
                sensitivity: "base"
            }
        );
    }

    function sortByCategory(a, b) {
        const categoryCompare =
            String(a.category || "").localeCompare(
                String(b.category || ""),
                undefined,
                {
                    sensitivity: "base"
                }
            );

        if (categoryCompare !== 0) {
            return categoryCompare;
        }

        return sortByName(a, b);
    }

    function sortBySeverity(a, b) {
        const aValue =
            SEVERITY_ORDER[
                String(a.severity || "").toLowerCase()
            ] || 0;

        const bValue =
            SEVERITY_ORDER[
                String(b.severity || "").toLowerCase()
            ] || 0;

        if (aValue !== bValue) {
            return bValue - aValue;
        }

        return sortByName(a, b);
    }

    /*
     * -------------------------------------------------------------------------
     * Category Filter
     * -------------------------------------------------------------------------
     */

    function populateCategoryFilter() {
        const categories = [
            ...new Set(
                state.techniques
                    .map((technique) =>
                        String(
                            technique.category || ""
                        ).trim()
                    )
                    .filter(Boolean)
            )
        ].sort((a, b) =>
            a.localeCompare(
                b,
                undefined,
                {
                    sensitivity: "base"
                }
            )
        );

        categoryFilter.innerHTML =
            '<option value="all">All categories</option>';

        categories.forEach((category) => {
            const option =
                document.createElement("option");

            option.value = category;
            option.textContent = category;

            categoryFilter.appendChild(option);
        });
    }

    /*
     * -------------------------------------------------------------------------
     * Rendering
     * -------------------------------------------------------------------------
     */

    function render() {
        const techniques = getFilteredTechniques();

        renderResultCount(techniques.length);
        renderActiveFilters();
        renderTechniques(techniques);
        updateUrlState();
    }

    function renderResultCount(count) {
        const total = state.techniques.length;

        if (count === total) {
            resultCount.textContent =
                `${count} ${pluralise(
                    count,
                    "technique",
                    "techniques"
                )}`;
            return;
        }

        resultCount.textContent =
            `${count} of ${total} techniques`;
    }

    function renderActiveFilters() {
        const filters = [];

        if (state.query) {
            filters.push({
                label: `Search: ${state.query}`,
                type: "query"
            });
        }

        if (state.category !== "all") {
            filters.push({
                label: `Category: ${state.category}`,
                type: "category"
            });
        }

        if (state.severity !== "all") {
            filters.push({
                label: `Severity: ${capitalise(
                    state.severity
                )}`,
                type: "severity"
            });
        }

        if (filters.length === 0) {
            activeFilters.innerHTML = "";
            activeFilters.hidden = true;
            return;
        }

        activeFilters.hidden = false;

        activeFilters.innerHTML = filters
            .map(
                (filter) => `
                    <button
                        type="button"
                        class="privesc-active-filter"
                        data-remove-filter="${escapeAttribute(
                            filter.type
                        )}"
                    >
                        ${escapeHtml(filter.label)}
                        <span aria-hidden="true">×</span>
                    </button>
                `
            )
            .join("");

        activeFilters
            .querySelectorAll("[data-remove-filter]")
            .forEach((button) => {
                button.addEventListener(
                    "click",
                    () => {
                        removeFilter(
                            button.dataset.removeFilter
                        );
                    }
                );
            });
    }

    function renderTechniques(techniques) {
        if (techniques.length === 0) {
            resultsContainer.innerHTML = "";
            emptyState.hidden = false;
            return;
        }

        emptyState.hidden = true;

        resultsContainer.innerHTML = techniques
            .map(renderTechniqueCard)
            .join("");
    }

    function renderTechniqueCard(technique) {
        const id =
            safeId(technique.id || technique.name);

        const detailsId =
            `privesc-details-${id}`;

        const severity =
            String(
                technique.severity || "informational"
            ).toLowerCase();

        const confidence =
            String(
                technique.confidence || "candidate"
            ).toLowerCase();

        const proofMode =
            normaliseProofMode(
                technique.proof?.mode
            );

        return `
            <article
                class="privesc-card"
                data-technique-id="${escapeAttribute(
                    technique.id || ""
                )}"
            >
                <div
                    class="privesc-card-summary"
                    role="button"
                    tabindex="0"
                    aria-expanded="false"
                    aria-controls="${escapeAttribute(
                        detailsId
                    )}"
                    data-technique-toggle
                >
                    <div class="privesc-card-heading">
                        <div class="privesc-card-title-row">
                            <h3 class="privesc-card-title">
                                ${escapeHtml(
                                    technique.name ||
                                    "Unnamed technique"
                                )}
                            </h3>

                            <span
                                class="privesc-toggle-icon"
                                aria-hidden="true"
                            >
                                +
                            </span>
                        </div>

                        <div class="privesc-card-badges">
                            ${renderSeverityBadge(
                                severity
                            )}

                            ${renderConfidenceBadge(
                                confidence
                            )}

                            ${renderCategoryBadge(
                                technique.category
                            )}

                            ${renderProofBadge(
                                proofMode
                            )}
                        </div>
                    </div>

                    ${
                        technique.summary
                            ? `
                                <p class="privesc-card-description">
                                    ${escapeHtml(
                                        technique.summary
                                    )}
                                </p>
                            `
                            : ""
                    }
                </div>

                <div
                    id="${escapeAttribute(detailsId)}"
                    class="privesc-card-details"
                    hidden
                >
                    ${renderTechniqueDetails(
                        technique
                    )}
                </div>
            </article>
        `;
    }

    function renderTechniqueDetails(technique) {
        return `
            ${renderListSection(
                "What You Found",
                technique.found,
                "privesc-found"
            )}

            ${renderListSection(
                "Preconditions",
                technique.requires,
                "privesc-requires"
            )}

            ${renderCommandsSection(
                technique.commands
            )}

            ${renderListSection(
                "Validation",
                technique.validation,
                "privesc-validation"
            )}

            ${renderProofSection(
                technique.proof
            )}

            ${renderListSection(
                "Detection",
                technique.detection,
                "privesc-detection"
            )}

            ${renderListSection(
                "Remediation",
                technique.remediation,
                "privesc-remediation"
            )}

            ${renderMitreSection(
                technique.mitre
            )}

            ${renderTagsSection(
                technique.tags
            )}

            ${renderRelatedSection(
                technique.related
            )}
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Badges
     * -------------------------------------------------------------------------
     */

    function renderSeverityBadge(severity) {
        return `
            <span
                class="
                    privesc-badge
                    privesc-severity
                    privesc-severity-${escapeAttribute(
                        severity
                    )}
                "
            >
                ${escapeHtml(
                    capitalise(severity)
                )}
            </span>
        `;
    }

    function renderConfidenceBadge(confidence) {
        return `
            <span
                class="
                    privesc-badge
                    privesc-confidence
                    privesc-confidence-${escapeAttribute(
                        confidence
                    )}
                "
            >
                ${escapeHtml(
                    capitalise(confidence)
                )}
            </span>
        `;
    }

    function renderCategoryBadge(category) {
        if (!category) {
            return "";
        }

        return `
            <span
                class="
                    privesc-badge
                    privesc-category-badge
                "
            >
                ${escapeHtml(category)}
            </span>
        `;
    }

    function renderProofBadge(mode) {
        if (!mode) {
            return "";
        }

        return `
            <span
                class="
                    privesc-badge
                    privesc-proof-badge
                    privesc-proof-badge-${escapeAttribute(
                        mode
                    )}
                "
            >
                ${escapeHtml(
                    proofModeLabel(mode)
                )}
            </span>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Generic Detail Sections
     * -------------------------------------------------------------------------
     */

    function renderListSection(
        title,
        items,
        className = ""
    ) {
        if (
            !Array.isArray(items) ||
            items.length === 0
        ) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    ${escapeAttribute(className)}
                "
            >
                <h4>${escapeHtml(title)}</h4>

                <ul>
                    ${items
                        .map(
                            (item) => `
                                <li>
                                    ${escapeHtml(item)}
                                </li>
                            `
                        )
                        .join("")}
                </ul>
            </section>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Commands / Enumeration
     * -------------------------------------------------------------------------
     */

    function renderCommandsSection(commands) {
        if (
            !Array.isArray(commands) ||
            commands.length === 0
        ) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    privesc-commands
                "
            >
                <h4>Enumeration</h4>

                <div class="privesc-command-list">
                    ${commands
                        .map(renderCommand)
                        .join("")}
                </div>
            </section>
        `;
    }

    function renderCommand(command) {
        return `
            <div class="privesc-command">
                <pre><code>${escapeHtml(
                    command
                )}</code></pre>

                <button
                    type="button"
                    class="privesc-copy-button"
                    data-copy-command="${escapeAttribute(
                        command
                    )}"
                    aria-label="Copy command"
                >
                    Copy
                </button>
            </div>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Proof
     * -------------------------------------------------------------------------
     */

    function renderProofSection(proof) {
        if (
            !proof ||
            typeof proof !== "object"
        ) {
            return "";
        }

        const mode =
            normaliseProofMode(proof.mode) ||
            "controlled";

        const hasContent = Boolean(
            proof.objective ||
            (
                Array.isArray(proof.steps) &&
                proof.steps.length
            ) ||
            (
                Array.isArray(proof.expected) &&
                proof.expected.length
            ) ||
            (
                Array.isArray(proof.cleanup) &&
                proof.cleanup.length
            ) ||
            proof.safety
        );

        if (!hasContent) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    privesc-proof
                    privesc-proof-${escapeAttribute(
                        mode
                    )}
                "
            >
                <div class="privesc-proof-header">
                    <h4>Proof</h4>

                    <span
                        class="
                            privesc-proof-mode
                            privesc-proof-mode-${escapeAttribute(
                                mode
                            )}
                        "
                    >
                        ${escapeHtml(
                            proofModeLabel(mode)
                        )}
                    </span>
                </div>

                ${
                    proof.objective
                        ? `
                            <div class="privesc-proof-objective">
                                <strong>Objective</strong>

                                <p>
                                    ${escapeHtml(
                                        proof.objective
                                    )}
                                </p>
                            </div>
                        `
                        : ""
                }

                ${renderProofList(
                    "Proof Steps",
                    proof.steps,
                    "privesc-proof-steps"
                )}

                ${renderProofList(
                    "Expected Evidence",
                    proof.expected,
                    "privesc-proof-expected"
                )}

                ${renderProofList(
                    "Cleanup",
                    proof.cleanup,
                    "privesc-proof-cleanup"
                )}

                ${
                    proof.safety
                        ? `
                            <div
                                class="
                                    privesc-proof-safety
                                    privesc-proof-safety-${escapeAttribute(
                                        mode
                                    )}
                                "
                            >
                                <strong>
                                    Safety
                                </strong>

                                <p>
                                    ${escapeHtml(
                                        proof.safety
                                    )}
                                </p>
                            </div>
                        `
                        : ""
                }
            </section>
        `;
    }

    function renderProofList(
        title,
        items,
        className
    ) {
        if (
            !Array.isArray(items) ||
            items.length === 0
        ) {
            return "";
        }

        return `
            <div
                class="
                    privesc-proof-block
                    ${escapeAttribute(className)}
                "
            >
                <strong>
                    ${escapeHtml(title)}
                </strong>

                <ol>
                    ${items
                        .map(
                            (item) => `
                                <li>
                                    ${escapeHtml(item)}
                                </li>
                            `
                        )
                        .join("")}
                </ol>
            </div>
        `;
    }

    function normaliseProofMode(mode) {
        if (!mode) {
            return null;
        }

        const value =
            String(mode)
                .trim()
                .toLowerCase();

        if (
            value === "controlled" ||
            value === "validation-only" ||
            value === "lab"
        ) {
            return value;
        }

        return "controlled";
    }

    function proofModeLabel(mode) {
        switch (mode) {
            case "validation-only":
                return "VALIDATION ONLY";

            case "lab":
                return "LAB ONLY";

            case "controlled":
            default:
                return "CONTROLLED PROOF";
        }
    }

    /*
     * -------------------------------------------------------------------------
     * MITRE ATT&CK
     * -------------------------------------------------------------------------
     */

    function renderMitreSection(entries) {
        if (
            !Array.isArray(entries) ||
            entries.length === 0
        ) {
            return "";
        }

        const rendered = entries
            .map(renderMitreEntry)
            .filter(Boolean)
            .join("");

        if (!rendered) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    privesc-mitre
                "
            >
                <h4>MITRE ATT&amp;CK</h4>

                <div class="privesc-mitre-list">
                    ${rendered}
                </div>
            </section>
        `;
    }

    function renderMitreEntry(entry) {
        if (!entry) {
            return "";
        }

        if (typeof entry === "string") {
            return `
                <div class="privesc-mitre-entry">
                    ${escapeHtml(entry)}
                </div>
            `;
        }

        const id = entry.id || "";
        const name = entry.name || "";
        const url = safeExternalUrl(entry.url);

        const label = [
            id,
            name
        ].filter(Boolean).join(" - ");

        if (!label) {
            return "";
        }

        if (!url) {
            return `
                <div class="privesc-mitre-entry">
                    ${escapeHtml(label)}
                </div>
            `;
        }

        return `
            <div class="privesc-mitre-entry">
                <a
                    href="${escapeAttribute(url)}"
                    target="_blank"
                    rel="noopener noreferrer"
                >
                    ${escapeHtml(label)}
                </a>
            </div>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Tags
     * -------------------------------------------------------------------------
     */

    function renderTagsSection(tags) {
        if (
            !Array.isArray(tags) ||
            tags.length === 0
        ) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    privesc-tags
                "
            >
                <h4>Tags</h4>

                <div class="privesc-tag-list">
                    ${tags
                        .map(
                            (tag) => `
                                <button
                                    type="button"
                                    class="privesc-tag"
                                    data-search-tag="${escapeAttribute(
                                        tag
                                    )}"
                                >
                                    ${escapeHtml(tag)}
                                </button>
                            `
                        )
                        .join("")}
                </div>
            </section>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Related Notes
     * -------------------------------------------------------------------------
     */

    function renderRelatedSection(related) {
        if (
            !Array.isArray(related) ||
            related.length === 0
        ) {
            return "";
        }

        const links = related
            .map(renderRelatedLink)
            .filter(Boolean)
            .join("");

        if (!links) {
            return "";
        }

        return `
            <section
                class="
                    privesc-detail-section
                    privesc-related
                "
            >
                <h4>Related Notes</h4>

                <ul>
                    ${links}
                </ul>
            </section>
        `;
    }

    function renderRelatedLink(value) {
        if (!value) {
            return "";
        }

        const href = String(value).trim();

        if (!href) {
            return "";
        }

        const label = relatedLinkLabel(href);

        return `
            <li>
                <a href="${escapeAttribute(href)}">
                    ${escapeHtml(label)}
                </a>
            </li>
        `;
    }

    function relatedLinkLabel(href) {
        let value = href
            .split("#")[0]
            .replace(/\/+$/, "");

        value =
            value.split("/").pop() || "Related note";

        value = value.replace(/\.md$/i, "");

        if (
            value.toLowerCase() === "index" ||
            !value
        ) {
            return "Related note";
        }

        return value
            .replace(/[-_]+/g, " ")
            .replace(/\b\w/g, (character) =>
                character.toUpperCase()
            );
    }

    /*
     * -------------------------------------------------------------------------
     * Card Expansion
     * -------------------------------------------------------------------------
     */

    function toggleTechnique(toggle) {
        const card =
            toggle.closest(".privesc-card");

        if (!card) {
            return;
        }

        const details =
            card.querySelector(
                ".privesc-card-details"
            );

        if (!details) {
            return;
        }

        const expanded =
            toggle.getAttribute(
                "aria-expanded"
            ) === "true";

        const newState = !expanded;

        toggle.setAttribute(
            "aria-expanded",
            newState ? "true" : "false"
        );

        details.hidden = !newState;

        card.classList.toggle(
            "is-expanded",
            newState
        );

        const icon =
            toggle.querySelector(
                ".privesc-toggle-icon"
            );

        if (icon) {
            icon.textContent =
                newState ? "−" : "+";
        }
    }

    function setAllCardsExpanded(expanded) {
        resultsContainer
            .querySelectorAll(".privesc-card")
            .forEach((card) => {
                const toggle =
                    card.querySelector(
                        "[data-technique-toggle]"
                    );

                const details =
                    card.querySelector(
                        ".privesc-card-details"
                    );

                if (
                    !toggle ||
                    !details
                ) {
                    return;
                }

                toggle.setAttribute(
                    "aria-expanded",
                    expanded ? "true" : "false"
                );

                details.hidden = !expanded;

                card.classList.toggle(
                    "is-expanded",
                    expanded
                );

                const icon =
                    toggle.querySelector(
                        ".privesc-toggle-icon"
                    );

                if (icon) {
                    icon.textContent =
                        expanded ? "−" : "+";
                }
            });
    }

    /*
     * -------------------------------------------------------------------------
     * Bulk Actions
     * -------------------------------------------------------------------------
     */

    function addExplorerActions() {
        const header =
            document.querySelector(
                ".privesc-results-header"
            );

        if (
            !header ||
            header.querySelector(
                ".privesc-bulk-actions"
            )
        ) {
            return;
        }

        const actions =
            document.createElement("div");

        actions.className =
            "privesc-bulk-actions";

        actions.innerHTML = `
            <button
                type="button"
                class="privesc-action-button"
                data-expand-all
            >
                Expand all
            </button>

            <button
                type="button"
                class="privesc-action-button"
                data-collapse-all
            >
                Collapse all
            </button>
        `;

        /*
         * Do not assume that the sort select itself is a direct child
         * of the results header. Some page layouts wrap it in a label
         * or control container.
         */
        const sortWrapper =
            sortSelect.closest(
                ".privesc-sort, .privesc-sort-control, label"
            );

        if (
            sortWrapper &&
            sortWrapper.parentElement === header
        ) {
            header.insertBefore(
                actions,
                sortWrapper
            );
        } else {
            header.appendChild(actions);
        }

        actions.addEventListener(
            "click",
            (event) => {
                if (
                    event.target.closest(
                        "[data-expand-all]"
                    )
                ) {
                    setAllCardsExpanded(true);
                    return;
                }

                if (
                    event.target.closest(
                        "[data-collapse-all]"
                    )
                ) {
                    setAllCardsExpanded(false);
                }
            }
        );
    }

    /*
     * -------------------------------------------------------------------------
     * Filter Reset
     * -------------------------------------------------------------------------
     */

    function resetFilters() {
        state.query = "";
        state.category = "all";
        state.severity = "all";
        state.sort = "name";

        searchInput.value = "";
        categoryFilter.value = "all";
        severityFilter.value = "all";
        sortSelect.value = "name";

        render();
        searchInput.focus();
    }

    function removeFilter(type) {
        switch (type) {
            case "query":
                state.query = "";
                searchInput.value = "";
                break;

            case "category":
                state.category = "all";
                categoryFilter.value = "all";
                break;

            case "severity":
                state.severity = "all";
                severityFilter.value = "all";
                break;

            default:
                return;
        }

        render();
    }

    /*
     * -------------------------------------------------------------------------
     * Loading State
     * -------------------------------------------------------------------------
     */

    function setLoadingState() {
        resultCount.textContent =
            "Loading techniques...";

        resultsContainer.innerHTML = `
            <div class="privesc-loading">
                Loading PrivEsc Explorer...
            </div>
        `;

        emptyState.hidden = true;
    }

    /*
     * -------------------------------------------------------------------------
     * Clipboard
     * -------------------------------------------------------------------------
     */

    async function copyCommand(button) {
        const command =
            button.dataset.copyCommand;

        if (!command) {
            return;
        }

        const originalText =
            button.textContent;

        try {
            await writeClipboard(command);

            button.textContent = "Copied";
            button.classList.add("is-copied");

            window.setTimeout(() => {
                button.textContent =
                    originalText;

                button.classList.remove(
                    "is-copied"
                );
            }, 1500);
        } catch (error) {
            console.error(
                "[PrivEsc Explorer] Unable to copy command:",
                error
            );

            button.textContent =
                "Copy failed";

            window.setTimeout(() => {
                button.textContent =
                    originalText;
            }, 1500);
        }
    }

    async function writeClipboard(value) {
        if (
            navigator.clipboard &&
            window.isSecureContext
        ) {
            await navigator.clipboard.writeText(
                value
            );
            return;
        }

        const textarea =
            document.createElement(
                "textarea"
            );

        textarea.value = value;

        textarea.setAttribute(
            "readonly",
            ""
        );

        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        textarea.style.pointerEvents = "none";

        document.body.appendChild(textarea);

        textarea.select();

        textarea.setSelectionRange(
            0,
            textarea.value.length
        );

        const successful =
            document.execCommand("copy");

        textarea.remove();

        if (!successful) {
            throw new Error(
                "Legacy clipboard copy failed."
            );
        }
    }

    /*
     * -------------------------------------------------------------------------
     * Tag Searching
     * -------------------------------------------------------------------------
     */

    document.addEventListener(
        "click",
        (event) => {
            const tag =
                event.target.closest(
                    "[data-search-tag]"
                );

            if (
                !tag ||
                !explorer ||
                !explorer.contains(tag)
            ) {
                return;
            }

            const value =
                tag.dataset.searchTag;

            if (!value) {
                return;
            }

            state.query = value;
            searchInput.value = value;

            render();

            explorer.scrollIntoView({
                behavior:
                    prefersReducedMotion()
                        ? "auto"
                        : "smooth",
                block: "start"
            });

            searchInput.focus();
        }
    );

    /*
     * -------------------------------------------------------------------------
     * URL State
     * -------------------------------------------------------------------------
     */

    function restoreStateFromUrl() {
        const params =
            new URLSearchParams(
                window.location.search
            );

        state.query =
            params.get("q") || "";

        state.category =
            params.get("category") || "all";

        state.severity =
            params.get("severity") || "all";

        state.sort =
            params.get("sort") || "name";

        searchInput.value =
            state.query;

        if (
            [...categoryFilter.options].some(
                (option) =>
                    option.value ===
                    state.category
            )
        ) {
            categoryFilter.value =
                state.category;
        } else {
            state.category = "all";
            categoryFilter.value = "all";
        }

        if (
            [...severityFilter.options].some(
                (option) =>
                    option.value ===
                    state.severity
            )
        ) {
            severityFilter.value =
                state.severity;
        } else {
            state.severity = "all";
            severityFilter.value = "all";
        }

        if (
            [...sortSelect.options].some(
                (option) =>
                    option.value ===
                    state.sort
            )
        ) {
            sortSelect.value =
                state.sort;
        } else {
            state.sort = "name";
            sortSelect.value = "name";
        }
    }

    function updateUrlState() {
        if (!state.platform) {
            return;
        }

        const url =
            new URL(
                window.location.href
            );

        const values = {
            q: state.query,
            category:
                state.category === "all"
                    ? ""
                    : state.category,
            severity:
                state.severity === "all"
                    ? ""
                    : state.severity,
            sort:
                state.sort === "name"
                    ? ""
                    : state.sort
        };

        Object.entries(values).forEach(
            ([key, value]) => {
                if (value) {
                    url.searchParams.set(
                        key,
                        value
                    );
                } else {
                    url.searchParams.delete(
                        key
                    );
                }
            }
        );

        window.history.replaceState(
            {},
            "",
            `${url.pathname}${url.search}${url.hash}`
        );
    }

    /*
     * -------------------------------------------------------------------------
     * Error Rendering
     * -------------------------------------------------------------------------
     */

    function renderFatalError(message) {
        if (!explorer) {
            return;
        }

        const safeMessage =
            escapeHtml(message);

        if (resultCount) {
            resultCount.textContent =
                "Explorer unavailable";
        }

        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div
                    class="privesc-error"
                    role="alert"
                >
                    <strong>
                        Unable to load PrivEsc Explorer
                    </strong>

                    <p>
                        ${safeMessage}
                    </p>
                </div>
            `;
            return;
        }

        explorer.innerHTML = `
            <div
                class="privesc-error"
                role="alert"
            >
                <strong>
                    Unable to load PrivEsc Explorer
                </strong>

                <p>
                    ${safeMessage}
                </p>
            </div>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Utilities
     * -------------------------------------------------------------------------
     */

    function debounce(
        callback,
        delay = 100
    ) {
        let timeoutId = null;

        return (...args) => {
            window.clearTimeout(
                timeoutId
            );

            timeoutId =
                window.setTimeout(
                    () => {
                        callback(...args);
                    },
                    delay
                );
        };
    }

    function pluralise(
        count,
        singular,
        plural
    ) {
        return count === 1
            ? singular
            : plural;
    }

    function capitalise(value) {
        const stringValue =
            String(value || "");

        if (!stringValue) {
            return "";
        }

        return (
            stringValue
                .charAt(0)
                .toUpperCase() +
            stringValue.slice(1)
        );
    }

    function safeId(value) {
        return String(value || "")
            .trim()
            .toLowerCase()
            .replace(
                /[^a-z0-9_-]+/g,
                "-"
            )
            .replace(
                /^-+|-+$/g,
                ""
            );
    }

    function safeExternalUrl(value) {
        if (!value) {
            return null;
        }

        try {
            const url =
                new URL(
                    value,
                    document.baseURI
                );

            if (
                url.protocol !== "https:" &&
                url.protocol !== "http:"
            ) {
                return null;
            }

            return url.href;
        } catch {
            return null;
        }
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function escapeAttribute(value) {
        return escapeHtml(value)
            .replace(/`/g, "&#096;");
    }

    function prefersReducedMotion() {
        return Boolean(
            window.matchMedia &&
            window.matchMedia(
                "(prefers-reduced-motion: reduce)"
            ).matches
        );
    }

    /*
     * -------------------------------------------------------------------------
     * MkDocs Material Compatibility
     * -------------------------------------------------------------------------
     *
     * Material's navigation.instant feature replaces page content without
     * performing a normal browser reload. document$ is therefore preferred
     * when available.
     */

    function start() {
        initialisePrivEscExplorer();
    }

    if (
        typeof document$ !== "undefined" &&
        document$?.subscribe
    ) {
        document$.subscribe(() => {
            start();
        });
    } else if (
        document.readyState === "loading"
    ) {
        document.addEventListener(
            "DOMContentLoaded",
            start,
            {
                once: true
            }
        );
    } else {
        start();
    }
})();
