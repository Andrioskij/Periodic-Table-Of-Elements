Periodic Table Of Elements
Version 1.2.0 "Chemistry Tool"

A desktop periodic table explorer: element details, quick property
trends, electron configuration views, and a simple binary compound
builder.

Requirements
    A modern x86_64 Linux distribution with glibc >= 2.31 (e.g.
    Ubuntu 22.04 or later). The frozen Qt binaries depend on a few
    system libraries available on most desktops:

        libegl1 libxkbcommon0 libxcb-cursor0 libdbus-1-3

    No installation required; this is a portable folder.

How to launch
    From the extracted folder run:

        ./PeriodicTableApp

    Keep the extracted folder intact: the _internal directory next
    to the executable contains the packaged Python runtime and
    datasets needed at startup.

Runtime logs
    A rotating log file is written by default to:

        ~/.local/share/T_P_python/PeriodicTableApp/logs/PeriodicTableApp.log

    Up to three rotated backups are kept alongside it (about
    512 KB per file). To redirect logs, set the
    PERIODIC_TABLE_LOG_ROOT environment variable before launch.

Included in this bundle
    PeriodicTableApp       application entry point
    _internal/             packaged runtime and datasets
    LICENSE.txt            MIT license terms
    RELEASE_NOTES.md       changes in this release

Uninstall
    Delete the extracted folder. Optional runtime artifacts (logs
    and Qt settings) live under ~/.local/share/T_P_python and
    ~/.config/T_P_python.
