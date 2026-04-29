Periodic Table Of Elements
Version 1.2.0 "Chemistry Tool"

A desktop periodic table explorer: element details, quick property
trends, electron configuration views, and a simple binary compound
builder.

Requirements
    Windows 10 or later (x64). No installation required; this is a
    portable build.

How to launch
    Double-click PeriodicTableApp.exe. Keep the extracted folder
    intact: the _internal directory next to the executable contains
    the packaged Python runtime and datasets needed at startup.

Runtime logs
    A rotating log file is written by default to:

        %LOCALAPPDATA%\T_P_python\PeriodicTableApp\logs\PeriodicTableApp.log

    Up to three rotated backups are kept alongside it (about
    512 KB per file). To redirect logs, set the
    PERIODIC_TABLE_LOG_ROOT environment variable before launch; the
    file will then be written under

        <PERIODIC_TABLE_LOG_ROOT>\T_P_python\PeriodicTableApp\logs

Included in this bundle
    PeriodicTableApp.exe   application entry point
    _internal\             packaged runtime and datasets
    LICENSE.txt            MIT license terms
    RELEASE_NOTES.md       changes in this release

Uninstall
    Delete the extracted folder. Optional runtime artifacts (logs
    and Qt settings) live under %LOCALAPPDATA%\T_P_python and can
    be removed the same way.
