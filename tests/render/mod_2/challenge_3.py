import unittest
from unittest.mock import MagicMock

import numpy as np
import pygame
from pygame import Surface

from src.render.menu.mod_2.challenge_3 import Challenge3


class Challenge3Tests(unittest.TestCase):
    def setUp(self):
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.init()
        self.change_state = MagicMock()
        self.chapter_index = 0
        self.challenge3 = Challenge3(Surface((800, 450)), self.change_state, self.chapter_index)

    def test_random_challenge_returns_valid_challenge(self):
        challenge = self.challenge3.random_challenge()
        self.assertIsInstance(challenge, list)
        self.assertTrue(all(isinstance(item, tuple) and len(item) == 2 for item in challenge))

    def test_random_challenge_returns_correct_number_of_notes_and_pauses(self):
        challenge = self.challenge3.random_challenge()
        note_count = sum(1 for item in challenge if item[0] == 'note')
        pause_count = sum(1 for item in challenge if item[0] == 'pause')
        self.assertTrue(note_count >= 1)
        self.assertTrue(pause_count >= 1)
        self.assertEqual(note_count + pause_count, len(challenge))

    def test_random_challenge_no_adjacent_pauses(self):
        challenge = self.challenge3.random_challenge()
        for i in range(len(challenge) - 1):
            self.assertFalse(challenge[i][0] == 'pause' and challenge[i + 1][0] == 'pause')

    def test_random_challenge_no_pause_at_start_or_end(self):
        challenge = self.challenge3.random_challenge()
        self.assertNotEqual(challenge[0][0], 'pause')
        self.assertNotEqual(challenge[-1][0], 'pause')

    def test_calculate_mean_vol_threshold_returns_zero_for_empty_stream(self):
        self.challenge3.vol_stream = []
        self.assertEqual(self.challenge3.calculate_mean_vol_threshold(), 0)

    def test_calculate_mean_vol_threshold_returns_zero_for_nan_stream(self):
        self.challenge3.vol_stream = [np.nan, np.nan, np.nan]
        self.assertEqual(self.challenge3.calculate_mean_vol_threshold(), 0)

    def test_calculate_mean_vol_threshold_returns_zero_for_inf_stream(self):
        self.challenge3.vol_stream = [np.inf, np.inf, np.inf]
        self.assertEqual(self.challenge3.calculate_mean_vol_threshold(), 0)

    def test_calculate_mean_vol_threshold_returns_correct_value_for_valid_stream(self):
        self.challenge3.vol_stream = [1, 2, 3, 4, 5]
        expected_value = np.mean(self.challenge3.vol_stream) * 0.7
        self.assertEqual(self.challenge3.calculate_mean_vol_threshold(), expected_value)

    def test_filter_audio_stream_returns_zero_for_values_below_sensibility(self):
        self.challenge3.vol_stream = [1, 2, 3, 4, 5]
        self.challenge3.vol_sensibility = 3
        expected_output = [0, 0, 3, 4, 5]
        self.assertEqual(self.challenge3.filter_audio_stream(self.challenge3.vol_stream, self.challenge3.vol_sensibility),
                         expected_output)

    def test_filter_audio_stream_returns_same_values_for_values_above_sensibility(self):
        self.challenge3.vol_stream = [1, 2, 3, 4, 5]
        self.challenge3.vol_sensibility = 1
        expected_output = [1, 2, 3, 4, 5]
        self.assertEqual(self.challenge3.filter_audio_stream(self.challenge3.vol_stream, self.challenge3.vol_sensibility),
                         expected_output)

    def test_filter_audio_stream_returns_zero_for_values_equal_to_sensibility(self):
        self.challenge3.vol_stream = [1, 2, 3, 4, 5]
        self.challenge3.vol_sensibility = 2
        expected_output = [0, 2, 3, 4, 5]
        self.assertEqual(self.challenge3.filter_audio_stream(self.challenge3.vol_stream, self.challenge3.vol_sensibility),
                         expected_output)

    def test_filter_audio_stream_returns_zero_for_empty_stream(self):
        self.challenge3.vol_stream = []
        self.challenge3.vol_sensibility = 2
        expected_output = []
        self.assertEqual(self.challenge3.filter_audio_stream(self.challenge3.vol_stream, self.challenge3.vol_sensibility),
                         expected_output)


if __name__ == '__main__':
    unittest.main()
