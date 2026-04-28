# PyInstaller spec for the Periodic Table Of Elements portable Windows build.
# Produces an onedir layout under dist/PeriodicTableApp/. tools/build_windows.ps1
# copies the folder into dist/release/<bundle>/ and runs a frozen smoke test
# that expects datasets at _internal/data/raw/ and _internal/data/reference/.

from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ["src/main.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("data", "data"),
        ("assets/styles", "assets/styles"),
        ("assets/app.ico", "assets_"),
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
    icon="assets/app.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="PeriodicTableApp",
)
