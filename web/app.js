// Bootstrap and UI wiring for the web companion.
//
// Pipeline on first load:
//   1. Fetch design_tokens.json + elements.json + the active language JSON.
//   2. Project token values onto :root as CSS custom properties.
//   3. Render the periodic table grid and prepare the side panel.
//   4. Pyodide is fetched lazily on the first molar-mass calc click so that
//      visitors who only want to browse element data never pay the 3-5 s
//      cold-start cost.

import {
    SUPPORTED_LANGUAGES,
    loadLanguage,
    tr,
    getCategoryText,
    getStandardStateText,
} from "./i18n.js";

const APP_VERSION = "1.3.0";

const state = {
    tokens: null,
    elements: [],
    elementsBySymbol: new Map(),
    activeLanguage: "en",
    activeTheme: "dark",
    activeTab: "info",
    selectedSymbol: null,
    pyodide: null,
    pyodideLoading: null,
};

const INFO_FIELDS = [
    { key: "atomic_number", source: "atomic_number" },
    { key: "atomic_mass", source: "atomic_mass", format: (v) => formatNumber(v, 4) },
    { key: "category", source: "category", localize: getCategoryText },
    { key: "period", source: "period" },
    { key: "group", source: "group" },
    { key: "standard_state", source: "standard_state", localize: getStandardStateText },
    { key: "electronegativity", source: "electronegativity", format: (v) => formatNumber(v, 2) },
    { key: "atomic_radius", source: "atomic_radius", format: (v) => formatNumber(v, 1) },
    { key: "ionization_energy", source: "ionization_energy", format: (v) => formatNumber(v, 3) },
    { key: "electron_affinity", source: "electron_affinity", format: (v) => formatNumber(v, 3) },
    { key: "oxidation_states", source: "oxidation_states" },
    { key: "melting_point", source: "melting_point", format: (v) => formatNumber(v, 2) },
    { key: "boiling_point", source: "boiling_point", format: (v) => formatNumber(v, 2) },
    { key: "density", source: "density", format: (v) => formatNumber(v, 4) },
    { key: "year_discovered", source: "year_discovered" },
];

function kebab(name) {
    return name.replace(/_/g, "-");
}

function formatNumber(value, decimals) {
    if (value === null || value === undefined || value === "") return "—";
    const num = Number(value);
    if (!Number.isFinite(num)) return "—";
    return num.toFixed(decimals);
}

function setCssProperty(name, value) {
    document.documentElement.style.setProperty(name, value);
}

function applyDesignTokens(tokens, themeName) {
    const root = document.documentElement;

    const themeColors = tokens.color.theme[themeName] ?? tokens.color.theme.dark;
    for (const [key, value] of Object.entries(themeColors)) {
        setCssProperty(`--color-${kebab(key)}`, value);
    }

    const categories = tokens.color.category[themeName] ?? tokens.color.category.dark;
    for (const [key, value] of Object.entries(categories)) {
        setCssProperty(`--color-category-${kebab(key)}`, value);
    }

    for (const [key, value] of Object.entries(tokens.color.button_border)) {
        setCssProperty(`--color-border-button-${kebab(key)}`, value);
    }
    setCssProperty("--color-fallback-ui", tokens.color.fallback.ui);
    for (const [key, value] of Object.entries(tokens.color.text_on_color)) {
        setCssProperty(`--color-text-on-color-${kebab(key)}`, value);
    }

    for (const [key, value] of Object.entries(tokens.font.family)) {
        setCssProperty(`--font-family-${kebab(key)}`, value);
    }
    for (const [key, value] of Object.entries(tokens.font.size)) {
        setCssProperty(`--font-size-${kebab(key)}`, `${value}px`);
    }
    for (const [key, value] of Object.entries(tokens.font.weight)) {
        setCssProperty(`--font-weight-${kebab(key)}`, value);
    }
    for (const [key, value] of Object.entries(tokens.font.letter_spacing)) {
        setCssProperty(`--font-letter-spacing-${kebab(key)}`, `${value}px`);
    }

    for (const [key, value] of Object.entries(tokens.spacing)) {
        setCssProperty(`--spacing-${kebab(key)}`, `${value}px`);
    }
    for (const [key, value] of Object.entries(tokens.radius)) {
        if (typeof value === "number") {
            const isRatio = key === "cell_ratio";
            setCssProperty(`--radius-${kebab(key)}`, isRatio ? value : `${value}px`);
        }
    }
    for (const [key, value] of Object.entries(tokens.border)) {
        setCssProperty(`--border-${kebab(key)}`, `${value}px`);
    }
    for (const [key, value] of Object.entries(tokens.scale)) {
        setCssProperty(`--scale-${kebab(key)}`, `${value}px`);
    }

    root.dataset.theme = themeName;
    state.activeTheme = themeName;
}

function categoryToTokenKey(category) {
    return category.replace(/[\s-]/g, "_");
}

function readableTextColor(hexColor) {
    if (!hexColor) return state.tokens?.color?.text_on_color?.dark ?? "#111111";
    const stripped = hexColor.replace("#", "");
    if (stripped.length !== 6) return state.tokens?.color?.text_on_color?.dark ?? "#111111";
    const r = parseInt(stripped.slice(0, 2), 16);
    const g = parseInt(stripped.slice(2, 4), 16);
    const b = parseInt(stripped.slice(4, 6), 16);
    const luminance = 0.299 * r + 0.587 * g + 0.114 * b;
    const threshold = state.tokens?.luminance?.text_on_color_threshold ?? 160;
    if (luminance >= threshold) {
        return state.tokens?.color?.text_on_color?.dark ?? "#111111";
    }
    return state.tokens?.color?.text_on_color?.light ?? "#FFFFFF";
}

function getCategoryColor(category) {
    const tokenKey = categoryToTokenKey(category);
    const themed = state.tokens?.color?.category?.[state.activeTheme] ?? {};
    return themed[tokenKey] ?? state.tokens?.color?.fallback?.ui ?? "#7A7A7A";
}

function renderPeriodicTable() {
    const main = document.getElementById("periodic-table");
    const series = document.getElementById("periodic-series");
    // Preserve the static structural cells declared in HTML (group headers,
    // period numbers, transition-metals band, series labels). Only clear
    // previously-rendered element cells.
    main.querySelectorAll(".element-cell").forEach((node) => node.remove());
    series.querySelectorAll(".element-cell").forEach((node) => node.remove());

    for (const element of state.elements) {
        const cell = document.createElement("button");
        cell.type = "button";
        cell.className = "element-cell";
        cell.dataset.symbol = element.symbol;
        // The element grid is offset by +1 column to leave room for the
        // period/series label column on the left, and the main grid is
        // offset by +1 row for the group-header row.
        cell.style.gridColumn = String(element.display_column + 1);
        const inMain = element.display_row <= 7;
        cell.style.gridRow = String(
            inMain ? element.display_row + 1 : element.display_row - 7
        );
        const bg = getCategoryColor(element.category);
        cell.style.setProperty("--cell-bg", bg);
        cell.style.setProperty("--cell-text", readableTextColor(bg));

        const number = document.createElement("span");
        number.className = "number";
        number.textContent = element.atomic_number;
        const symbol = document.createElement("span");
        symbol.className = "symbol";
        symbol.textContent = element.symbol;
        cell.append(number, symbol);

        cell.addEventListener("click", () => selectElement(element.symbol));

        if (inMain) {
            main.appendChild(cell);
        } else {
            series.appendChild(cell);
        }
    }

    if (state.selectedSymbol) {
        markSelectedCell(state.selectedSymbol);
    }
}

function markSelectedCell(symbol) {
    document
        .querySelectorAll(".element-cell.is-selected")
        .forEach((node) => node.classList.remove("is-selected"));
    if (!symbol) return;
    const node = document.querySelector(`.element-cell[data-symbol="${CSS.escape(symbol)}"]`);
    if (node) node.classList.add("is-selected");
}

function selectElement(symbol) {
    state.selectedSymbol = symbol;
    markSelectedCell(symbol);
    renderInfoCard();
    document.getElementById("info-empty").hidden = true;
    document.getElementById("info-card").hidden = false;
}

function renderInfoCard() {
    if (!state.selectedSymbol) return;
    const element = state.elementsBySymbol.get(state.selectedSymbol);
    if (!element) return;

    const accent = getCategoryColor(element.category);
    const fg = readableTextColor(accent);

    const symbolNode = document.getElementById("info-symbol");
    symbolNode.textContent = element.symbol;
    symbolNode.style.background = accent;
    symbolNode.style.color = fg;
    symbolNode.style.borderColor = accent;

    document.getElementById("info-atomic-number").textContent = element.atomic_number;
    document.getElementById("info-name").textContent = element.name;
    document.getElementById("info-category").textContent = getCategoryText(
        state.activeLanguage,
        element.category,
    );

    const grid = document.getElementById("info-grid");
    grid.replaceChildren();
    for (const field of INFO_FIELDS) {
        const wrap = document.createElement("div");
        const dt = document.createElement("dt");
        dt.textContent = tr(state.activeLanguage, field.key);
        const dd = document.createElement("dd");
        let value = element[field.source];
        if (field.localize) {
            value = field.localize(state.activeLanguage, value);
        } else if (field.format) {
            value = field.format(value);
        } else if (value === null || value === undefined || value === "") {
            value = "—";
        }
        dd.textContent = value;
        wrap.append(dt, dd);
        grid.appendChild(wrap);
    }
}

function setActiveTab(tabId) {
    state.activeTab = tabId;
    const tabs = ["info", "molar"];
    for (const id of tabs) {
        const tab = document.getElementById(`tab-${id}`);
        const panel = document.getElementById(`panel-${id}`);
        const isActive = id === tabId;
        tab.classList.toggle("is-active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
        panel.hidden = !isActive;
    }
}

function applyStaticTranslations() {
    document.documentElement.lang = state.activeLanguage;
    document.getElementById("app-title").textContent = tr(state.activeLanguage, "title");
    document.getElementById("theme-label").textContent =
        state.activeTheme === "dark" ? "Light" : "Dark";
    document.getElementById("app-version").textContent = `v${APP_VERSION}`;
    for (const node of document.querySelectorAll("[data-i18n]")) {
        node.textContent = tr(state.activeLanguage, node.dataset.i18n);
    }
    document.getElementById("info-empty").textContent = tr(
        state.activeLanguage,
        "info_prompt",
    );
}

function populateLanguageSelect() {
    const select = document.getElementById("language-select");
    select.replaceChildren();
    for (const { code, label } of SUPPORTED_LANGUAGES) {
        const option = document.createElement("option");
        option.value = code;
        option.textContent = label;
        if (code === state.activeLanguage) option.selected = true;
        select.appendChild(option);
    }
    select.addEventListener("change", async (event) => {
        const code = event.target.value;
        await loadLanguage(code);
        state.activeLanguage = code;
        applyStaticTranslations();
        if (state.selectedSymbol) renderInfoCard();
    });
}

function setupThemeToggle() {
    const button = document.getElementById("theme-toggle");
    button.addEventListener("click", () => {
        const next = state.activeTheme === "dark" ? "light" : "dark";
        applyDesignTokens(state.tokens, next);
        document.getElementById("theme-label").textContent =
            next === "dark" ? "Light" : "Dark";
        renderPeriodicTable();
        if (state.selectedSymbol) renderInfoCard();
    });
}

function setupTabs() {
    document.getElementById("tab-info").addEventListener("click", () => setActiveTab("info"));
    document.getElementById("tab-molar").addEventListener("click", () => setActiveTab("molar"));
}

async function ensurePyodide() {
    if (state.pyodide) return state.pyodide;
    if (state.pyodideLoading) return state.pyodideLoading;

    const status = document.getElementById("pyodide-status");
    status.textContent = "Loading Pyodide…";

    state.pyodideLoading = (async () => {
        // eslint-disable-next-line no-undef
        const pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
        });
        const moduleSource = await fetch("./python/molar_mass.py").then((response) => {
            if (!response.ok) {
                throw new Error(`Failed to fetch molar_mass.py: HTTP ${response.status}`);
            }
            return response.text();
        });
        pyodide.FS.mkdirTree("/python");
        pyodide.FS.writeFile("/python/molar_mass.py", moduleSource);
        pyodide.globals.set("__elements_json", JSON.stringify(state.elements));
        pyodide.runPython(`
import sys, json
if '/python' not in sys.path:
    sys.path.insert(0, '/python')
import molar_mass
ELEMENTS = json.loads(__elements_json)
`);
        state.pyodide = pyodide;
        status.textContent = "Pyodide ready";
        return pyodide;
    })();

    try {
        return await state.pyodideLoading;
    } catch (err) {
        status.textContent = "Pyodide failed";
        state.pyodideLoading = null;
        throw err;
    }
}

async function computeMolarMass(formula) {
    const pyodide = await ensurePyodide();
    pyodide.globals.set("__formula", formula);
    const result = pyodide.runPython(`
import json
try:
    atoms = molar_mass.parse_formula(__formula)
    total = molar_mass.compute_molar_mass(atoms, ELEMENTS)
    composition = molar_mass.compute_percent_composition(atoms, ELEMENTS, total_mass=total)
    json.dumps({"ok": True, "total": total, "composition": composition})
except molar_mass.FormulaError as exc:
    json.dumps({"ok": False, "code": exc.code, "params": exc.params, "message": str(exc)})
`);
    return JSON.parse(result);
}

function formatErrorMessage(payload) {
    if (!payload.code) return payload.message;
    const key = `formula_error_${payload.code}`;
    return tr(state.activeLanguage, key, payload.params);
}

function setupMolarForm() {
    const form = document.getElementById("molar-form");
    const input = document.getElementById("molar-input");
    const status = document.getElementById("molar-status");
    const result = document.getElementById("molar-result");
    const totalNode = document.getElementById("molar-total-value");
    const tbody = document.getElementById("molar-table-body");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const formula = input.value.trim();
        if (!formula) return;

        status.classList.remove("is-error");
        status.textContent = "…";
        result.hidden = true;

        try {
            const payload = await computeMolarMass(formula);
            if (!payload.ok) {
                status.classList.add("is-error");
                status.textContent = formatErrorMessage(payload);
                return;
            }
            status.textContent = "";
            totalNode.textContent = `${formula} → ${payload.total.toFixed(3)} g/mol`;
            tbody.replaceChildren();
            for (const row of payload.composition) {
                const tr = document.createElement("tr");
                const cells = [row.symbol, row.count, row.mass.toFixed(3), `${row.percent.toFixed(2)}%`];
                for (const value of cells) {
                    const td = document.createElement("td");
                    td.textContent = value;
                    tr.appendChild(td);
                }
                tbody.appendChild(tr);
            }
            result.hidden = false;
        } catch (err) {
            status.classList.add("is-error");
            status.textContent = err.message;
        }
    });
}

async function bootstrap() {
    const loader = document.getElementById("loader");
    const loaderMessage = document.getElementById("loader-message");

    loaderMessage.textContent = "Loading design tokens…";
    const tokensResponse = await fetch("./design_tokens.json");
    state.tokens = await tokensResponse.json();
    applyDesignTokens(state.tokens, state.activeTheme);

    loaderMessage.textContent = "Loading element dataset…";
    const elementsResponse = await fetch("./data/elements.json");
    state.elements = await elementsResponse.json();
    for (const element of state.elements) {
        state.elementsBySymbol.set(element.symbol, element);
    }

    loaderMessage.textContent = "Loading translations…";
    await loadLanguage("en");
    if (state.activeLanguage !== "en") await loadLanguage(state.activeLanguage);

    populateLanguageSelect();
    setupThemeToggle();
    setupTabs();
    setupMolarForm();
    applyStaticTranslations();
    renderPeriodicTable();

    loader.hidden = true;
    document.getElementById("app").hidden = false;
}

bootstrap().catch((err) => {
    console.error(err);
    document.getElementById("loader-message").textContent = `Bootstrap failed: ${err.message}`;
});
