# PyInstaller spec for the Periodic Table Of Elements portable build.
# Produces an onedir layout under dist/PeriodicTableApp/ on Windows and Linux,
# and a windowed .app bundle on macOS. Per-OS build wrappers
# (tools/build_windows.ps1, tools/build_unix.sh) copy the output into
# dist/release/<bundle>/ and run a frozen smoke test that expects datasets at
# _internal/data/raw/ and _internal/data/reference/.

import sys

from PyInstaller.utils.hooks import collect_submodules

# PyInstaller's icon parameter only accepts .ico on Windows and .icns on macOS;
# on Linux it is ignored. The repo only ships a .ico, so we set the EXE icon
# only on Windows and still bundle the .ico under assets/ for in-app use.
_icon_for_exe = "assets/app.ico" if sys.platform == "win32" else None

a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("data", "data"),
        ("assets/styles", "assets/styles"),
        ("assets/app.ico", "assets"),
    ],
    hiddenimports=collect_submodules("src"),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PeriodicTableApp",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=_icon_for_exe,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PeriodicTableApp",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="PeriodicTableApp.app",
        icon=None,
        bundle_identifier="t_p_python.periodic_table_app",
    )
