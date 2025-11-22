import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)
Pyramid = None
if not Pyramid:
    from Pyramid import Pyramid

from Pyramid import Pyramid


class TestPyramid(unittest.TestCase):

    def setUp(self):
        self.colors = {"Blue", "Green", "Yellow", "Red", "Purple", "Black", "White"}
        self.pyramid = Pyramid()
    def test_initial_unrolled(self):
        # Tests that all colors are in unrolled_dice at initialization
        self.assertSetEqual(self.pyramid.unrolled_dice, self.colors)

    def test_initial_rolled_empty(self):
        #Tests that rolled_dice is empty at initialization
        self.assertEqual(len(self.pyramid.rolled_dice), 0)

    def test_roll_removes_from_unrolled(self):
        # Tests that rolling removes the color from unrolled_dice and adds to rolled_dice
        before = set(self.pyramid.unrolled_dice)
        result = self.pyramid.roll()
        after = set(self.pyramid.unrolled_dice)
        self.assertEqual(len(before) - 1, len(after))
        self.assertEqual(len(self.pyramid.rolled_dice), 1)

    def test_roll_returns_valid(self):
        # Tests that roll returns a set of (color, value) with valid color and value
        result = self.pyramid.roll()
        self.assertIsInstance(result, set)
        self.assertEqual(len(result), 2)
        color = next(val for val in result if isinstance(val, str))
        value = next(val for val in result if isinstance(val, int))
        self.assertIn(color, self.colors)
        self.assertIn(value, [1, 2, 3])

    def test_blackwhite_rule(self):
        # Tests that rolling Black or White also removes the paired color from unrolled_dice.
        # This will manually force Black or White to be the only unrolled_dice colors
        self.pyramid.unrolled_dice = {"Black", "White"}
        result = self.pyramid.roll()
        # After rolling, both should be removed from unrolled_dice, and both added to rolled_dice
        self.assertEqual(self.pyramid.unrolled_dice, set())
        self.assertEqual(self.pyramid.rolled_dice, {"Black", "White"})
        self.assertIn(next(val for val in result if isinstance(val, str)), {"Black", "White"})

    def test_roll_alldice(self):
        # Tests that rolling all dice exhausts unrolled_dice
        for _ in range(7):
            self.pyramid.roll()
        self.assertEqual(len(self.pyramid.unrolled_dice), 0)
        self.assertEqual(len(self.pyramid.rolled_dice), 7)
        result = self.pyramid.roll() # Try rolling again which should print error and return None
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
