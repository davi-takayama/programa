import unittest
from unittest.mock import Mock, patch

from src.utils.audioinput.audio_analyzer import AudioAnalyzer


class TestAudioAnalyzer(unittest.TestCase):
    def setUp(self):
        self.queue = Mock()
        self.analyzer = AudioAnalyzer(self.queue)

    def test_frequency_to_number_with_zero_frequency(self):
        result = self.analyzer.frequency_to_number(0, 440)
        self.assertEqual(result, 0)

    def test_frequency_to_number_with_non_zero_frequency(self):
        result = self.analyzer.frequency_to_number(440, 440)
        self.assertEqual(result, 69)

    def test_number_to_frequency(self):
        result = self.analyzer.number_to_frequency(69, 440)
        self.assertEqual(result, 440)

    def test_number_to_note_name(self):
        result = self.analyzer.number_to_note_name(69)
        self.assertEqual(result, 'A')

    def test_frequency_to_note_name(self):
        result = self.analyzer.frequency_to_note_name(440, 440)
        self.assertEqual(result, 'A4')


if __name__ == '__main__':
    unittest.main()
