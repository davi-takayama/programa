import pygame
import unittest
from unittest.mock import MagicMock

from pygame import Surface

from src.render.menu.mod_2.challenge_2 import Challenge2


class TestChallenge2(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.font.init()
        self.change_state = MagicMock()
        self.chapter_index = 0
        self.challenge2 = Challenge2(Surface((800, 450)), self.change_state, self.chapter_index)

    def test_get_random_time_signature(self):
        self.challenge2.get_random_time_signature()
        upper_num, lower_num = self.challenge2.time_signature
        self.assertIn(upper_num, [2, 3, 4, 6, 8])
        self.assertIn(lower_num, [2, 4, 8])
        self.assertNotEqual((upper_num, lower_num), (2, 8))
        self.assertNotEqual((upper_num, lower_num), (8, 2))

    def test_correct_answer(self):
        self.challenge2.get_random_time_signature()
        self.challenge2.time_signature = (4, 4)
        self.challenge2.notes_and_pauses = [0.25, 0.25, 0.25, 0.25]
        self.challenge2.buttons[1].on_click()
        self.challenge2.click_continue()

        self.assertEqual(1, self.challenge2.score)

    def test_random_notes_generation(self):
        self.challenge2.time_signature = (4, 4)
        self.challenge2.notes = []
        self.challenge2.notes_and_pauses = []
        self.challenge2.get_random_notes()
        self.assertEqual(sum(self.challenge2.notes), self.challenge2.time_signature[0] / self.challenge2.time_signature[1])

    def test_consecutive_pauses_in_notes_and_pauses(self):
        self.challenge2.time_signature = (4, 4)
        self.challenge2.notes = []
        self.challenge2.notes_and_pauses = []
        self.challenge2.get_random_notes()
        for i in range(len(self.challenge2.notes_and_pauses) - 1):
            self.assertFalse(not self.challenge2.notes_and_pauses[i] and not self.challenge2.notes_and_pauses[i + 1])

if __name__ == '__main__':
    unittest.main()