// Web-side localization mirroring src/services/localization_service.tr().
//
// Loads the same JSON files served from data/localization/ and exposes
// a small `tr(code, key, params)` API. English is fetched eagerly as the
// fallback, the requested language on demand. Placeholders use Python-style
// {name} interpolation so existing strings work verbatim.

const SUPPORTED_LANGUAGES = [
    { code: "en", label: "English" },
    { code: "it", label: "Italiano" },
    { code: "es", label: "Español" },
    { code: "fr", label: "Français" },
    { code: "de", label: "Deutsch" },
    { code: "zh", label: "中文（简体）" },
    { code: "ru", label: "Русский" },
];

const cache = new Map();

async function loadLanguage(code) {
    if (cache.has(code)) return cache.get(code);
    const response = await fetch(`./data/localization/${code}.json`);
    if (!response.ok) {
        throw new Error(`Failed to load localization '${code}': HTTP ${response.status}`);
    }
    const data = await response.json();
    cache.set(code, data);
    return data;
}

function format(template, params) {
    if (!params) return template;
    return template.replace(/\{(\w+)\}/g, (match, key) =>
        Object.prototype.hasOwnProperty.call(params, key) ? String(params[key]) : match
    );
}

function tr(code, key, params) {
    const primary = cache.get(code);
    const fallback = cache.get("en");
    const text =
        (primary && primary.ui_texts && primary.ui_texts[key]) ??
        (fallback && fallback.ui_texts && fallback.ui_texts[key]) ??
        key;
    return format(text, params);
}

function getCategoryText(code, category) {
    const primary = cache.get(code);
    const fallback = cache.get("en");
    return (
        (primary && primary.localized_category_texts && primary.localized_category_texts[category]) ??
        (fallback && fallback.localized_category_texts && fallback.localized_category_texts[category]) ??
        category
    );
}

function getStandardStateText(code, state) {
    const primary = cache.get(code);
    const fallback = cache.get("en");
    return (
        (primary && primary.localized_standard_state_texts && primary.localized_standard_state_texts[state]) ??
        (fallback && fallback.localized_standard_state_texts && fallback.localized_standard_state_texts[state]) ??
        state
    );
}

export {
    SUPPORTED_LANGUAGES,
    loadLanguage,
    tr,
    getCategoryText,
    getStandardStateText,
};
