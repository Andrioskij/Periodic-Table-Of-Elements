# Periodic Table Of Elements

Release target: `1.2.0 "Chemistry Tool"`

PySide6 desktop app for exploring the periodic table, quick trends, electron configuration, and compound nomenclature.

This GitHub repository is meant to host the source code and project documentation.
Each release publishes three portable zips as GitHub release assets — Windows (`...-win.zip`), macOS (`...-mac.zip`), and Linux (`...-linux.zip`) — produced respectively by `tools/build_windows.ps1` and `tools/build_unix.sh`. Binaries are not committed to the repository. No installer, code signing, or notarization is in scope for this delivery model.
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

## Building portable bundles

This repo uses a conservative `PyInstaller` setup. `PyInstaller` is not a runtime dependency; it is declared only in `requirements-build.txt`. Both build wrappers consume the same `PeriodicTableApp.spec` and run an offscreen smoke launch against the frozen executable before zipping the bundle.

Install the build dependency set:

```bash
python -m pip install -r requirements-build.txt
```

### Windows

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean
```

To pin the build to a specific local venv without activating it first, the script also accepts an explicit interpreter:

```powershell
powershell -ExecutionPolicy Bypass -File tools/build_windows.ps1 -Clean -PythonExe .\.venv\Scripts\python.exe
```

Expected output: `dist/release/PeriodicTableApp-1.2.0-chemistry-tool-win.zip`.

### macOS and Linux

```bash
bash tools/build_unix.sh --clean
```

The OS suffix (`mac` or `linux`) is detected from `uname`, so the same script produces a `.app` bundle on macOS and an onedir folder on Linux. Outputs:

- macOS: `dist/release/PeriodicTableApp-1.2.0-chemistry-tool-mac.zip` (contains `PeriodicTableApp.app`, unsigned)
- Linux: `dist/release/PeriodicTableApp-1.2.0-chemistry-tool-linux.zip`

On Linux, the smoke launch needs the same Qt offscreen system libraries used by CI: `libegl1 libxkbcommon0 libxcb-cursor0 libdbus-1-3`.

### Release-asset delivery

Each release published from CI ships all three zips. End users do not need an installer for this delivery model: they extract the zip, keep the extracted folder together, and remove the app later by deleting that folder. The release folder also bundles a per-OS `README.txt`, a `LICENSE.txt`, and `RELEASE_NOTES.md`. For portfolio publication, keep generated `dist/` outputs out of the repository and distribute only the portable zips through the GitHub release assets.

## License

This project is released under the MIT license. See `LICENSE` for details.

See [CHANGELOG.md](CHANGELOG.md) for the full version history.
