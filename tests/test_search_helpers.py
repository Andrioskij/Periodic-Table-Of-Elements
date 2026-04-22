import unittest

from src.ui.search_helpers import compute_match_score, get_ranked_matches

HYDROGEN = {"name": "Hydrogen", "symbol": "H", "atomic_number": 1}
HELIUM = {"name": "Helium", "symbol": "He", "atomic_number": 2}
IRON = {"name": "Iron", "symbol": "Fe", "atomic_number": 26}
OXYGEN = {"name": "Oxygen", "symbol": "O", "atomic_number": 8}
SODIUM = {"name": "Sodium", "symbol": "Na", "atomic_number": 11}


class TestComputeMatchScore(unittest.TestCase):

    def test_exact_symbol_match(self):
        score = compute_match_score(IRON, "fe")
        self.assertEqual(score, 100)

    def test_exact_atomic_number(self):
        score = compute_match_score(IRON, "26")
        self.assertEqual(score, 98)

    def test_exact_name_match(self):
        score = compute_match_score(IRON, "iron")
        self.assertEqual(score, 96)

    def test_name_prefix(self):
        score = compute_match_score(HYDROGEN, "hyd")
        self.assertEqual(score, 90)

    def test_symbol_prefix(self):
        # "n" matches Na symbol prefix but not Sodium's name prefix
        score = compute_match_score(SODIUM, "n")
        self.assertEqual(score, 88)

    def test_substring_in_name(self):
        score = compute_match_score(HYDROGEN, "rogen")
        self.assertEqual(score, 78)

    def test_empty_query_returns_zero(self):
        score = compute_match_score(IRON, "")
        self.assertEqual(score, 0)

    def test_no_match_returns_zero(self):
        score = compute_match_score(IRON, "zzzzz")
        self.assertEqual(score, 0)

    def test_localized_name_exact_match(self):
        score = compute_match_score(IRON, "ferro", localized_name="Ferro")
        self.assertEqual(score, 95)


class TestGetRankedMatches(unittest.TestCase):

    ELEMENTS = [HYDROGEN, HELIUM, IRON, OXYGEN, SODIUM]

    def test_exact_symbol_first(self):
        results = get_ranked_matches(self.ELEMENTS, "Fe")
        self.assertEqual(results[0]["symbol"], "Fe")

    def test_respects_limit(self):
        results = get_ranked_matches(self.ELEMENTS, "h", limit=2)
        self.assertLessEqual(len(results), 2)

    def test_no_results_for_gibberish(self):
        results = get_ranked_matches(self.ELEMENTS, "xyzxyz")
        self.assertEqual(results, [])

    def test_atomic_number_search(self):
        results = get_ranked_matches(self.ELEMENTS, "8")
        self.assertEqual(results[0]["symbol"], "O")


if __name__ == "__main__":
    unittest.main()
