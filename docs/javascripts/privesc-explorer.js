/*
 * PrivEsc Explorer
 * ----------------
 * Interactive Windows and Linux privilege escalation reference for
 * Asif's Security Notes.
 *
 * Expected pages:
 *   /privesc/windows/
 *   /privesc/linux/
 *
 * Expected data:
 *   /data/privesc/windows.json
 *   /data/privesc/linux.json
 *
 * The same JavaScript engine is used for both platforms.
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

        if (!state.platform) {
            renderFatalError(
                "PrivEsc Explorer could not determine the requested platform."
            );
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
        /*
         * MkDocs pages can be hosted:
         *
         *   /
         *
         * or under a project path:
         *
         *   /security-notes/
         *
         * The explorer page is expected at:
         *
         *   .../privesc/windows/
         *   .../privesc/linux/
         *
         * We resolve the data relative to the current document rather than
         * assuming that the site is always hosted at the domain root.
         */

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
     * Events
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

        resultsContainer.addEventListener("click", handleResultsClick);

        resultsContainer.addEventListener("keydown", handleResultsKeydown);
    }

    function handleResultsClick(event) {
        const copyButton = event.target.closest("[data-copy-command]");

        if (copyButton) {
            copyCommand(copyButton);
            return;
        }

        const toggle = event.target.closest("[data-technique-toggle]");

        if (toggle) {
            toggleTechnique(toggle);
        }
    }

    function handleResultsKeydown(event) {
        if (event.key !== "Enter" && event.key !== " ") {
            return;
        }

        const toggle = event.target.closest("[data-technique-toggle]");

        if (!toggle) {
            return;
        }

        event.preventDefault();
        toggleTechnique(toggle);
    }

    /*
     * -------------------------------------------------------------------------
     * Filtering
     * -------------------------------------------------------------------------
     */

    function getFilteredTechniques() {
        const queryTokens = tokenise(state.query);

        const filtered = state.techniques.filter((technique) => {
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
        });

        return sortTechniques(filtered);
    }

    function matchesPlatform(technique) {
        if (!technique.platform) {
            return true;
        }

        return (
            String(technique.platform).toLowerCase() === state.platform
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

        return tokens.every((token) => haystack.includes(token));
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
            ...(technique.remediation || [])
        ];

        if (Array.isArray(technique.mitre)) {
            technique.mitre.forEach((entry) => {
                if (typeof entry === "string") {
                    values.push(entry);
                    return;
                }

                if (entry && typeof entry === "object") {
                    values.push(entry.id);
                    values.push(entry.name);
                }
            });
        }

        return values
            .filter((value) => value !== null && value !== undefined)
            .join(" ")
            .toLowerCase();
    }

    /*
     * -------------------------------------------------------------------------
     * Sorting
     * -------------------------------------------------------------------------
     */

    function sortTechniques(techniques) {
        const copy = [...techniques];

        switch (state.sort) {
            case "severity":
                copy.sort((a, b) => {
                    const severityDifference =
                        severityScore(b.severity) -
                        severityScore(a.severity);

                    if (severityDifference !== 0) {
                        return severityDifference;
                    }

                    return compareNames(a, b);
                });
                break;

            case "category":
                copy.sort((a, b) => {
                    const categoryA = String(a.category || "");
                    const categoryB = String(b.category || "");

                    const categoryDifference = categoryA.localeCompare(
                        categoryB,
                        undefined,
                        { sensitivity: "base" }
                    );

                    if (categoryDifference !== 0) {
                        return categoryDifference;
                    }

                    return compareNames(a, b);
                });
                break;

            case "name":
            default:
                copy.sort(compareNames);
                break;
        }

        return copy;
    }

    function compareNames(a, b) {
        return String(a.name || "").localeCompare(
            String(b.name || ""),
            undefined,
            { sensitivity: "base" }
        );
    }

    function severityScore(severity) {
        return (
            SEVERITY_ORDER[
                String(severity || "").toLowerCase()
            ] || 0
        );
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
                    .map((technique) => technique.category)
                    .filter(Boolean)
            )
        ].sort((a, b) =>
            String(a).localeCompare(String(b), undefined, {
                sensitivity: "base"
            })
        );

        categoryFilter.innerHTML = "";

        const allOption = document.createElement("option");
        allOption.value = "all";
        allOption.textContent = "All categories";
        categoryFilter.appendChild(allOption);

        categories.forEach((category) => {
            const option = document.createElement("option");

            option.value = category;
            option.textContent = category;

            categoryFilter.appendChild(option);
        });

        categoryFilter.value = state.category;
    }

    /*
     * -------------------------------------------------------------------------
     * Main Rendering
     * -------------------------------------------------------------------------
     */

    function render() {
        const techniques = getFilteredTechniques();

        renderResultCount(techniques.length);
        renderActiveFilters();
        renderTechniqueCards(techniques);
        renderEmptyState(techniques.length === 0);
    }

    function setLoadingState() {
        resultCount.textContent = "Loading techniques...";

        resultsContainer.innerHTML = `
            <div class="privesc-loading" role="status">
                <span class="privesc-loading-indicator"></span>
                <span>Loading ${escapeHtml(state.platform)} techniques...</span>
            </div>
        `;
    }

    function renderResultCount(count) {
        const total = state.techniques.length;

        if (count === total) {
            resultCount.textContent =
                `${total} ${pluralise(total, "technique", "techniques")}`;
            return;
        }

        resultCount.textContent =
            `${count} of ${total} ${pluralise(total, "technique", "techniques")}`;
    }

    function renderTechniqueCards(techniques) {
        if (techniques.length === 0) {
            resultsContainer.innerHTML = "";
            return;
        }

        const fragment = document.createDocumentFragment();

        techniques.forEach((technique) => {
            fragment.appendChild(createTechniqueCard(technique));
        });

        resultsContainer.replaceChildren(fragment);
    }

    function renderEmptyState(isEmpty) {
        emptyState.hidden = !isEmpty;
    }

    /*
     * -------------------------------------------------------------------------
     * Active Filters
     * -------------------------------------------------------------------------
     */

    function renderActiveFilters() {
        activeFilters.innerHTML = "";

        const filters = [];

        if (state.query) {
            filters.push({
                type: "query",
                label: `Search: ${state.query}`
            });
        }

        if (state.category !== "all") {
            filters.push({
                type: "category",
                label: state.category
            });
        }

        if (state.severity !== "all") {
            filters.push({
                type: "severity",
                label: capitalise(state.severity)
            });
        }

        if (filters.length === 0) {
            activeFilters.hidden = true;
            return;
        }

        activeFilters.hidden = false;

        filters.forEach((filter) => {
            const button = document.createElement("button");

            button.type = "button";
            button.className = "privesc-filter-chip";
            button.dataset.filterType = filter.type;

            button.innerHTML = `
                <span>${escapeHtml(filter.label)}</span>
                <span aria-hidden="true">&times;</span>
            `;

            button.setAttribute(
                "aria-label",
                `Remove ${filter.label} filter`
            );

            button.addEventListener("click", () => {
                clearSingleFilter(filter.type);
            });

            activeFilters.appendChild(button);
        });
    }

    function clearSingleFilter(type) {
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

    /*
     * -------------------------------------------------------------------------
     * Technique Cards
     * -------------------------------------------------------------------------
     */

    function createTechniqueCard(technique) {
        const article = document.createElement("article");

        const techniqueId = safeId(
            technique.id ||
            technique.name ||
            `technique-${Math.random().toString(36).slice(2)}`
        );

        const detailId = `${techniqueId}-details`;

        article.className = "privesc-card";
        article.dataset.techniqueId = techniqueId;
        article.dataset.category = technique.category || "";
        article.dataset.severity = technique.severity || "";

        article.innerHTML = `
            <div
                class="privesc-card-header"
                data-technique-toggle
                role="button"
                tabindex="0"
                aria-expanded="false"
                aria-controls="${escapeAttribute(detailId)}"
            >
                <div class="privesc-card-title-group">
                    <div class="privesc-card-badges">
                        ${renderPlatformBadge(technique)}
                        ${renderCategoryBadge(technique)}
                        ${renderSeverityBadge(technique)}
                        ${renderConfidenceBadge(technique)}
                    </div>

                    <h2 class="privesc-card-title">
                        ${escapeHtml(technique.name || "Unnamed technique")}
                    </h2>

                    <p class="privesc-card-summary">
                        ${escapeHtml(technique.summary || "")}
                    </p>
                </div>

                <div
                    class="privesc-card-chevron"
                    aria-hidden="true"
                >
                    &#9662;
                </div>
            </div>

            <div
                id="${escapeAttribute(detailId)}"
                class="privesc-card-details"
                hidden
            >
                ${renderTechniqueDetails(technique)}
            </div>
        `;

        return article;
    }

    function renderPlatformBadge(technique) {
        const platform =
            String(technique.platform || state.platform).toUpperCase();

        return `
            <span class="privesc-badge privesc-badge-platform">
                ${escapeHtml(platform)}
            </span>
        `;
    }

    function renderCategoryBadge(technique) {
        if (!technique.category) {
            return "";
        }

        return `
            <span class="privesc-badge privesc-badge-category">
                ${escapeHtml(technique.category)}
            </span>
        `;
    }

    function renderSeverityBadge(technique) {
        if (!technique.severity) {
            return "";
        }

        const severity = String(technique.severity).toLowerCase();

        return `
            <span
                class="privesc-badge privesc-badge-severity privesc-severity-${escapeAttribute(severity)}"
            >
                ${escapeHtml(severity.toUpperCase())}
            </span>
        `;
    }

    function renderConfidenceBadge(technique) {
        if (!technique.confidence) {
            return "";
        }

        const confidence = String(technique.confidence).toLowerCase();

        return `
            <span
                class="privesc-badge privesc-badge-confidence privesc-confidence-${escapeAttribute(confidence)}"
            >
                ${escapeHtml(confidence.toUpperCase())}
            </span>
        `;
    }

    function renderTechniqueDetails(technique) {
        return `
            ${renderFoundSection(technique)}
            ${renderRequirementsSection(technique)}
            ${renderCommandsSection(technique)}
            ${renderListSection(
                "Validation",
                technique.validation,
                "privesc-validation"
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
            ${renderMitreSection(technique)}
            ${renderTagsSection(technique)}
            ${renderRelatedSection(technique)}
        `;
    }

    function renderFoundSection(technique) {
        return renderListSection(
            "What You Found",
            technique.found,
            "privesc-found"
        );
    }

    function renderRequirementsSection(technique) {
        if (
            !Array.isArray(technique.requires) ||
            technique.requires.length === 0
        ) {
            return "";
        }

        const items = technique.requires
            .map(
                (requirement) => `
                    <li>
                        <span
                            class="privesc-requirement-marker"
                            aria-hidden="true"
                        >
                            &#9633;
                        </span>
                        <span>${escapeHtml(requirement)}</span>
                    </li>
                `
            )
            .join("");

        return `
            <section class="privesc-detail-section privesc-requirements">
                <h3>Preconditions</h3>
                <ul class="privesc-requirement-list">
                    ${items}
                </ul>
            </section>
        `;
    }

    function renderCommandsSection(technique) {
        if (
            !Array.isArray(technique.commands) ||
            technique.commands.length === 0
        ) {
            return "";
        }

        const commands = technique.commands
            .map((command, index) => {
                const commandId =
                    `${safeId(technique.id || technique.name)}-command-${index}`;

                return `
                    <div class="privesc-command">
                        <pre><code id="${escapeAttribute(commandId)}">${escapeHtml(command)}</code></pre>

                        <button
                            type="button"
                            class="privesc-copy-button"
                            data-copy-command
                            data-command="${escapeAttribute(command)}"
                            aria-label="Copy command"
                            title="Copy command"
                        >
                            Copy
                        </button>
                    </div>
                `;
            })
            .join("");

        return `
            <section class="privesc-detail-section privesc-commands">
                <h3>Enumeration</h3>
                ${commands}
            </section>
        `;
    }

    function renderListSection(title, values, className) {
        if (!Array.isArray(values) || values.length === 0) {
            return "";
        }

        const items = values
            .map((value) => `<li>${escapeHtml(value)}</li>`)
            .join("");

        return `
            <section class="privesc-detail-section ${escapeAttribute(className)}">
                <h3>${escapeHtml(title)}</h3>
                <ul>
                    ${items}
                </ul>
            </section>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * MITRE ATT&CK
     * -------------------------------------------------------------------------
     */

    function renderMitreSection(technique) {
        if (
            !Array.isArray(technique.mitre) ||
            technique.mitre.length === 0
        ) {
            return "";
        }

        const entries = technique.mitre
            .map(renderMitreEntry)
            .filter(Boolean)
            .join("");

        if (!entries) {
            return "";
        }

        return `
            <section class="privesc-detail-section privesc-mitre">
                <h3>MITRE ATT&amp;CK</h3>

                <div class="privesc-mitre-list">
                    ${entries}
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
                <span class="privesc-mitre-entry">
                    ${escapeHtml(entry)}
                </span>
            `;
        }

        const id = entry.id || "";
        const name = entry.name || "";
        const url = safeExternalUrl(entry.url);

        const label = [id, name]
            .filter(Boolean)
            .join(" - ");

        if (!label) {
            return "";
        }

        if (!url) {
            return `
                <span class="privesc-mitre-entry">
                    ${escapeHtml(label)}
                </span>
            `;
        }

        return `
            <a
                class="privesc-mitre-entry"
                href="${escapeAttribute(url)}"
                target="_blank"
                rel="noopener noreferrer"
            >
                ${escapeHtml(label)}
            </a>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Tags
     * -------------------------------------------------------------------------
     */

    function renderTagsSection(technique) {
        if (
            !Array.isArray(technique.tags) ||
            technique.tags.length === 0
        ) {
            return "";
        }

        const tags = technique.tags
            .map(
                (tag) => `
                    <button
                        type="button"
                        class="privesc-tag"
                        data-search-tag="${escapeAttribute(tag)}"
                    >
                        ${escapeHtml(tag)}
                    </button>
                `
            )
            .join("");

        return `
            <section class="privesc-detail-section privesc-tags-section">
                <h3>Tags</h3>

                <div class="privesc-tags">
                    ${tags}
                </div>
            </section>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Related Notes
     * -------------------------------------------------------------------------
     */

    function renderRelatedSection(technique) {
        if (
            !Array.isArray(technique.related) ||
            technique.related.length === 0
        ) {
            return "";
        }

        const links = technique.related
            .map((related) => {
                const parsed = parseRelatedEntry(related);

                if (!parsed) {
                    return "";
                }

                return `
                    <a
                        class="privesc-related-link"
                        href="${escapeAttribute(parsed.url)}"
                    >
                        ${escapeHtml(parsed.label)}
                    </a>
                `;
            })
            .filter(Boolean)
            .join("");

        if (!links) {
            return "";
        }

        return `
            <section class="privesc-detail-section privesc-related">
                <h3>Related Notes</h3>

                <div class="privesc-related-links">
                    ${links}
                </div>
            </section>
        `;
    }

    function parseRelatedEntry(entry) {
        if (!entry) {
            return null;
        }

        if (typeof entry === "object") {
            if (!entry.url) {
                return null;
            }

            return {
                url: resolveInternalUrl(entry.url),
                label: entry.label || humanisePath(entry.url)
            };
        }

        if (typeof entry === "string") {
            return {
                url: resolveInternalUrl(entry),
                label: humanisePath(entry)
            };
        }

        return null;
    }

    function resolveInternalUrl(path) {
        try {
            return new URL(path, document.baseURI).href;
        } catch {
            return path;
        }
    }

    function humanisePath(path) {
        const clean = String(path)
            .replace(/[?#].*$/, "")
            .replace(/\/+$/, "");

        const parts = clean
            .split("/")
            .filter(Boolean);

        const last = parts[parts.length - 1] || "Related Note";

        return last
            .replace(/\.md$/i, "")
            .replace(/[-_]+/g, " ")
            .replace(/\b\w/g, (character) => character.toUpperCase());
    }

    /*
     * -------------------------------------------------------------------------
     * Expand / Collapse
     * -------------------------------------------------------------------------
     */

    function toggleTechnique(toggle) {
        const card = toggle.closest(".privesc-card");

        if (!card) {
            return;
        }

        const details = card.querySelector(".privesc-card-details");

        if (!details) {
            return;
        }

        const expanded =
            toggle.getAttribute("aria-expanded") === "true";

        toggle.setAttribute(
            "aria-expanded",
            expanded ? "false" : "true"
        );

        details.hidden = expanded;

        card.classList.toggle("is-expanded", !expanded);
    }

    /*
     * -------------------------------------------------------------------------
     * Copy Commands
     * -------------------------------------------------------------------------
     */

    async function copyCommand(button) {
        const command = button.dataset.command;

        if (!command) {
            return;
        }

        const originalText = button.textContent;

        try {
            await writeClipboard(command);

            button.textContent = "Copied";
            button.classList.add("is-copied");

            window.setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove("is-copied");
            }, 1500);
        } catch (error) {
            console.error(
                "[PrivEsc Explorer] Unable to copy command:",
                error
            );

            button.textContent = "Copy failed";

            window.setTimeout(() => {
                button.textContent = originalText;
            }, 1500);
        }
    }

    async function writeClipboard(value) {
        if (
            navigator.clipboard &&
            window.isSecureContext
        ) {
            await navigator.clipboard.writeText(value);
            return;
        }

        const textarea = document.createElement("textarea");

        textarea.value = value;
        textarea.setAttribute("readonly", "");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        textarea.style.pointerEvents = "none";

        document.body.appendChild(textarea);

        textarea.select();
        textarea.setSelectionRange(0, textarea.value.length);

        const successful = document.execCommand("copy");

        textarea.remove();

        if (!successful) {
            throw new Error("Legacy clipboard copy failed.");
        }
    }

    /*
     * -------------------------------------------------------------------------
     * Tag Searching
     * -------------------------------------------------------------------------
     */

    document.addEventListener("click", (event) => {
        const tag = event.target.closest("[data-search-tag]");

        if (!tag || !explorer || !explorer.contains(tag)) {
            return;
        }

        const value = tag.dataset.searchTag;

        if (!value) {
            return;
        }

        state.query = value;
        searchInput.value = value;

        render();

        explorer.scrollIntoView({
            behavior: prefersReducedMotion() ? "auto" : "smooth",
            block: "start"
        });

        searchInput.focus();
    });

    /*
     * -------------------------------------------------------------------------
     * Error Rendering
     * -------------------------------------------------------------------------
     */

    function renderFatalError(message) {
        if (!explorer) {
            return;
        }

        const safeMessage = escapeHtml(message);

        if (resultCount) {
            resultCount.textContent = "Explorer unavailable";
        }

        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="privesc-error" role="alert">
                    <strong>Unable to load PrivEsc Explorer</strong>
                    <p>${safeMessage}</p>
                </div>
            `;
            return;
        }

        explorer.innerHTML = `
            <div class="privesc-error" role="alert">
                <strong>Unable to load PrivEsc Explorer</strong>
                <p>${safeMessage}</p>
            </div>
        `;
    }

    /*
     * -------------------------------------------------------------------------
     * Utility Functions
     * -------------------------------------------------------------------------
     */

    function debounce(callback, delay = 100) {
        let timeoutId = null;

        return (...args) => {
            window.clearTimeout(timeoutId);

            timeoutId = window.setTimeout(() => {
                callback(...args);
            }, delay);
        };
    }

    function pluralise(count, singular, plural) {
        return count === 1 ? singular : plural;
    }

    function capitalise(value) {
        const stringValue = String(value || "");

        if (!stringValue) {
            return "";
        }

        return (
            stringValue.charAt(0).toUpperCase() +
            stringValue.slice(1)
        );
    }

    function safeId(value) {
        return String(value || "")
            .trim()
            .toLowerCase()
            .replace(/[^a-z0-9_-]+/g, "-")
            .replace(/^-+|-+$/g, "");
    }

    function safeExternalUrl(value) {
        if (!value) {
            return null;
        }

        try {
            const url = new URL(value, document.baseURI);

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
     * Material's navigation.instant feature can replace page content without
     * performing a normal browser reload.
     *
     * document$ is exposed by Material when instant navigation is enabled.
     * We use it when available while retaining DOMContentLoaded as the normal
     * fallback.
     */

    function start() {
        initialisePrivEscExplorer();
    }

    if (typeof document$ !== "undefined" && document$?.subscribe) {
        document$.subscribe(() => {
            start();
        });
    } else if (document.readyState === "loading") {
        document.addEventListener(
            "DOMContentLoaded",
            start,
            { once: true }
        );
    } else {
        start();
    }
})();
