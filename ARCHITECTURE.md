# Architecture

## Layer rules

```
config  ─▶ domain  ─▶ services  ─▶ ui
   ▲          ▲           ▲         │
   └──────────┴───────────┴── No back-edges. ────┘
```

- `config/` and `domain/` are pure-Python and **must not** import `PySide6` or read files.
- `services/` performs I/O (JSON load, QSettings) and is allowed to import `domain` and `config`.
- `ui/` is the only layer allowed to import `PySide6.QtWidgets`/`QtGui`/`QtCore`.
- The exception: `services/settings_service.py` imports `PySide6.QtCore.QSettings` deliberately — this is the only PySide6 dependency outside `ui/`.

A change that adds a `PySide6` import in `domain/` or `config/` should be rejected on review.

## Patterns in use

### Builder
`src/ui/main_window_builder.py` exposes pure functions (`build_search_widget`,
`build_trend_controls`, `build_right_panel_area`, …) that return dictionaries
of widgets. They are **stateless** and **don't reference `MainWindow`**, which
makes them trivial to unit-test and to compose differently.

### Manager (state outside MainWindow)
`src/ui/managers/{search,trend,compound_builder}_manager.py` hold mutable
state (current search matches, active trend mode, selected element pair). The
`MainWindow` reads/writes these managers instead of growing more attributes.
**New cross-widget state should land in a manager, not in `MainWindow`.**

### Context (lightweight DI)
`src/ui/context.AppContext` is a frozen-ish dataclass with `elements`,
`nomenclature_data`, `settings_service`, and the three managers. `MainWindow`
takes a single `context: AppContext` instead of a long argument list.

### Panel
`src/ui/panels/*` are self-contained QWidgets with their own state and tests
under `tests/ui/`. New right-side features should be a new panel + a new
right-panel mode in `src/services/settings_service.VALID_RIGHT_PANEL_MODES`.

## Data flow at startup

```
data/raw/elements.json        ─┐
data/reference/*.json         ─┼─▶ services.data_loader  ─▶ AppContext  ─▶ Managers ─▶ MainWindow ─▶ Widgets
data/localization/<lang>.json ─┘                                                        ▲
                                                                                        │
                                                                            services.localization_service.tr()
```

`tr()` is **lazy**: each language JSON is loaded on first access, not at startup.

## Where to add new things

| Adding…                         | Goes into…                                          |
| ------------------------------- | --------------------------------------------------- |
| A new pure formula/parser       | `src/domain/<name>.py` + `tests/test_<name>.py`     |
| A new external dataset          | `data/reference/<name>.json` + loader in `src/services/<name>.py` |
| A new right-side panel          | `src/ui/panels/<name>_panel.py` + `tests/ui/test_<name>_panel.py` |
| A new trend overlay             | New mode in `src/config/static_data.NUMERIC_TREND_PROPERTIES` + UI button + `TrendManager` handling |
| A new keyboard shortcut         | `src/ui/main_window.py::_configure_focus_and_shortcuts` |
| A new localized string          | All 7 files under `data/localization/`              |

## Known sharp edges
- `src/ui/main_window.py` is ~1,500 LOC and the obvious refactor target.
- `src/main.py` re-exports ~40 symbols as a "compatibility facade"; do not extend it.
- `assert` on duplicate atomic numbers in `MainWindow.__init__` is stripped under `-O`.
