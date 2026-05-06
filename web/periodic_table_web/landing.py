"""Landing page for the public web app.

Greets first-time visitors and sends them either to ``/table`` or to
the matching desktop installer on GitHub Releases. The landing is
mounted at ``/``; the table component (formerly at ``/``) is now at
``/table``.

Download URLs are built from :mod:`src.app_metadata` so the page
inherits the desktop's pinned version automatically — no GitHub API
call at request time, no CORS surface area, no rate limit. The URL
template points at a specific release tag (``releases/download/vX.Y.Z``)
rather than the floating ``releases/latest/download`` redirect, because
the asset filename embeds the version too: linking to a stable
filename at the floating tag still 404s once the version bumps. When
the desktop bumps, the web rebuild picks the new version up.

OS detection: a one-shot script reads ``navigator.userAgent`` /
``platform`` on mount and pushes the verdict into :class:`LandingState`
via ``rx.call_script``. Failure mode is benign — if the script never
reports back, ``os_kind`` stays ``"unknown"`` and all three download
links are shown side-by-side. Mobile is detected via the same script;
when true, the download CTAs are replaced with a brief note steering
the visitor to the in-browser version.
"""

from __future__ import annotations

import reflex as rx

from periodic_table_web.i18n import TranslationState
from periodic_table_web.nav import header as nav_header
from periodic_table_web.theme import UI_FONT_FAMILY
from periodic_table_web.theme_state import ThemeState
from src.app_metadata import APP_VERSION, get_release_bundle_name

REPO_URL = "https://github.com/Andrioskij/Periodic-Table-Of-Elements"
RELEASE_TAG = f"v{APP_VERSION}"
RELEASES_PAGE_URL = f"{REPO_URL}/releases/latest"


def _download_url(os_suffix: str) -> str:
    """Return the pinned GitHub release asset URL for ``os_suffix``."""
    name = get_release_bundle_name(os_suffix)
    return f"{REPO_URL}/releases/download/{RELEASE_TAG}/{name}.zip"


DOWNLOAD_LINKS: dict[str, str] = {
    "win": _download_url("win"),
    "mac": _download_url("mac"),
    "linux": _download_url("linux"),
}


_OS_DETECT_SCRIPT = """
(function() {
  try {
    const ua = (navigator.userAgent || "").toLowerCase();
    const platform = (navigator.platform || "").toLowerCase();
    const mobileRe = /android|iphone|ipad|ipod|windows phone|mobile/;
    if (mobileRe.test(ua)) return "mobile";
    if (ua.includes("mac") || platform.includes("mac")) return "mac";
    if (ua.includes("win") || platform.includes("win")) return "win";
    if (ua.includes("linux") || platform.includes("linux")) return "linux";
  } catch (err) {}
  return "unknown";
})()
"""


class LandingState(rx.State):
    """Detected operating system for the active visitor.

    ``os_kind`` is one of ``win`` / ``mac`` / ``linux`` / ``mobile`` /
    ``unknown``. Set once on mount via :data:`_OS_DETECT_SCRIPT`; if
    JavaScript is disabled or the UA string is not recognised, it
    stays ``unknown`` and the page shows all three desktop links.
    """

    os_kind: str = "unknown"

    @rx.event
    def detect_os(self) -> rx.event.EventSpec:
        return rx.call_script(_OS_DETECT_SCRIPT, callback=LandingState.set_os_kind)

    @rx.event
    def set_os_kind(self, value: str) -> None:
        if value in {"win", "mac", "linux", "mobile"}:
            self.os_kind = value

    @rx.var(cache=True)
    def is_mobile(self) -> bool:
        return self.os_kind == "mobile"

    @rx.var(cache=True)
    def primary_os(self) -> str:
        return self.os_kind if self.os_kind in {"win", "mac", "linux"} else ""


def _open_browser_button() -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.text(
                TranslationState.t["landing_open_browser_cta"],
                font_size="1rem",
                font_weight="700",
            ),
            rx.text("→", font_size="1.1rem"),
            spacing="2",
            align="center",
        ),
        href="/table",
        background=ThemeState.colors["accent_active"],
        color=ThemeState.colors["cell_text"],
        padding="14px 22px",
        border_radius="10px",
        text_decoration="none",
        cursor="pointer",
        _hover={"filter": "brightness(1.1)"},
    )


def _download_button(os_suffix: str, label_key: str, *, primary: bool) -> rx.Component:
    """Pinned-version download link for one of win/mac/linux."""
    bg = (
        ThemeState.colors["accent_active"]
        if primary
        else ThemeState.colors["accent_inactive"]
    )
    color = (
        ThemeState.colors["cell_text"]
        if primary
        else ThemeState.colors["foreground"]
    )
    return rx.link(
        rx.text(
            TranslationState.t[label_key],
            font_size="0.95rem" if primary else "0.85rem",
            font_weight="700" if primary else "600",
        ),
        href=DOWNLOAD_LINKS[os_suffix],
        background=bg,
        color=color,
        padding="12px 18px" if primary else "10px 14px",
        border="1px solid " + ThemeState.colors["border"],
        border_radius="10px",
        text_decoration="none",
        cursor="pointer",
        _hover={"filter": "brightness(1.1)"},
    )


def _download_section() -> rx.Component:
    """Cluster of OS-aware download CTAs.

    On mobile, replaced by a single short note. On desktop, the
    detected OS gets the primary button and the other two render as
    secondary links beneath it. When detection has not yet run (or
    failed), all three are shown as primary side-by-side.
    """
    return rx.cond(
        LandingState.is_mobile,
        rx.text(
            TranslationState.t["landing_mobile_note"],
            color=ThemeState.colors["text_muted"],
            font_size="0.85rem",
            max_width="42ch",
        ),
        rx.vstack(
            rx.match(
                LandingState.os_kind,
                ("win", _download_button("win", "landing_download_label_win", primary=True)),
                ("mac", _download_button("mac", "landing_download_label_mac", primary=True)),
                ("linux", _download_button("linux", "landing_download_label_linux", primary=True)),
                rx.hstack(
                    _download_button("win", "landing_download_label_win", primary=True),
                    _download_button("mac", "landing_download_label_mac", primary=True),
                    _download_button("linux", "landing_download_label_linux", primary=True),
                    spacing="2",
                    flex_wrap="wrap",
                ),
            ),
            rx.cond(
                LandingState.primary_os != "",
                rx.hstack(
                    rx.cond(
                        LandingState.os_kind != "win",
                        _download_button("win", "landing_download_label_win", primary=False),
                    ),
                    rx.cond(
                        LandingState.os_kind != "mac",
                        _download_button("mac", "landing_download_label_mac", primary=False),
                    ),
                    rx.cond(
                        LandingState.os_kind != "linux",
                        _download_button("linux", "landing_download_label_linux", primary=False),
                    ),
                    spacing="2",
                    flex_wrap="wrap",
                ),
            ),
            rx.text(
                TranslationState.t["landing_download_caption"].to(str)
                + " "
                + RELEASE_TAG,
                color=ThemeState.colors["text_muted"],
                font_size="0.78rem",
            ),
            spacing="2",
            align="start",
        ),
    )


def _hero() -> rx.Component:
    return rx.vstack(
        rx.heading(
            TranslationState.t["landing_hero_title"],
            size="9",
            color=ThemeState.colors["foreground"],
            line_height="1.05",
            margin_bottom="0.5rem",
        ),
        rx.text(
            TranslationState.t["landing_hero_subtitle"],
            color=ThemeState.colors["text_muted"],
            font_size="1.05rem",
            max_width="56ch",
            margin_bottom="1.5rem",
        ),
        rx.hstack(
            _open_browser_button(),
            spacing="3",
            align="center",
            flex_wrap="wrap",
            margin_bottom="1.25rem",
        ),
        _download_section(),
        spacing="2",
        align="start",
        width="100%",
    )


def _feature_card(title_key: str, body_key: str) -> rx.Component:
    return rx.vstack(
        rx.text(
            TranslationState.t[title_key],
            font_size="1rem",
            font_weight="700",
            color=ThemeState.colors["foreground"],
        ),
        rx.text(
            TranslationState.t[body_key],
            font_size="0.85rem",
            color=ThemeState.colors["text_muted"],
            line_height="1.45",
        ),
        background=ThemeState.colors["panel"],
        border="1px solid " + ThemeState.colors["border"],
        border_radius="12px",
        padding="16px",
        spacing="2",
        align="start",
        width="100%",
        height="100%",
    )


def _features() -> rx.Component:
    return rx.vstack(
        rx.heading(
            TranslationState.t["landing_features_heading"],
            size="5",
            color=ThemeState.colors["foreground"],
            margin_bottom="0.5rem",
        ),
        rx.grid(
            _feature_card("landing_feature_table_title", "landing_feature_table_desc"),
            _feature_card("landing_feature_tools_title", "landing_feature_tools_desc"),
            _feature_card("landing_feature_i18n_title", "landing_feature_i18n_desc"),
            _feature_card("landing_feature_theme_title", "landing_feature_theme_desc"),
            columns={"base": "1", "md": "2"},
            spacing="3",
            width="100%",
        ),
        spacing="3",
        align="start",
        width="100%",
        margin_top="3rem",
    )


def _footer() -> rx.Component:
    return rx.hstack(
        rx.link(
            TranslationState.t["landing_footer_repo"],
            href=REPO_URL,
            color=ThemeState.colors["text_muted"],
            font_size="0.8rem",
            text_decoration="underline",
        ),
        rx.spacer(),
        rx.text(
            TranslationState.t["landing_footer_built_with"],
            color=ThemeState.colors["text_muted"],
            font_size="0.8rem",
        ),
        width="100%",
        margin_top="3rem",
        padding_top="1.25rem",
        border_top="1px solid " + ThemeState.colors["divider"],
    )


def landing_page() -> rx.Component:
    """Render the ``/`` landing route."""
    return rx.box(
        rx.vstack(
            nav_header("home"),
            _hero(),
            _features(),
            _footer(),
            spacing="2",
            align="stretch",
            width="100%",
            max_width="1100px",
            margin="0 auto",
        ),
        on_mount=LandingState.detect_os,
        background=ThemeState.colors["background"],
        min_height="100vh",
        padding="1.5rem 1.25rem 2rem",
        color=ThemeState.colors["foreground"],
        font_family=UI_FONT_FAMILY,
    )
