# Periodic Table — Browser Version

Browser version of the desktop Periodic Table app, built with
[Reflex](https://reflex.dev) (Python that compiles to a React frontend
backed by a FastAPI/Granian Python backend).

This is a separate, independently runnable project that **shares the
desktop app's domain and data layers** as a single source of truth — no
file is duplicated.

## Status

Batch 7 closed (interactivity layer). Currently shipping:

- Click an element → highlight + element-detail card on the right.
- Search box filters cells by name, symbol, or atomic number — non-
  matches fade to 25 % opacity, the active selection still keeps its
  yellow border.
- Trend recoloring: switch between **Default** (category palette),
  **Radius**, **Ionization**, **Electron Affinity**,
  **Electronegativity**, **Metallic**, and **Nonmetallic**. Numeric
  trends interpolate a two-color gradient over the dataset min/max.
- Responsive layout: on viewports below `lg`, the info card stacks
  below the table; above, it sits on the right.

Still missing in this batch (intentionally — see roadmap below):
electron configuration / Lewis diagrams (Batch 8), tool area for
molar mass / stoichiometry / compound builder (Batch 9), and
i18n / theme switcher / deploy build (Batch 10).

![Periodic table with element selected](../assets/screenshots/web-batch7.png)

## Prerequisites

- Python 3.14 (the same version the desktop app targets).
- Node.js LTS installed on your system. Reflex uses [Bun](https://bun.sh)
  for the JS toolchain and downloads it automatically on the first
  `reflex init`/`reflex run`.

## Setup

From the repository root:

```bash
cd web
python -m venv .venv

# Windows (Git Bash):
.venv/Scripts/python.exe -m pip install -r requirements.txt

# macOS / Linux:
.venv/bin/python -m pip install -r requirements.txt
```

The desktop project uses its own venv at the repository root
(`/.venv/`); keep the browser venv (`web/.venv/`) separate to avoid
PySide6 vs. Reflex dependency conflicts.

## Run the dev server

```bash
cd web
.venv/Scripts/reflex.exe run        # Windows (Git Bash)
# or
.venv/bin/reflex run                # macOS / Linux
```

Reflex starts:
- the frontend on http://localhost:3000
- the FastAPI/Granian backend on http://localhost:8000

Open http://localhost:3000 in a browser. The first start compiles the
React bundle and may take a minute; subsequent starts are fast.

## Folder layout

```
web/
├── .venv/                       # virtualenv (gitignored)
├── .web/                        # Reflex/React build artifacts (gitignored)
├── assets/                      # static assets served by the frontend
├── periodic_table_web/
│   ├── __init__.py              # adds repo root to sys.path
│   ├── periodic_table_web.py    # Reflex App, index page, UI components
│   ├── state.py                 # rx.State (selection, search, trend)
│   ├── trends.py                # trend color helpers (lerp, gradients)
│   └── theme.py                 # palette / colors
├── requirements.txt             # pinned to reflex==0.9.1
├── rxconfig.py                  # Reflex project configuration
└── README.md
```

## Single source of truth

`web/periodic_table_web/__init__.py` inserts the repository root into
`sys.path` so the Reflex app can import:

- `src.services.data_loader` — JSON loaders for `data/raw/elements.json`
  and friends.
- `src.domain.*` — pure-Python parsers and chemistry logic.

`src.ui.*` is **never imported** from the web app: it depends on
PySide6, which has no place in the Reflex runtime.

When the desktop app's data files change, the browser version picks
them up automatically — no sync step.

## Roadmap

- **Batch 6 — done** — project scaffolding, static periodic table
  grid, color-coded by category.
- **Batch 7 — done (this batch)** — element selection, info card,
  search box, trend recoloring (Default / Radius / Ionization /
  Electron Affinity / Electronegativity / Metallic / Nonmetallic),
  responsive layout.
- **Batch 8** — alternate right-panel views: electron configuration
  (orbital diagram with ↑↓ arrows) and Lewis structures, with a
  toggle at the top of the panel (Info / Electron config / Lewis).
- **Batch 9** — tool area: molar mass, stoichiometry, compound builder,
  solubility lookup.
- **Batch 10** — i18n (the 7 desktop locales), theme switcher, and a
  deployable build (Docker / Reflex Hosting).
