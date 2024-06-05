import unittest
from unittest.mock import patch

import pygame
from pygame import Surface

from src.render.menu.mod_2.challenge import Challenge


class TestChallenge(unittest.TestCase):
    def setUp(self):
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.init()
        self.challenge = Challenge(Surface((800, 450)), None, 0)

    @patch('random.choice', return_value=1)
    def test_chosen_notes_sum_equals_expected(self, mock_random_choice):
        self.challenge.pick_notes()
        self.assertEqual(sum(self.challenge.chosen_notes), 2)

    @patch('random.choice', return_value=0.5)
    def test_chosen_notes_sum_less_than_expected(self, mock_random_choice):
        self.challenge.pick_notes()
        self.assertEqual(sum(self.challenge.chosen_notes), 1)

    @patch('random.choice', return_value=0.125)
    def test_chosen_notes_sum_greater_than_expected(self, mock_random_choice):
        self.challenge.pick_notes()
        self.assertEqual(sum(self.challenge.chosen_notes), 0.25)

    def test_num_notes_selected_increases_with_challenge(self):
        self.assertEqual(self.challenge.num_notes_selected(), 2)
        self.challenge.current_challenge = 5
        self.assertEqual(self.challenge.num_notes_selected(), 3)
        self.challenge.current_challenge = 10
        self.assertEqual(self.challenge.num_notes_selected(), 4)


if __name__ == '__main__':
    unittest.main()
