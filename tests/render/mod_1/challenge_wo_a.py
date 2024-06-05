import random
import unittest
from unittest.mock import Mock, patch

import pygame
from pygame import Surface

from src.render.menu.mod_1.challenge import Challenge


class TestChallenge(unittest.TestCase):
    @patch('src.render.menu.mod_1.challenge.AudioAnalyzer')
    @patch('src.render.menu.mod_1.challenge.sd.InputStream')
    def setUp(self, mock_stream, mock_analyzer):
        pygame.font.init()
        pygame.mixer.init()
        pygame.display.init()
        self.screen = Surface((800, 450))
        self.change_state = Mock()
        self.chapter_index = 0
        self.mock_stream = mock_stream
        self.mock_analyzer = mock_analyzer
        self.challenge = Challenge(self.screen, self.change_state, self.chapter_index, )

    def test_click_continue(self):
        initial_challenge = self.challenge.current_challenge
        self.challenge.click_continue()
        self.assertEqual(self.challenge.current_challenge, initial_challenge + 1)

    def test_pick_random_note(self):
        note, num = self.challenge.pick_random_note()
        self.assertIn(note[0], self.challenge.staff_notes)
        self.assertIn(num, range(len(self.challenge.staff_notes)))

    def test_swap_note_if_invalid(self):
        self.assertEqual(self.challenge.swap_note_if_invalid('E#'), 'F')
        self.assertEqual(self.challenge.swap_note_if_invalid('B#'), 'C')
        self.assertEqual(self.challenge.swap_note_if_invalid('Cb'), 'B')
        self.assertEqual(self.challenge.swap_note_if_invalid('Fb'), 'E')

    def test_check_correct_answer(self):
        self.challenge.current_challenge = 0
        self.challenge.current_note = random.choice(self.challenge.staff_notes)

        score = self.challenge.score
        for button in self.challenge.note_buttons:
            if button.text == self.challenge.current_note:
                button.on_click()
                break

        self.assertEqual(score + 1, self.challenge.score)

    def test_check_incorrect_answer(self):
        self.challenge.current_challenge = 0
        self.challenge.current_note = random.choice(self.challenge.staff_notes)

        score = self.challenge.score
        for button in self.challenge.note_buttons:
            if button.text != self.challenge.current_note:
                button.on_click()
                break

        self.assertEqual(score, self.challenge.score)


if __name__ == '__main__':
    unittest.main()
