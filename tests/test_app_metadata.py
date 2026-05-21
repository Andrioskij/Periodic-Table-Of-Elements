import tomllib
import unittest
from pathlib import Path

from src.app_metadata import (
    APP_VERSION,
    build_window_title,
    get_build_metadata,
    get_release_bundle_name,
    get_release_display_name,
    get_release_slug,
)


class TestAppMetadata(unittest.TestCase):

    def test_version_format(self):
        parts = APP_VERSION.split(".")
        self.assertGreaterEqual(len(parts), 3)

    def test_release_display_name_contains_version(self):
        name = get_release_display_name()
        self.assertIn(APP_VERSION, name)

    def test_window_title_contains_version(self):
        title = build_window_title("Periodic Table Of Elements")
        self.assertIn(APP_VERSION, title)
        self.assertIn("Periodic Table Of Elements", title)

    def test_release_slug_lowercase_no_spaces(self):
        slug = get_release_slug()
        self.assertEqual(slug, slug.lower())
        self.assertNotIn(" ", slug)

    def test_bundle_name_contains_version_and_slug(self):
        name = get_release_bundle_name()
        self.assertIn(APP_VERSION, name)
        self.assertIn(get_release_slug(), name)

    def test_bundle_name_with_os_suffix_appends_suffix(self):
        for suffix in ("win", "mac", "linux"):
            with self.subTest(suffix=suffix):
                name = get_release_bundle_name(suffix)
                self.assertTrue(name.endswith(f"-{suffix}"))
                self.assertIn(APP_VERSION, name)
                self.assertIn(get_release_slug(), name)

    def test_bundle_name_no_suffix_when_none(self):
        self.assertEqual(get_release_bundle_name(), get_release_bundle_name(None))

    def test_build_metadata_keys(self):
        meta = get_build_metadata()
        expected_keys = {"app_id", "display_name", "executable_name", "version", "vendor"}
        self.assertTrue(expected_keys.issubset(meta.keys()))

    def test_pyproject_declares_dynamic_version_from_app_metadata(self):
        """pyproject.toml must source its version from src.app_metadata.APP_VERSION.

        Guards against accidentally re-introducing a hardcoded literal in
        [project].version — the whole point of the dynamic setup is that
        a single bump of APP_VERSION updates the wheel metadata too.
        """
        pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))

        self.assertNotIn(
            "version",
            pyproject["project"],
            "pyproject.toml [project].version must NOT be a literal — use dynamic",
        )
        self.assertIn(
            "version",
            pyproject["project"].get("dynamic", []),
            "pyproject.toml [project].dynamic must include 'version'",
        )
        self.assertEqual(
            pyproject["tool"]["setuptools"]["dynamic"]["version"]["attr"],
            "src.app_metadata.APP_VERSION",
            "Dynamic version source must point at src.app_metadata.APP_VERSION",
        )


if __name__ == "__main__":
    unittest.main()
