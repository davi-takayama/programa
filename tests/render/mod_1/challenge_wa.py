import unittest
from unittest.mock import patch

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
        self.mock_stream = mock_stream
        self.mock_analyzer = mock_analyzer
        self.challenge = Challenge(Surface((800, 450)), None, 0, use_audio=True)

    def tearDown(self):
        self.challenge.played_notes = []

    @patch('src.render.menu.mod_1.challenge.time.time', return_value=1000)
    def test_get_note_with_note_played_and_volume_below_sensibility(self, mock_time):
        global vol
        vol = 4
        self.challenge.vol_sensibility = 5
        self.challenge.note_played = 'A'
        self.challenge.get_note()
        self.assertEqual(self.challenge.played_notes, [])

    @patch('src.render.menu.mod_1.challenge.time.time', return_value=1000)
    @patch("src.render.menu.mod_1.challenge._queue.get", return_value=440)
    def test_get_note_with_note_played_and_volume_above_sensibility(self, mock_time, mock_queue):
        global vol
        vol = 6
        self.challenge.vol_sensibility = 5
        self.challenge._continue = False
        self.challenge.note_played = None
        self.challenge._queue.put(440)
        self.challenge.get_note()

        self.assertEqual(['A'], self.challenge.played_notes)

    @patch('src.render.menu.mod_1.challenge.statistics.mode', return_value='A')
    def test_correct_note(self, mock_mode):
        self.challenge.current_note = ('A', 0)
        self.challenge.played_notes = ['A', 'A', 'A']
        self.challenge.process_note_played()
        self.assertEqual(self.challenge.score, 1)

    @patch('src.render.menu.mod_1.challenge.statistics.mode', return_value='B')
    def test_incorrect_note(self, mock_mode):
        self.challenge.current_note = ('A', 0)
        self.challenge.played_notes = ['B', 'B', 'B']
        self.challenge.process_note_played()
        self.assertEqual(self.challenge.score, 0)

    @patch('src.render.menu.mod_1.challenge.statistics.mode', return_value='C#')
    def test_note_equivalent_is_recognized_as_correct(self, mock_mode):
        self.challenge.current_note = ('Db', 0)
        self.challenge.played_notes = ['C#', 'C#', 'C#']
        self.challenge.process_note_played()
        self.assertEqual(self.challenge.score, 1)
