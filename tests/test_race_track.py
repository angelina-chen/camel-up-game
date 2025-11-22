import unittest
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.append(parent_dir)
RaceTrack = None
if not RaceTrack:
    from RaceTrack import RaceTrack


from RaceTrack import RaceTrack

class TestValidMove(unittest.TestCase):
    def setUp(self):
        ''' This runs before each test '''
        pass

    def test_0(self):
        ''' Test return datatype '''
        # actual = self.empty_board.valid_move(2, 2)
        race_track = RaceTrack()
        race_track.set_up_camels([("red", 0), ("blue", 1), ("green", 2), ("yellow", 3), ("purple", 4)])
        self.assertEqual(race_track.to_list(), [[('red',)], [('blue',)], [('green',)], [('yellow',)], [('purple',)], [], [], [], [], [], [], [], [], [], [], []])
        race_track.location_update("red", 2)
        race_track.location_update("blue", 1)
        race_track.location_update("green", 2)
        race_track.location_update("yellow", 1)
        self.assertEqual(race_track.to_list(), [[], [], [], [], [('purple',), ('green',), ('red',), ('blue',), ('yellow',)], [], [], [], [], [], [], [], [], [], [], []])
        race_track.location_update("red", 1)
        race_track.location_update("blue", 1)
        race_track.location_update("green", 2)
        race_track.location_update("purple", 2)
        race_track.location_update("yellow", 1)
        race_track.location_update("purple", 1)
        self.assertEqual(race_track.to_list(), [[], [], [], [], [], [('red',)], [('blue',)], [('yellow',), ('green',)], [('purple',)], [], [], [], [], [], [], []])

    # def test_1(self):
    #     ''' Valid move on empty 3x3 board '''
    #     actual = self.empty_board.valid_move(2, 2)
    #     self.assertTrue(actual)
    #
    # def test_2(self):
    #     ''' Row, col too high on empty 3x3 board '''
    #     actual = self.empty_board.valid_move(3, 3)
    #     self.assertFalse(actual)

if __name__ == "__main__":
    unittest.main()
