# AUR package: `periodic-table-app-bin`

Files in this directory are the source for the
[`periodic-table-app-bin`](https://aur.archlinux.org/packages/periodic-table-app-bin)
AUR package, which installs the prebuilt Linux portable bundle from a
GitHub release.

## Files

| File | Purpose |
| ---- | ------- |
| `PKGBUILD` | Build recipe consumed by `makepkg`. |
| `.SRCINFO` | Machine-readable metadata regenerated from `PKGBUILD`. |
| `periodic-table-app.desktop` | Freedesktop entry installed under `/usr/share/applications/`. |
| `periodic-table-app.png` | 256x256 PNG icon installed under `/usr/share/icons/hicolor/256x256/apps/`. |

## What the package does

- Downloads the published Linux zip from the GitHub release matching `pkgver`.
- Installs the unpacked bundle to `/opt/periodic-table-app-bin/`.
- Symlinks `/usr/bin/periodic-table-app` to the bundled `PeriodicTableApp`
  executable.
- Installs a `.desktop` file and PNG icon so the app shows up in standard
  application menus.
- Installs the bundled `LICENSE.txt` to `/usr/share/licenses/periodic-table-app-bin/`.

PyInstaller bundles ship their own Python runtime and Qt libraries, so the
package declares no `depends`. End users only need the standard graphical
session libraries they already have.

## How to publish (first-time setup)

The AUR is git-backed. Each AUR package has its own git remote at
`ssh://aur@aur.archlinux.org/<pkgname>.git`. To publish:

1. Create an AUR account at https://aur.archlinux.org and add an SSH key.
2. Clone the (initially empty) AUR repo:
   ```bash
   git clone ssh://aur@aur.archlinux.org/periodic-table-app-bin.git
   cd periodic-table-app-bin
   ```
3. Copy the four files from this directory into the clone:
   ```bash
   cp /path/to/repo/packaging/aur/PKGBUILD .
   cp /path/to/repo/packaging/aur/.SRCINFO .
   cp /path/to/repo/packaging/aur/periodic-table-app.desktop .
   cp /path/to/repo/packaging/aur/periodic-table-app.png .
   ```
4. Validate locally on an Arch system:
   ```bash
   namcap PKGBUILD
   makepkg --printsrcinfo > .SRCINFO   # confirm it matches the committed file
   makepkg -si                          # builds and installs into a clean chroot
   ```
5. Commit and push:
   ```bash
   git add PKGBUILD .SRCINFO periodic-table-app.desktop periodic-table-app.png
   git commit -m "Initial import: periodic-table-app-bin 1.2.0"
   git push
   ```

## How to update on a new release

Each new upstream release (`vX.Y.Z`) requires:

1. Bump `pkgver` in `PKGBUILD` to `X.Y.Z` and reset `pkgrel=1`.
2. Update the first entry in `sha256sums=()` with the new SHA-256 of the
   Linux zip published by the matrix release workflow. The published zip
   name follows
   `PeriodicTableApp-<version>-chemistry-tool-linux.zip`.
   Compute the hash from the GitHub release asset:
   ```bash
   curl -sL "https://github.com/Andrioskij/Periodic-Table-Of-Elements/releases/download/vX.Y.Z/PeriodicTableApp-X.Y.Z-chemistry-tool-linux.zip" \
       | sha256sum
   ```
3. Regenerate `.SRCINFO`:
   ```bash
   makepkg --printsrcinfo > .SRCINFO
   ```
4. Sync the four files into the AUR clone (same as steps 3-5 above) and push.
   Use a commit message like `Update to X.Y.Z`.

## Notes

- The `.png` icon shipped here is a copy of `assets/app_256.png` from the
  upstream repo. Keep them in sync if the icon changes.
- The PyInstaller bundle ships its own Qt libraries, so PKGBUILD does not
  list `qt6-base` as a dependency. The bundle still requires the graphical
  stack provided by a standard Arch desktop session.
- `options=('!strip')` is set because PyInstaller bundles include
  pre-stripped third-party shared objects; running `strip` again can break
  them.
