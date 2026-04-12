import unittest

from src.ui.layout_policy import (
    compute_responsive_layout,
    resolve_responsive_mode,
)


class TestResolveResponsiveMode(unittest.TestCase):

    def test_wide(self):
        self.assertEqual(resolve_responsive_mode(1600), "wide")

    def test_medium(self):
        self.assertEqual(resolve_responsive_mode(1200), "medium")

    def test_narrow(self):
        self.assertEqual(resolve_responsive_mode(900), "narrow")

    def test_compact(self):
        self.assertEqual(resolve_responsive_mode(600), "compact")

    def test_very_small_clamps_to_compact(self):
        self.assertEqual(resolve_responsive_mode(200), "compact")

    def test_boundary_wide(self):
        self.assertEqual(resolve_responsive_mode(1500), "wide")

    def test_boundary_medium(self):
        self.assertEqual(resolve_responsive_mode(1100), "medium")

    def test_boundary_narrow(self):
        self.assertEqual(resolve_responsive_mode(800), "narrow")


class TestComputeResponsiveLayout(unittest.TestCase):

    def test_wide_layout_horizontal(self):
        policy = compute_responsive_layout(1600)
        self.assertEqual(policy.mode, "wide")
        self.assertEqual(policy.content_direction, "horizontal")

    def test_narrow_layout_vertical(self):
        policy = compute_responsive_layout(700)
        self.assertEqual(policy.content_direction, "vertical")

    def test_cell_size_within_bounds(self):
        for width in [400, 800, 1200, 1800]:
            policy = compute_responsive_layout(width)
            self.assertGreaterEqual(policy.cell_size, 22)

    def test_header_height_scales(self):
        small = compute_responsive_layout(600)
        large = compute_responsive_layout(1800)
        self.assertLessEqual(small.header_height, large.header_height)

    def test_font_size_minimum(self):
        policy = compute_responsive_layout(400)
        self.assertGreaterEqual(policy.element_font_size, 8)


if __name__ == "__main__":
    unittest.main()
