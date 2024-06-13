import unittest
from unittest.mock import Mock, patch

import pygame
from pygame import Surface

from src.render.menu.mod_3.challenge import Challenge


class TestChallenge(unittest.TestCase):
    @patch('src.render.menu.mod_3.challenge.AudioAnalyzer')
    @patch('src.render.menu.mod_3.challenge.ProtectedList')
    @patch('src.render.menu.mod_3.challenge.Surface')
    def setUp(self, mock_surface, mock_protected_list, mock_audio_analyzer):
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.init()
        self.mock_change_state = Mock()
        self.challenge = Challenge(Surface((0, 0)), self.mock_change_state, 0)
        self.challenge.queue = mock_protected_list
        self.challenge.alyzer = mock_audio_analyzer

    def test_audio_retrieval_with_frequency(self):
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.init()
        self.challenge.queue.get.return_value = 440
        self.challenge.alyzer.frequency_to_note_name.return_value = "A4"
        self.challenge.get_audio()
        self.assertEqual([("A", 0)], self.challenge.played)

    def test_threshold_meet_with_audio_above_mean(self):
        audio = [('A', 0.8), ('B', 0.6), ('C', 0.4)]
        mean_vol_threshold = 0.5
        result = Challenge.find_threshold_meet(audio, mean_vol_threshold)
        self.assertEqual([({'A', 'B'}, 2)], result)

    def test_threshold_meet_with_audio_mixed(self):
        audio = [('A', 0.8), ('B', 0.3), ('C', 0.6)]
        mean_vol_threshold = 0.5
        result = Challenge.find_threshold_meet(audio, mean_vol_threshold)
        self.assertEqual([({'A'}, 1), ('C', 1)], result)

    def test_round_played_values_with_valid_values(self):
        note_list = [({'A', 'B'}, 50), ({'C', 'D'}, 70), ({'E', 'F'}, 80)]
        result = Challenge.round_played_values(note_list)
        self.assertEqual([({'A', 'B'}, 0.25), ({'C', 'D'}, 0.25), ({'E', 'F'}, 0.5)], result)

    def test_score_calculation_with_perfect_score(self):
        self.challenge.curr_bars = [[("C", 0.25), ("C", 0.25), ("D", 0.25), ("E", 0.25)],
                                    [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]]
        bar_list = [[("C", 0.25), ("C", 0.25), ("D", 0.25), ("E", 0.25)],
                    [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]]
        self.challenge.calculate_score(bar_list)
        self.assertEqual(1, self.challenge.score)

    def test_score_calculation_with_no_score(self):
        self.challenge.curr_bars = [[("C", 0.25), ("C", 0.25), ("D", 0.25), ("E", 0.25)],
                                    [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]]
        bar_list = [[("G", 0.125), ("F", 0.5), ("E", 0.125), ("D", 0.25)],
                    [("C", 0.5), ("C", 0.25), ("D", 0.125), ("E", 0.125)]]
        self.challenge.calculate_score(bar_list)
        self.assertEqual(0, self.challenge.score)

    def test_score_calculation_with_half_score(self):
        self.challenge.curr_bars = [[("C", 0.25), ("C", 0.25), ("D", 0.25), ("E", 0.25)],
                                    [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]]
        bar_list = [[("D", 0.5), ("E", 0.5)],
                    [("G", 0.25), ("F", 0.25), ("E", 0.25), ("D", 0.25)]]
        self.challenge.calculate_score(bar_list)
        self.assertEqual(0, self.challenge.score)


if __name__ == '__main__':
    unittest.main()
