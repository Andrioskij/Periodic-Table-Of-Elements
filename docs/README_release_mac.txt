Periodic Table Of Elements
Version 1.2.0 "Chemistry Tool"

A desktop periodic table explorer: element details, quick property
trends, electron configuration views, and a simple binary compound
builder.

Requirements
    macOS 11 or later (universal x86_64/arm64 not provided; the
    bundle matches the architecture of the build runner). No
    installation required; this is a portable .app bundle.

How to launch
    Drag PeriodicTableApp.app to Applications, or just double-click
    it from the extracted folder. The bundle is unsigned, so on the
    first run macOS Gatekeeper may block it: open System Settings >
    Privacy & Security and click "Open Anyway", or right-click the
    .app and choose "Open" from the context menu.

Runtime logs
    A rotating log file is written by default to:

        ~/Library/Application Support/T_P_python/PeriodicTableApp/logs/PeriodicTableApp.log

    Up to three rotated backups are kept alongside it (about
    512 KB per file). To redirect logs, set the
    PERIODIC_TABLE_LOG_ROOT environment variable before launch.

Included in this bundle
    PeriodicTableApp.app   application bundle
    LICENSE.txt            MIT license terms
    RELEASE_NOTES.md       changes in this release

Uninstall
    Delete PeriodicTableApp.app and the optional runtime artifacts
    under ~/Library/Application Support/T_P_python.
