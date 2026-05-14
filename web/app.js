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
    activeToolTab: "molar",
    selectedSymbol: null,
    pyodide: null,
    pyodideLoading: null,
    stoich: null,
    toolsModalReturnFocus: null,
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
    if (state.activeTab === "electron") {
        renderElectronPanel();
    }
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

const SIDE_TAB_IDS = ["info", "electron"];
const TOOL_TAB_IDS = ["molar", "stoichiometry", "concentration", "gas-laws", "ph"];

function _setActiveTabIn(ids, activeId) {
    for (const id of ids) {
        const tab = document.getElementById(`tab-${id}`);
        const panel = document.getElementById(`panel-${id}`);
        if (!tab || !panel) continue;
        const isActive = id === activeId;
        tab.classList.toggle("is-active", isActive);
        tab.setAttribute("aria-selected", isActive ? "true" : "false");
        panel.hidden = !isActive;
    }
}

function setActiveTab(tabId) {
    state.activeTab = tabId;
    _setActiveTabIn(SIDE_TAB_IDS, tabId);
    if (tabId === "electron") {
        renderElectronPanel();
    }
}

function setActiveToolTab(tabId) {
    state.activeToolTab = tabId;
    _setActiveTabIn(TOOL_TAB_IDS, tabId);
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
    for (const node of document.querySelectorAll("[data-i18n-placeholder]")) {
        node.placeholder = tr(state.activeLanguage, node.dataset.i18nPlaceholder);
    }
    for (const node of document.querySelectorAll("[data-i18n-aria-label]")) {
        node.setAttribute(
            "aria-label",
            tr(state.activeLanguage, node.dataset.i18nAriaLabel),
        );
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
        if (state.activeTab === "electron") renderElectronPanel();
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
    for (const id of SIDE_TAB_IDS) {
        document.getElementById(`tab-${id}`).addEventListener("click", () => setActiveTab(id));
    }
    for (const id of TOOL_TAB_IDS) {
        document.getElementById(`tab-${id}`).addEventListener("click", () => setActiveToolTab(id));
    }
}

function openToolsModal() {
    const modal = document.getElementById("tools-modal");
    state.toolsModalReturnFocus = document.activeElement;
    modal.hidden = false;
    document.body.classList.add("is-modal-open");
    const activePanel = document.getElementById(`panel-${state.activeToolTab}`);
    const focusable = activePanel
        ? activePanel.querySelector("input, button, select")
        : null;
    if (focusable) {
        focusable.focus();
    } else {
        document.getElementById("tools-close").focus();
    }
}

function closeToolsModal() {
    const modal = document.getElementById("tools-modal");
    if (modal.hidden) return;
    modal.hidden = true;
    document.body.classList.remove("is-modal-open");
    const returnTo = state.toolsModalReturnFocus;
    state.toolsModalReturnFocus = null;
    if (returnTo && typeof returnTo.focus === "function") {
        returnTo.focus();
    }
}

function setupToolsModal() {
    document.getElementById("tools-open").addEventListener("click", openToolsModal);
    const modal = document.getElementById("tools-modal");
    for (const node of modal.querySelectorAll("[data-tools-close]")) {
        node.addEventListener("click", closeToolsModal);
    }
    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && !modal.hidden) {
            event.preventDefault();
            closeToolsModal();
        }
    });
}

function computeMatchScore(element, query, localizedName) {
    const q = (query || "").trim().toLowerCase();
    if (!q) return 0;
    const name = String(element.name || "").toLowerCase();
    const loc = String(localizedName || element.name || "").toLowerCase();
    const sym = String(element.symbol || "").toLowerCase();
    const num = String(element.atomic_number || "");
    if (q === sym) return 100;
    if (q === num) return 98;
    if (q === name) return 96;
    if (q === loc) return 95;
    if (name.startsWith(q)) return 90;
    if (loc.startsWith(q)) return 89;
    if (sym.startsWith(q)) return 88;
    if (num.startsWith(q)) return 86;
    if (name.includes(q)) return 78;
    if (loc.includes(q)) return 77;
    if (sym.includes(q)) return 74;
    return 0;
}

function searchElements(query) {
    const ranked = [];
    for (const element of state.elements) {
        const score = computeMatchScore(element, query, element.name);
        if (score > 0) ranked.push({ score, element });
    }
    ranked.sort((a, b) =>
        b.score - a.score || a.element.atomic_number - b.element.atomic_number,
    );
    return ranked.map((row) => row.element);
}

function clearSearchHighlights() {
    document
        .querySelectorAll(".element-cell.is-search-match")
        .forEach((node) => node.classList.remove("is-search-match"));
}

function highlightMatches(matches) {
    clearSearchHighlights();
    for (const element of matches) {
        const node = document.querySelector(
            `.element-cell[data-symbol="${CSS.escape(element.symbol)}"]`,
        );
        if (node) node.classList.add("is-search-match");
    }
}

function setupSearchForm() {
    const form = document.getElementById("search-form");
    const input = document.getElementById("search-input");
    const status = document.getElementById("search-status");
    let debounceTimer = null;

    const updateLive = () => {
        const query = input.value.trim();
        status.classList.remove("is-error");
        if (!query) {
            clearSearchHighlights();
            status.textContent = "";
            return;
        }
        const matches = searchElements(query);
        highlightMatches(matches);
        if (!matches.length) {
            status.textContent = "";
            return;
        }
        const top = matches[0];
        status.textContent = tr(state.activeLanguage, "search_found", {
            name: top.name,
            symbol: top.symbol,
        });
    };

    input.addEventListener("input", () => {
        if (debounceTimer) clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updateLive, 80);
    });

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        if (debounceTimer) {
            clearTimeout(debounceTimer);
            debounceTimer = null;
        }
        const query = input.value.trim();
        if (!query) {
            clearSearchHighlights();
            status.classList.remove("is-error");
            status.textContent = "";
            return;
        }
        const matches = searchElements(query);
        highlightMatches(matches);
        if (!matches.length) {
            status.classList.add("is-error");
            status.textContent = tr(state.activeLanguage, "search_not_found");
            return;
        }
        const top = matches[0];
        status.classList.remove("is-error");
        status.textContent = tr(state.activeLanguage, "search_found", {
            name: top.name,
            symbol: top.symbol,
        });
        selectElement(top.symbol);
        const cell = document.querySelector(
            `.element-cell[data-symbol="${CSS.escape(top.symbol)}"]`,
        );
        if (cell) cell.scrollIntoView({ block: "nearest", behavior: "smooth" });
    });
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
        const PYTHON_FILES = [
            "molar_mass.py",
            "electron_configuration.py",
            "stoichiometry.py",
            "src/__init__.py",
            "src/config/__init__.py",
            "src/config/static_data.py",
            "src/domain/__init__.py",
            "src/domain/molar_mass.py",
        ];
        const sources = await Promise.all(
            PYTHON_FILES.map(async (relPath) => {
                const response = await fetch(`./python/${relPath}`);
                if (!response.ok) {
                    throw new Error(`Failed to fetch ${relPath}: HTTP ${response.status}`);
                }
                return [relPath, await response.text()];
            }),
        );
        pyodide.FS.mkdirTree("/python");
        pyodide.FS.mkdirTree("/python/src");
        pyodide.FS.mkdirTree("/python/src/config");
        pyodide.FS.mkdirTree("/python/src/domain");
        for (const [relPath, source] of sources) {
            pyodide.FS.writeFile(`/python/${relPath}`, source);
        }
        pyodide.globals.set("__elements_json", JSON.stringify(state.elements));
        pyodide.runPython(`
import sys, json
if '/python' not in sys.path:
    sys.path.insert(0, '/python')
import molar_mass
import electron_configuration
import stoichiometry
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

async function balanceEquation(equation) {
    const pyodide = await ensurePyodide();
    pyodide.globals.set("__equation", equation);
    const result = pyodide.runPython(`
import json
try:
    reactants, products = stoichiometry.parse_equation(__equation)
    coeffs = stoichiometry.balance_parsed(reactants, products)
    formatted = stoichiometry.format_balanced_equation(reactants, products, coeffs)
    json.dumps({"ok": True, "reactants": reactants, "products": products,
                "coefficients": coeffs, "formatted": formatted})
except stoichiometry.EquationError as exc:
    json.dumps({"ok": False, "code": exc.code, "params": exc.params, "message": str(exc)})
`);
    return JSON.parse(result);
}

async function computeStoichiometricMasses(
    reactants,
    products,
    coefficients,
    givenCompound,
    givenMassGrams,
) {
    const pyodide = await ensurePyodide();
    pyodide.globals.set("__r", JSON.stringify(reactants));
    pyodide.globals.set("__p", JSON.stringify(products));
    pyodide.globals.set("__c", JSON.stringify(coefficients));
    pyodide.globals.set("__given_compound", givenCompound);
    pyodide.globals.set("__given_mass", givenMassGrams);
    const result = pyodide.runPython(`
import json
try:
    rows = stoichiometry.compute_stoichiometric_masses(
        json.loads(__r), json.loads(__p), json.loads(__c),
        ELEMENTS, __given_compound, __given_mass,
    )
    json.dumps({"ok": True, "rows": rows})
except stoichiometry.EquationError as exc:
    json.dumps({"ok": False, "code": exc.code, "params": exc.params, "message": str(exc)})
`);
    return JSON.parse(result);
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

async function getOrbitalData(configText) {
    const pyodide = await ensurePyodide();
    pyodide.globals.set("__config_text", configText || "");
    const result = pyodide.runPython(`
import json
from electron_configuration import configuration_to_map, fill_boxes
from src.config.static_data import ORBITAL_BOX_COUNTS, VALID_SUBSHELLS

occupancy = configuration_to_map(__config_text)
rows = []
for level in range(1, 8):
    subshells = []
    for subshell in VALID_SUBSHELLS[level]:
        key = f"{level}{subshell}"
        if key in occupancy:
            count = occupancy[key]
            box_count = ORBITAL_BOX_COUNTS[subshell]
            subshells.append({
                "subshell": subshell,
                "key": key,
                "boxes": fill_boxes(count, box_count),
            })
    if subshells:
        rows.append({"level": level, "subshells": subshells})
json.dumps(rows)
`);
    return JSON.parse(result);
}

function renderOrbitalDiagram(symbol, rows) {
    const wrap = document.getElementById("electron-diagram-wrap");
    if (!rows.length) {
        wrap.replaceChildren();
        wrap.hidden = true;
        return;
    }
    const SVG_NS = "http://www.w3.org/2000/svg";
    const SUBSHELL_BOXES = { s: 1, p: 3, d: 5, f: 7 };
    const SUBSHELL_ORDER = ["s", "p", "d", "f"];
    const boxW = 14;
    const boxH = 20;
    const boxGap = 2;
    const colGap = 18;
    const labelH = 14;
    const rowGap = 6;
    const leftMargin = 22;
    const topMargin = 22;

    const colX = {};
    let cx = leftMargin;
    for (const sub of SUBSHELL_ORDER) {
        colX[sub] = cx;
        const width = SUBSHELL_BOXES[sub] * boxW + (SUBSHELL_BOXES[sub] - 1) * boxGap;
        cx += width + colGap;
    }
    const totalWidth = cx;
    const perRow = labelH + boxH + rowGap;
    const totalHeight = topMargin + 7 * perRow;

    const svg = document.createElementNS(SVG_NS, "svg");
    svg.setAttribute("class", "orbital-diagram");
    svg.setAttribute("viewBox", `0 0 ${totalWidth} ${totalHeight}`);
    svg.setAttribute("preserveAspectRatio", "xMinYMin meet");

    const symbolText = document.createElementNS(SVG_NS, "text");
    symbolText.setAttribute("class", "symbol-label");
    symbolText.setAttribute("x", "4");
    symbolText.setAttribute("y", "14");
    symbolText.textContent = symbol;
    svg.appendChild(symbolText);

    for (const row of rows) {
        const yBase = topMargin + (row.level - 1) * perRow;
        const lvl = document.createElementNS(SVG_NS, "text");
        lvl.setAttribute("class", "level-label");
        lvl.setAttribute("x", "4");
        lvl.setAttribute("y", String(yBase + labelH + boxH / 2 + 3));
        lvl.textContent = String(row.level);
        svg.appendChild(lvl);

        for (const ss of row.subshells) {
            const xBase = colX[ss.subshell];
            const lab = document.createElementNS(SVG_NS, "text");
            lab.setAttribute("class", "subshell-label");
            lab.setAttribute("x", String(xBase));
            lab.setAttribute("y", String(yBase + labelH - 2));
            lab.textContent = ss.key;
            svg.appendChild(lab);

            for (let i = 0; i < ss.boxes.length; i++) {
                const x = xBase + i * (boxW + boxGap);
                const y = yBase + labelH;
                const rect = document.createElementNS(SVG_NS, "rect");
                rect.setAttribute("class", "box");
                rect.setAttribute("x", String(x));
                rect.setAttribute("y", String(y));
                rect.setAttribute("width", String(boxW));
                rect.setAttribute("height", String(boxH));
                svg.appendChild(rect);

                if (ss.boxes[i] >= 1) {
                    const up = document.createElementNS(SVG_NS, "text");
                    up.setAttribute("class", "arrow-up");
                    up.setAttribute("x", String(x + 2));
                    up.setAttribute("y", String(y + boxH - 4));
                    up.textContent = "↑";
                    svg.appendChild(up);
                }
                if (ss.boxes[i] === 2) {
                    const dn = document.createElementNS(SVG_NS, "text");
                    dn.setAttribute("class", "arrow-down");
                    dn.setAttribute("x", String(x + boxW - 8));
                    dn.setAttribute("y", String(y + boxH - 4));
                    dn.textContent = "↓";
                    svg.appendChild(dn);
                }
            }
        }
    }
    wrap.replaceChildren(svg);
    wrap.hidden = false;
}

async function renderElectronPanel() {
    const element = state.selectedSymbol
        ? state.elementsBySymbol.get(state.selectedSymbol)
        : null;
    const wrap = document.getElementById("electron-diagram-wrap");
    const status = document.getElementById("electron-status");
    const prompt = document.getElementById("electron-prompt");
    const titleNode = document.getElementById("electron-title");

    if (!element) {
        wrap.hidden = true;
        wrap.replaceChildren();
        status.classList.remove("is-error");
        status.textContent = "";
        prompt.hidden = false;
        titleNode.textContent = tr(state.activeLanguage, "diagram_title");
        return;
    }

    titleNode.textContent = tr(state.activeLanguage, "diagram_title_symbol", {
        symbol: element.symbol,
    });
    prompt.hidden = true;
    status.classList.remove("is-error");
    status.textContent = state.pyodide ? "" : "Loading Pyodide…";

    try {
        const rows = await getOrbitalData(element.electron_configuration);
        if (!rows.length) {
            status.classList.add("is-error");
            status.textContent = tr(state.activeLanguage, "diagram_not_available");
            wrap.hidden = true;
            wrap.replaceChildren();
            return;
        }
        status.textContent = "";
        renderOrbitalDiagram(element.symbol, rows);
    } catch (err) {
        status.classList.add("is-error");
        status.textContent = err.message;
        wrap.hidden = true;
        wrap.replaceChildren();
    }
}

function formatErrorMessage(payload, prefix = "formula_error") {
    if (!payload.code) return payload.message;
    const key = `${prefix}_${payload.code}`;
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

function setupStoichForm() {
    const form = document.getElementById("stoich-form");
    const input = document.getElementById("stoich-input");
    const status = document.getElementById("stoich-status");
    const balanced = document.getElementById("stoich-balanced");
    const massSection = document.getElementById("stoich-mass-section");
    const compoundSelect = document.getElementById("stoich-compound");
    const massInput = document.getElementById("stoich-mass-input");
    const calcButton = document.getElementById("stoich-calc");
    const massTable = document.getElementById("stoich-mass-table");
    const massTbody = document.getElementById("stoich-mass-tbody");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const equation = input.value.trim();
        if (!equation) return;

        status.classList.remove("is-error");
        status.textContent = "…";
        balanced.hidden = true;
        balanced.textContent = "";
        massSection.hidden = true;
        massTable.hidden = true;

        try {
            const payload = await balanceEquation(equation);
            if (!payload.ok) {
                status.classList.add("is-error");
                status.textContent = formatErrorMessage(payload, "equation_error");
                state.stoich = null;
                return;
            }
            status.textContent = "";
            balanced.textContent = payload.formatted;
            balanced.hidden = false;

            const compounds = [...payload.reactants, ...payload.products];
            compoundSelect.replaceChildren();
            for (const compound of compounds) {
                const option = document.createElement("option");
                option.value = compound;
                option.textContent = compound;
                compoundSelect.appendChild(option);
            }
            state.stoich = {
                reactants: payload.reactants,
                products: payload.products,
                coefficients: payload.coefficients,
            };
            massSection.hidden = false;
        } catch (err) {
            status.classList.add("is-error");
            status.textContent = err.message;
            state.stoich = null;
        }
    });

    calcButton.addEventListener("click", async () => {
        if (!state.stoich) return;
        const given = compoundSelect.value;
        const mass = parseFloat(massInput.value);
        if (!given || !Number.isFinite(mass) || mass < 0) {
            status.classList.add("is-error");
            status.textContent = tr(state.activeLanguage, "stoichiometry_error");
            return;
        }

        status.classList.remove("is-error");
        status.textContent = "…";
        try {
            const payload = await computeStoichiometricMasses(
                state.stoich.reactants,
                state.stoich.products,
                state.stoich.coefficients,
                given,
                mass,
            );
            if (!payload.ok) {
                status.classList.add("is-error");
                status.textContent = formatErrorMessage(payload, "equation_error");
                return;
            }
            status.textContent = "";
            massTbody.replaceChildren();
            for (const row of payload.rows) {
                const tr = document.createElement("tr");
                const cells = [
                    row.compound,
                    String(row.coefficient),
                    row.molar_mass.toFixed(3),
                    row.moles.toFixed(4),
                    row.mass.toFixed(4),
                ];
                for (const value of cells) {
                    const td = document.createElement("td");
                    td.textContent = value;
                    tr.appendChild(td);
                }
                massTbody.appendChild(tr);
            }
            massTable.hidden = false;
        } catch (err) {
            status.classList.add("is-error");
            status.textContent = err.message;
        }
    });
}

function parsePositiveNumber(value) {
    if (value === null || value === undefined || value === "") return null;
    const num = Number(value);
    if (!Number.isFinite(num) || num <= 0) return null;
    return num;
}

function formatNumberSmart(value) {
    if (!Number.isFinite(value)) return "—";
    const abs = Math.abs(value);
    if (abs !== 0 && (abs < 1e-3 || abs >= 1e6)) {
        return value.toExponential(4);
    }
    if (abs >= 100) return value.toFixed(2);
    if (abs >= 1) return value.toFixed(4);
    return value.toFixed(5);
}

function setupConcentrationForm() {
    const modeSelect = document.getElementById("conc-mode");
    const solutionForm = document.getElementById("conc-solution-form");
    const dilutionForm = document.getElementById("conc-dilution-form");
    const status = document.getElementById("conc-status");
    const resultWrap = document.getElementById("conc-result");
    const resultList = document.getElementById("conc-result-list");

    const renderResult = (rows) => {
        resultList.replaceChildren();
        for (const { labelKey, value, fallbackLabel } of rows) {
            const dt = document.createElement("dt");
            dt.textContent = tr(state.activeLanguage, labelKey) || fallbackLabel;
            const dd = document.createElement("dd");
            dd.textContent = value;
            resultList.append(dt, dd);
        }
        resultWrap.hidden = false;
    };

    const showError = (key) => {
        status.classList.add("is-error");
        status.textContent = tr(state.activeLanguage, key);
        resultWrap.hidden = true;
    };

    const clearStatus = () => {
        status.classList.remove("is-error");
        status.textContent = "";
    };

    modeSelect.addEventListener("change", () => {
        clearStatus();
        resultWrap.hidden = true;
        if (modeSelect.value === "dilution") {
            solutionForm.hidden = true;
            dilutionForm.hidden = false;
        } else {
            solutionForm.hidden = false;
            dilutionForm.hidden = true;
        }
    });

    solutionForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearStatus();
        const formulaRaw = document.getElementById("conc-solute-formula").value.trim();
        const soluteMassG = parsePositiveNumber(
            document.getElementById("conc-solute-mass").value,
        );
        const soluteMoles = parsePositiveNumber(
            document.getElementById("conc-solute-moles").value,
        );
        const solventMassG = parsePositiveNumber(
            document.getElementById("conc-solvent-mass").value,
        );
        const volumeRaw = parsePositiveNumber(
            document.getElementById("conc-solution-volume").value,
        );
        const volumeUnit = document.getElementById("conc-volume-unit").value;
        const volumeL = volumeRaw === null
            ? null
            : (volumeUnit === "L" ? volumeRaw : volumeRaw / 1000);

        // We need a way to compute moles of solute: either user gave moles
        // directly, or user gave mass + formula (so we can call Pyodide for
        // the molar mass).
        if (soluteMoles === null && (soluteMassG === null || !formulaRaw)) {
            showError("concentration_error_missing_inputs");
            return;
        }

        let molesSolute = soluteMoles;
        let molarMassSolute = null;
        if (molesSolute === null) {
            status.textContent = "…";
            try {
                const payload = await computeMolarMass(formulaRaw);
                if (!payload.ok) {
                    status.classList.add("is-error");
                    status.textContent = formatErrorMessage(payload);
                    resultWrap.hidden = true;
                    return;
                }
                molarMassSolute = payload.total;
                molesSolute = soluteMassG / molarMassSolute;
            } catch (err) {
                status.classList.add("is-error");
                status.textContent = err.message;
                resultWrap.hidden = true;
                return;
            }
            status.textContent = "";
        }

        const rows = [];
        if (volumeL !== null && volumeL > 0) {
            const molarity = molesSolute / volumeL;
            rows.push({
                labelKey: "concentration_result_molarity",
                value: `${formatNumberSmart(molarity)} mol/L`,
                fallbackLabel: "Molarity",
            });
        }
        if (solventMassG !== null && solventMassG > 0) {
            const molality = molesSolute / (solventMassG / 1000);
            rows.push({
                labelKey: "concentration_result_molality",
                value: `${formatNumberSmart(molality)} mol/kg`,
                fallbackLabel: "Molality",
            });
            if (soluteMassG !== null && soluteMassG > 0) {
                const massPercent = (soluteMassG / (soluteMassG + solventMassG)) * 100;
                rows.push({
                    labelKey: "concentration_result_mass_percent",
                    value: `${formatNumberSmart(massPercent)} %`,
                    fallbackLabel: "Mass percent",
                });
            }
        }
        if (rows.length === 0) {
            showError("concentration_error_missing_inputs");
            return;
        }
        renderResult(rows);
    });

    dilutionForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const solveFor = document.getElementById("conc-dilution-solve-for").value;
        const m1 = parsePositiveNumber(document.getElementById("conc-dilution-m1").value);
        const m2 = parsePositiveNumber(document.getElementById("conc-dilution-m2").value);
        const v1Raw = parsePositiveNumber(document.getElementById("conc-dilution-v1").value);
        const v2Raw = parsePositiveNumber(document.getElementById("conc-dilution-v2").value);
        const v1Unit = document.getElementById("conc-dilution-v1-unit").value;
        const v2Unit = document.getElementById("conc-dilution-v2-unit").value;
        const v1 = v1Raw === null ? null : (v1Unit === "L" ? v1Raw : v1Raw / 1000);
        const v2 = v2Raw === null ? null : (v2Unit === "L" ? v2Raw : v2Raw / 1000);

        const inputs = { M1: m1, V1: v1, M2: m2, V2: v2 };
        for (const key of Object.keys(inputs)) {
            if (key === solveFor) continue;
            if (inputs[key] === null) {
                showError("concentration_error_missing_inputs");
                return;
            }
        }

        let result;
        let unit;
        switch (solveFor) {
            case "M1":
                result = (inputs.M2 * inputs.V2) / inputs.V1;
                unit = "mol/L";
                break;
            case "M2":
                result = (inputs.M1 * inputs.V1) / inputs.V2;
                unit = "mol/L";
                break;
            case "V1": {
                const litres = (inputs.M2 * inputs.V2) / inputs.M1;
                result = v1Unit === "L" ? litres : litres * 1000;
                unit = v1Unit;
                break;
            }
            case "V2": {
                const litres = (inputs.M1 * inputs.V1) / inputs.M2;
                result = v2Unit === "L" ? litres : litres * 1000;
                unit = v2Unit;
                break;
            }
            default:
                showError("concentration_error_missing_inputs");
                return;
        }

        renderResult([{
            labelKey: `concentration_dilution_${solveFor.toLowerCase()}`,
            value: `${formatNumberSmart(result)} ${unit}`,
            fallbackLabel: solveFor,
        }]);
    });
}

// Gas-law unit conversion factors → SI (Pa, m³, K, mol).
// Internally we use the value of R that pairs with the units we keep:
//   R = 0.0820573 L·atm·mol⁻¹·K⁻¹ when we keep pressure in atm and volume in L
//   R = 8.314462618 J·mol⁻¹·K⁻¹  when we work in Pa + m³.
// The conversions below normalise to atm + L + K + mol so the math reads
// the same regardless of which unit the user typed.
const PRESSURE_TO_ATM = {
    atm: 1.0,
    kPa: 1.0 / 101.325,
    mmHg: 1.0 / 760.0,
    Pa: 1.0 / 101325.0,
};
const PRESSURE_FROM_ATM = {
    atm: 1.0,
    kPa: 101.325,
    mmHg: 760.0,
    Pa: 101325.0,
};
const VOLUME_TO_L = { L: 1.0, mL: 0.001 };
const VOLUME_FROM_L = { L: 1.0, mL: 1000.0 };
const GAS_CONSTANT_L_ATM = 0.0820573660809596;

function temperatureToKelvin(value, unit) {
    return unit === "C" ? value + 273.15 : value;
}

function temperatureFromKelvin(kelvin, unit) {
    return unit === "C" ? kelvin - 273.15 : kelvin;
}

function readGasField(inputId, unitId, options = {}) {
    const inputEl = document.getElementById(inputId);
    const raw = inputEl.value.trim();
    const unit = unitId ? document.getElementById(unitId).value : null;
    if (raw === "") return { value: null, unit, blank: true };
    const num = Number(raw);
    if (!Number.isFinite(num)) return { value: null, unit, blank: false, invalid: true };
    if (options.allowNegative !== true && num < 0) {
        return { value: null, unit, blank: false, invalid: true };
    }
    return { value: num, unit, blank: false };
}

function setupGasLawsForm() {
    const modeSelect = document.getElementById("gas-mode");
    const idealForm = document.getElementById("gas-ideal-form");
    const combinedForm = document.getElementById("gas-combined-form");
    const daltonForm = document.getElementById("gas-dalton-form");
    const status = document.getElementById("gas-status");
    const resultWrap = document.getElementById("gas-result");
    const resultList = document.getElementById("gas-result-list");
    const daltonRows = document.getElementById("gas-dalton-rows");
    const daltonAddBtn = document.getElementById("gas-dalton-add");

    const showError = (key) => {
        status.classList.add("is-error");
        status.textContent = tr(state.activeLanguage, key);
        resultWrap.hidden = true;
    };
    const clearStatus = () => {
        status.classList.remove("is-error");
        status.textContent = "";
    };
    const renderResult = (rows) => {
        resultList.replaceChildren();
        for (const { label, value } of rows) {
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = value;
            resultList.append(dt, dd);
        }
        resultWrap.hidden = false;
    };

    modeSelect.addEventListener("change", () => {
        clearStatus();
        resultWrap.hidden = true;
        idealForm.hidden = modeSelect.value !== "ideal";
        combinedForm.hidden = modeSelect.value !== "combined";
        daltonForm.hidden = modeSelect.value !== "dalton";
    });

    idealForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const fields = {
            P: readGasField("gas-ideal-p", "gas-ideal-p-unit"),
            V: readGasField("gas-ideal-v", "gas-ideal-v-unit"),
            n: readGasField("gas-ideal-n", null),
            T: readGasField("gas-ideal-t", "gas-ideal-t-unit", { allowNegative: true }),
        };
        for (const f of Object.values(fields)) {
            if (f.invalid) {
                showError("gas_laws_error_two_blanks");
                return;
            }
        }
        const blanks = Object.entries(fields).filter(([, f]) => f.blank).map(([k]) => k);
        if (blanks.length !== 1) {
            showError("gas_laws_error_two_blanks");
            return;
        }
        const P_atm = fields.P.blank ? null : fields.P.value * PRESSURE_TO_ATM[fields.P.unit];
        const V_L = fields.V.blank ? null : fields.V.value * VOLUME_TO_L[fields.V.unit];
        const n_mol = fields.n.blank ? null : fields.n.value;
        const T_K = fields.T.blank ? null : temperatureToKelvin(fields.T.value, fields.T.unit);

        const target = blanks[0];
        let resultLabel;
        let resultValue;
        switch (target) {
            case "P": {
                const Patm = (n_mol * GAS_CONSTANT_L_ATM * T_K) / V_L;
                resultLabel = tr(state.activeLanguage, "gas_laws_pressure");
                resultValue =
                    `${formatNumberSmart(Patm * PRESSURE_FROM_ATM[fields.P.unit])} ${fields.P.unit}`;
                break;
            }
            case "V": {
                const VL = (n_mol * GAS_CONSTANT_L_ATM * T_K) / P_atm;
                resultLabel = tr(state.activeLanguage, "gas_laws_volume");
                resultValue =
                    `${formatNumberSmart(VL * VOLUME_FROM_L[fields.V.unit])} ${fields.V.unit}`;
                break;
            }
            case "n": {
                const n = (P_atm * V_L) / (GAS_CONSTANT_L_ATM * T_K);
                resultLabel = tr(state.activeLanguage, "gas_laws_moles");
                resultValue = `${formatNumberSmart(n)} mol`;
                break;
            }
            case "T": {
                const TK = (P_atm * V_L) / (n_mol * GAS_CONSTANT_L_ATM);
                const out = temperatureFromKelvin(TK, fields.T.unit);
                resultLabel = tr(state.activeLanguage, "gas_laws_temperature");
                resultValue = `${formatNumberSmart(out)} ${fields.T.unit === "C" ? "°C" : "K"}`;
                break;
            }
            default:
                return;
        }
        renderResult([{ label: resultLabel, value: resultValue }]);
    });

    combinedForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const fields = {
            P1: readGasField("gas-comb-p1", "gas-comb-p1-unit"),
            V1: readGasField("gas-comb-v1", "gas-comb-v1-unit"),
            T1: readGasField("gas-comb-t1", "gas-comb-t1-unit", { allowNegative: true }),
            P2: readGasField("gas-comb-p2", "gas-comb-p2-unit"),
            V2: readGasField("gas-comb-v2", "gas-comb-v2-unit"),
            T2: readGasField("gas-comb-t2", "gas-comb-t2-unit", { allowNegative: true }),
        };
        for (const f of Object.values(fields)) {
            if (f.invalid) {
                showError("gas_laws_error_two_blanks");
                return;
            }
        }
        const blanks = Object.entries(fields).filter(([, f]) => f.blank).map(([k]) => k);
        if (blanks.length !== 1) {
            showError("gas_laws_error_two_blanks");
            return;
        }
        const norm = {
            P1: fields.P1.blank ? null : fields.P1.value * PRESSURE_TO_ATM[fields.P1.unit],
            V1: fields.V1.blank ? null : fields.V1.value * VOLUME_TO_L[fields.V1.unit],
            T1: fields.T1.blank ? null : temperatureToKelvin(fields.T1.value, fields.T1.unit),
            P2: fields.P2.blank ? null : fields.P2.value * PRESSURE_TO_ATM[fields.P2.unit],
            V2: fields.V2.blank ? null : fields.V2.value * VOLUME_TO_L[fields.V2.unit],
            T2: fields.T2.blank ? null : temperatureToKelvin(fields.T2.value, fields.T2.unit),
        };

        const target = blanks[0];
        // P1·V1 / T1 = P2·V2 / T2 → solve for the missing variable in SI.
        let resultSI;
        switch (target) {
            case "P1":
                resultSI = (norm.P2 * norm.V2 * norm.T1) / (norm.T2 * norm.V1);
                break;
            case "V1":
                resultSI = (norm.P2 * norm.V2 * norm.T1) / (norm.T2 * norm.P1);
                break;
            case "T1":
                resultSI = (norm.P1 * norm.V1 * norm.T2) / (norm.P2 * norm.V2);
                break;
            case "P2":
                resultSI = (norm.P1 * norm.V1 * norm.T2) / (norm.T1 * norm.V2);
                break;
            case "V2":
                resultSI = (norm.P1 * norm.V1 * norm.T2) / (norm.T1 * norm.P2);
                break;
            case "T2":
                resultSI = (norm.P2 * norm.V2 * norm.T1) / (norm.P1 * norm.V1);
                break;
            default:
                return;
        }

        const f = fields[target];
        let label;
        let value;
        if (target.startsWith("P")) {
            label = tr(state.activeLanguage, "gas_laws_pressure");
            value = `${formatNumberSmart(resultSI * PRESSURE_FROM_ATM[f.unit])} ${f.unit}`;
        } else if (target.startsWith("V")) {
            label = tr(state.activeLanguage, "gas_laws_volume");
            value = `${formatNumberSmart(resultSI * VOLUME_FROM_L[f.unit])} ${f.unit}`;
        } else {
            label = tr(state.activeLanguage, "gas_laws_temperature");
            const out = temperatureFromKelvin(resultSI, f.unit);
            value = `${formatNumberSmart(out)} ${f.unit === "C" ? "°C" : "K"}`;
        }
        renderResult([{ label: `${target}: ${label}`, value }]);
    });

    const makeDaltonRow = (index) => {
        const row = document.createElement("div");
        row.className = "gas-dalton-row";
        row.dataset.index = String(index);

        const labelInput = document.createElement("input");
        labelInput.type = "text";
        labelInput.className = "molar-input";
        labelInput.placeholder = tr(state.activeLanguage, "gas_laws_dalton_component_label");
        labelInput.dataset.role = "label";

        const fractionInput = document.createElement("input");
        fractionInput.type = "number";
        fractionInput.className = "molar-input";
        fractionInput.min = "0";
        fractionInput.step = "any";
        fractionInput.placeholder = tr(state.activeLanguage, "gas_laws_dalton_mole_fraction");
        fractionInput.dataset.role = "fraction";

        const removeBtn = document.createElement("button");
        removeBtn.type = "button";
        removeBtn.className = "control-button";
        removeBtn.textContent = tr(state.activeLanguage, "gas_laws_remove");
        removeBtn.addEventListener("click", () => row.remove());

        row.append(labelInput, fractionInput, removeBtn);
        return row;
    };

    daltonAddBtn.addEventListener("click", () => {
        daltonRows.appendChild(makeDaltonRow(daltonRows.children.length));
    });
    // Seed two empty rows so the user has something to fill in by default.
    daltonRows.appendChild(makeDaltonRow(0));
    daltonRows.appendChild(makeDaltonRow(1));

    daltonForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const totalField = readGasField("gas-dalton-total", "gas-dalton-total-unit");
        if (totalField.blank || totalField.invalid || totalField.value <= 0) {
            showError("concentration_error_missing_inputs");
            return;
        }
        const rowsEls = Array.from(daltonRows.querySelectorAll(".gas-dalton-row"));
        const entries = [];
        for (const r of rowsEls) {
            const labelInput = r.querySelector("input[data-role='label']");
            const fractionInput = r.querySelector("input[data-role='fraction']");
            const raw = fractionInput.value.trim();
            if (raw === "") continue;
            const fraction = Number(raw);
            if (!Number.isFinite(fraction) || fraction <= 0) {
                showError("gas_laws_error_invalid_fraction");
                return;
            }
            entries.push({ label: labelInput.value.trim() || `${entries.length + 1}`, fraction });
        }
        if (entries.length === 0) {
            showError("concentration_error_missing_inputs");
            return;
        }
        const totalAtm = totalField.value * PRESSURE_TO_ATM[totalField.unit];
        const partialUnit = totalField.unit;
        renderResult(entries.map((e) => ({
            label: `${tr(state.activeLanguage, "gas_laws_dalton_partial_pressure")} — ${e.label}`,
            value: `${formatNumberSmart(
                e.fraction * totalAtm * PRESSURE_FROM_ATM[partialUnit],
            )} ${partialUnit}`,
        })));
    });
}

function setupPhForm() {
    const modeSelect = document.getElementById("ph-mode");
    const interconvertForm = document.getElementById("ph-interconvert-form");
    const strongForm = document.getElementById("ph-strong-form");
    const status = document.getElementById("ph-status");
    const resultWrap = document.getElementById("ph-result");
    const resultList = document.getElementById("ph-result-list");

    const showError = (key) => {
        status.classList.add("is-error");
        status.textContent = tr(state.activeLanguage, key);
        resultWrap.hidden = true;
    };
    const clearStatus = () => {
        status.classList.remove("is-error");
        status.textContent = "";
    };
    const renderResult = (rows) => {
        resultList.replaceChildren();
        for (const { label, value } of rows) {
            const dt = document.createElement("dt");
            dt.textContent = label;
            const dd = document.createElement("dd");
            dd.textContent = value;
            resultList.append(dt, dd);
        }
        resultWrap.hidden = false;
    };

    modeSelect.addEventListener("change", () => {
        clearStatus();
        resultWrap.hidden = true;
        interconvertForm.hidden = modeSelect.value !== "interconvert";
        strongForm.hidden = modeSelect.value !== "strong";
    });

    const formatPh = (value) => value.toFixed(2);
    const formatConc = (value) => {
        if (!Number.isFinite(value) || value <= 0) return "—";
        return value.toExponential(3);
    };

    interconvertForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const phRaw = document.getElementById("ph-input-ph").value.trim();
        const pohRaw = document.getElementById("ph-input-poh").value.trim();
        const hRaw = document.getElementById("ph-input-h").value.trim();
        const ohRaw = document.getElementById("ph-input-oh").value.trim();

        const filled = [phRaw, pohRaw, hRaw, ohRaw].filter((v) => v !== "");
        if (filled.length !== 1) {
            showError("ph_error_multiple_inputs");
            return;
        }

        let ph;
        let poh;
        let hConc;
        let ohConc;
        if (phRaw !== "") {
            ph = Number(phRaw);
            if (!Number.isFinite(ph)) {
                showError("ph_error_invalid_input");
                return;
            }
            poh = 14 - ph;
            hConc = Math.pow(10, -ph);
            ohConc = Math.pow(10, -poh);
        } else if (pohRaw !== "") {
            poh = Number(pohRaw);
            if (!Number.isFinite(poh)) {
                showError("ph_error_invalid_input");
                return;
            }
            ph = 14 - poh;
            hConc = Math.pow(10, -ph);
            ohConc = Math.pow(10, -poh);
        } else if (hRaw !== "") {
            hConc = Number(hRaw);
            if (!Number.isFinite(hConc) || hConc <= 0) {
                showError("ph_error_invalid_input");
                return;
            }
            ph = -Math.log10(hConc);
            poh = 14 - ph;
            ohConc = Math.pow(10, -poh);
        } else {
            ohConc = Number(ohRaw);
            if (!Number.isFinite(ohConc) || ohConc <= 0) {
                showError("ph_error_invalid_input");
                return;
            }
            poh = -Math.log10(ohConc);
            ph = 14 - poh;
            hConc = Math.pow(10, -ph);
        }

        renderResult([
            { label: tr(state.activeLanguage, "ph_value_ph"), value: formatPh(ph) },
            { label: tr(state.activeLanguage, "ph_value_poh"), value: formatPh(poh) },
            { label: tr(state.activeLanguage, "ph_value_h_plus"), value: formatConc(hConc) },
            { label: tr(state.activeLanguage, "ph_value_oh_minus"), value: formatConc(ohConc) },
        ]);
    });

    strongForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearStatus();
        const kind = document.getElementById("ph-strong-kind").value;
        const concRaw = document.getElementById("ph-strong-conc").value.trim();
        const polyRaw = document.getElementById("ph-strong-poly").value.trim();
        const conc = Number(concRaw);
        const poly = polyRaw === "" ? 1 : Number(polyRaw);
        if (!Number.isFinite(conc) || conc <= 0) {
            showError("ph_error_invalid_input");
            return;
        }
        if (!Number.isFinite(poly) || poly < 1) {
            showError("ph_error_invalid_input");
            return;
        }
        const effective = conc * poly;
        let ph;
        let poh;
        let hConc;
        let ohConc;
        if (kind === "acid") {
            hConc = effective;
            ph = -Math.log10(hConc);
            poh = 14 - ph;
            ohConc = Math.pow(10, -poh);
        } else {
            ohConc = effective;
            poh = -Math.log10(ohConc);
            ph = 14 - poh;
            hConc = Math.pow(10, -ph);
        }
        renderResult([
            { label: tr(state.activeLanguage, "ph_value_ph"), value: formatPh(ph) },
            { label: tr(state.activeLanguage, "ph_value_poh"), value: formatPh(poh) },
            { label: tr(state.activeLanguage, "ph_value_h_plus"), value: formatConc(hConc) },
            { label: tr(state.activeLanguage, "ph_value_oh_minus"), value: formatConc(ohConc) },
        ]);
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
    setupStoichForm();
    setupConcentrationForm();
    setupGasLawsForm();
    setupPhForm();
    setupSearchForm();
    setupToolsModal();
    applyStaticTranslations();
    renderPeriodicTable();

    loader.hidden = true;
    document.getElementById("app").hidden = false;

    const preload = () => {
        ensurePyodide().catch((err) =>
            console.warn("Pyodide preload failed", err),
        );
    };
    if (typeof requestIdleCallback === "function") {
        requestIdleCallback(preload);
    } else {
        setTimeout(preload, 0);
    }
}

bootstrap().catch((err) => {
    console.error(err);
    document.getElementById("loader-message").textContent = `Bootstrap failed: ${err.message}`;
});
