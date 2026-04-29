import unittest

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


if __name__ == "__main__":
    unittest.main()
