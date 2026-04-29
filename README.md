# Periodic Table Of Elements

Release target: `1.1.0 "Chemistry Tool"`

PySide6 desktop app for exploring the periodic table, quick trends, electron configuration, and compound nomenclature.

This GitHub repository is meant to host the source code and project documentation.
Current Windows delivery choice: the project ships the portable zip produced by `tools/build_windows.ps1`. The Windows binary should be published only as a GitHub release asset, not committed to the repository. No installer is planned in this scope, and code signing remains out of scope.
License: `MIT`.

## Environment setup

Validated local baseline for this repo:

- Python `3.14` 64-bit
- `PySide6==6.11.0` for runtime and tests
- `PyInstaller==6.19.0` for Windows packaging

Recommended Windows setup from the repo root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If `Activate.ps1` is blocked by the local PowerShell execution policy, keep using the venv by calling `.\.venv\Scripts\python.exe` directly in the commands below.

## Quick start

Install the runtime dependency set and run the public entry point:

```powershell
python -m pip install -r requirements.txt
```

```powershell
python -m src.main
```

The runtime requirement file is intentionally minimal and currently contains only the dependency needed to execute the app from source.

## Tests

Install the test environment and run the suite:

```powershell
python -m pip install -r requirements-test.txt
```

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

`requirements-test.txt` currently reuses the runtime dependency set because the tests use `unittest` from the Python standard library and do not need extra third-party packages.

## Using the app

- Use the search box to find an element by name, symbol, or atomic number. `Ctrl+F` moves focus there instantly.
- Use the trend buttons to recolor the table and compare quick patterns such as electronegativity, radius, or metallic character.
- Use `Ctrl+1`, `Ctrl+2`, and `Ctrl+3` to switch the right panel between element info, electron configuration, and compound output.
- Verified UI languages currently exposed in the app are `en`, `it`, `es`, `fr`, `de`, `zh` (Simplified Chinese), and `ru`.
- Build a compound by selecting two elements, choosing oxidation states, and pressing `Calculate formula`. The current builder is intentionally limited to simple binary compounds. `Ctrl+L` resets it.
- Hover the primary controls for short hints while learning the main flows.

## Windows build

This repo uses a conservative `PyInstaller` setup. `PyInstaller` is not a runtime dependency; it is declared only in `requirements-build.txt`.

1. install the build dependency set:

```powershell
python -m pip install -r requirements-build.txt
```

2. build from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean
```

If you want to pin the build to a specific local venv without activating it first, the script also accepts an explicit interpreter:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean -PythonExe .\.venv\Scripts\python.exe
```

Expected outputs:

- `dist/PeriodicTableApp/`
- `dist/release/PeriodicTableApp-1.1.0-chemistry-tool/`
- `dist/release/PeriodicTableApp-1.1.0-chemistry-tool.zip`

For portfolio publication, keep those generated `dist/` outputs out of the repository and distribute only the portable zip through the GitHub release assets.
End users do not need an installer for this delivery model: they extract the zip, keep the extracted folder together, and remove the app later by deleting that folder.

The repo already includes `assets/app.ico` and the build script now performs a conservative post-build smoke on the copied release folder: it verifies the packaged datasets and icon, launches the frozen executable with `QT_QPA_PLATFORM=offscreen`, and expects a clean auto-exit.
The release folder now also includes a user-facing `README.txt`, a `LICENSE.txt`, and `RELEASE_NOTES.md` so the portable bundle can be delivered without depending on the repo checkout.

## License

This project is released under the MIT license. See `LICENSE` for details.

See [CHANGELOG.md](CHANGELOG.md) for the full version history.
