#!/usr/bin/env bash
# Cross-platform PyInstaller build wrapper for macOS and Linux. Mirrors the
# behavior of tools/build_windows.ps1: invokes PyInstaller against the shared
# spec, copies the resulting onedir output (or .app bundle on macOS) into
# dist/release/<bundle>/, runs an offscreen smoke launch, and zips the bundle.
#
# Usage:
#   tools/build_unix.sh [--clean] [--python <interpreter>]
#
# The OS suffix appended to the bundle name (mac or linux) is detected from
# uname so the final artifact matches the layout published to GitHub releases.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." >/dev/null 2>&1 && pwd)"

CLEAN=0
PYTHON_EXE="python3"
while [ $# -gt 0 ]; do
    case "$1" in
        --clean)
            CLEAN=1
            shift
            ;;
        --python)
            PYTHON_EXE="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1" >&2
            echo "Usage: $0 [--clean] [--python <interpreter>]" >&2
            exit 2
            ;;
    esac
done

if ! command -v "$PYTHON_EXE" >/dev/null 2>&1; then
    echo "Python interpreter not found: $PYTHON_EXE" >&2
    exit 1
fi

UNAME_S="$(uname -s)"
case "$UNAME_S" in
    Darwin)
        OS_SUFFIX="mac"
        ;;
    Linux)
        OS_SUFFIX="linux"
        ;;
    *)
        echo "Unsupported platform: $UNAME_S (use tools/build_windows.ps1 on Windows)" >&2
        exit 1
        ;;
esac

cd "$REPO_ROOT"

SPEC_PATH="$REPO_ROOT/PeriodicTableApp.spec"
if [ ! -f "$SPEC_PATH" ]; then
    echo "Missing PyInstaller spec file: $SPEC_PATH" >&2
    exit 1
fi

if ! "$PYTHON_EXE" -m PyInstaller --version >/dev/null 2>&1; then
    echo "PyInstaller is not installed. Install build dependencies with:" >&2
    echo "    $PYTHON_EXE -m pip install -r requirements-build.txt" >&2
    exit 1
fi

METADATA_JSON="$("$PYTHON_EXE" -c "from src.app_metadata import get_build_metadata, get_release_bundle_name; import json; m = get_build_metadata(); m['release_bundle_name'] = get_release_bundle_name('$OS_SUFFIX'); print(json.dumps(m))")"

EXEC_NAME="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['executable_name'])" "$METADATA_JSON")"
BUNDLE_NAME="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['release_bundle_name'])" "$METADATA_JSON")"
DISPLAY_NAME="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['display_name'])" "$METADATA_JSON")"
RELEASE_DISPLAY="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['release_display_name'])" "$METADATA_JSON")"
ICON_PRESENT="$("$PYTHON_EXE" -c "import json,sys; print('1' if json.loads(sys.argv[1])['icon_present'] else '0')" "$METADATA_JSON")"
ICON_PATH="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['optional_icon_path'])" "$METADATA_JSON")"
VENDOR="$("$PYTHON_EXE" -c "import json,sys; print(json.loads(sys.argv[1])['vendor'])" "$METADATA_JSON")"

BUILD_DIR="$REPO_ROOT/build"
DIST_DIR="$REPO_ROOT/dist"
RELEASE_ROOT="$DIST_DIR/release"
EXEC_OUTPUT="$DIST_DIR/$EXEC_NAME"
APP_OUTPUT="$DIST_DIR/$EXEC_NAME.app"
RELEASE_FOLDER="$RELEASE_ROOT/$BUNDLE_NAME"
RELEASE_ZIP="$RELEASE_ROOT/$BUNDLE_NAME.zip"
LICENSE_SOURCE="$REPO_ROOT/LICENSE"
RELEASE_NOTES_SOURCE="$REPO_ROOT/RELEASE_NOTES.md"
README_SOURCE="$REPO_ROOT/docs/README_release_${OS_SUFFIX}.txt"

for required in "$LICENSE_SOURCE" "$RELEASE_NOTES_SOURCE" "$README_SOURCE"; do
    if [ ! -f "$required" ]; then
        echo "Missing required file: $required" >&2
        exit 1
    fi
done

if [ "$CLEAN" -eq 1 ]; then
    rm -rf "$BUILD_DIR" "$EXEC_OUTPUT" "$APP_OUTPUT" "$RELEASE_FOLDER" "$RELEASE_ZIP"
fi

mkdir -p "$RELEASE_ROOT"

echo "Building $DISPLAY_NAME $RELEASE_DISPLAY ($OS_SUFFIX)"
"$PYTHON_EXE" -m PyInstaller --clean --noconfirm "$SPEC_PATH"

if [ "$OS_SUFFIX" = "mac" ]; then
    if [ ! -d "$APP_OUTPUT" ]; then
        echo "Expected macOS .app bundle not found: $APP_OUTPUT" >&2
        exit 1
    fi
    rm -rf "$RELEASE_FOLDER"
    mkdir -p "$RELEASE_FOLDER"
    cp -R "$APP_OUTPUT" "$RELEASE_FOLDER/"
    EXECUTABLE_PATH="$RELEASE_FOLDER/$EXEC_NAME.app/Contents/MacOS/$EXEC_NAME"
    INTERNAL_DIR="$RELEASE_FOLDER/$EXEC_NAME.app/Contents/Resources"
    EXECUTABLE_WORKDIR="$RELEASE_FOLDER/$EXEC_NAME.app/Contents/MacOS"
else
    if [ ! -d "$EXEC_OUTPUT" ]; then
        echo "Expected onedir build folder not found: $EXEC_OUTPUT" >&2
        exit 1
    fi
    rm -rf "$RELEASE_FOLDER"
    cp -R "$EXEC_OUTPUT" "$RELEASE_FOLDER"
    EXECUTABLE_PATH="$RELEASE_FOLDER/$EXEC_NAME"
    INTERNAL_DIR="$RELEASE_FOLDER/_internal"
    EXECUTABLE_WORKDIR="$RELEASE_FOLDER"
fi

cp "$README_SOURCE" "$RELEASE_FOLDER/README.txt"
cp "$LICENSE_SOURCE" "$RELEASE_FOLDER/LICENSE.txt"
cp "$RELEASE_NOTES_SOURCE" "$RELEASE_FOLDER/RELEASE_NOTES.md"

for required in \
    "$EXECUTABLE_PATH" \
    "$INTERNAL_DIR/data/raw/elements.json" \
    "$INTERNAL_DIR/data/reference/nomenclature_data.json" \
; do
    if [ ! -e "$required" ]; then
        echo "Release verification failed, missing: $required" >&2
        exit 1
    fi
done

if [ "$ICON_PRESENT" = "1" ]; then
    if [ ! -f "$INTERNAL_DIR/assets/app.ico" ]; then
        echo "Release verification failed, missing bundled icon at $INTERNAL_DIR/assets/app.ico" >&2
        exit 1
    fi
fi

SMOKE_ROOT="$REPO_ROOT/.test_runtime/frozen_smoke"
rm -rf "$SMOKE_ROOT"
mkdir -p "$SMOKE_ROOT"

if [ ! -x "$EXECUTABLE_PATH" ]; then
    chmod +x "$EXECUTABLE_PATH" || true
fi

echo "Running offscreen smoke launch: $EXECUTABLE_PATH"
(
    cd "$EXECUTABLE_WORKDIR"
    QT_QPA_PLATFORM=offscreen \
    PERIODIC_TABLE_SMOKE_EXIT_MS=1500 \
    PERIODIC_TABLE_LOG_ROOT="$SMOKE_ROOT" \
    "$EXECUTABLE_PATH"
)

SMOKE_LOG="$SMOKE_ROOT/$VENDOR/$EXEC_NAME/logs/$EXEC_NAME.log"
if [ ! -f "$SMOKE_LOG" ]; then
    echo "Frozen smoke log not produced at $SMOKE_LOG" >&2
    exit 1
fi
echo "Frozen smoke launch passed: $EXECUTABLE_PATH"

rm -f "$RELEASE_ZIP"
(
    cd "$RELEASE_ROOT"
    if command -v zip >/dev/null 2>&1; then
        zip -r -q "$BUNDLE_NAME.zip" "$BUNDLE_NAME"
    else
        "$PYTHON_EXE" -c "import shutil, sys; shutil.make_archive(sys.argv[1], 'zip', root_dir='.', base_dir=sys.argv[2])" "$BUNDLE_NAME" "$BUNDLE_NAME"
    fi
)

if [ ! -f "$RELEASE_ZIP" ]; then
    echo "Failed to produce release zip: $RELEASE_ZIP" >&2
    exit 1
fi

echo "Release folder: $RELEASE_FOLDER"
echo "Release zip:    $RELEASE_ZIP"

if [ "$ICON_PRESENT" != "1" ]; then
    echo "Warning: optional icon not found at $ICON_PATH; default PyInstaller icon was used." >&2
fi
