import unittest

from core.selection import apply_selection, parse_selector


class SelectionTests(unittest.TestCase):
    def test_empty_selector_returns_all(self):
        self.assertEqual(parse_selector("", 4), [0, 1, 2, 3])

    def test_ranges_and_order(self):
        self.assertEqual(parse_selector("1,3-5,2", 5), [0, 2, 3, 4, 1])

    def test_descending_range(self):
        self.assertEqual(parse_selector("4-2", 4), [3, 2, 1])

    def test_duplicates_rejected_by_default(self):
        self.assertEqual(parse_selector("1,1,2", 3), [0, 1])

    def test_custom_order_allows_duplicates(self):
        self.assertEqual(parse_selector("2,2,1", 3, allow_duplicates=True), [1, 1, 0])

    def test_apply_range_skip_and_custom_order(self):
        self.assertEqual(
            apply_selection(range(6), frame_range="2-5", skip_frames="2", custom_order="3,1"),
            [4, 2],
        )

    def test_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            parse_selector("5", 4)

    def test_invalid_selector_raises(self):
        with self.assertRaises(ValueError):
            parse_selector("hello", 4)
