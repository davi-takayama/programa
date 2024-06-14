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

    def test_filter_audio_stream_returns_zero_for_empty_stream(self):
        self.challenge3.vol_stream = []
        self.challenge3.vol_sensibility = 2
        expected_output = []
        self.assertEqual(self.challenge3.filter_audio_stream(self.challenge3.vol_stream, self.challenge3.vol_sensibility),
                         expected_output)

    def test_process_audio_stream_valid_answer(self):
        self.challenge3.vol_stream = [0.04, 0.04, 0.06, 0.06, 9.48, 9.48, 21.154, 23.3168, 26.274160000000002, 27.488191999999998,
                                      28.1524704, 27.922132480000005, 27.372920576000002, 26.7010106112, 26.606786237439998,
                                      26.529559369728, 26.571269121433602, 26.35616569823232, 26.21748696393318, 25.5987305324331,
                                      24.959243499273253, 24.21959480634127, 24.089767661122902, 23.999872493492834,
                                      24.039928030923146, 23.807960104883197, 23.30157762716127, 22.68590754640889, 22.04749703471403,
                                      21.902680916224583, 21.85203559018772, 21.88494330128246, 21.78539577829404, 21.5020678159153,
                                      20.97549271884187, 20.363512106951436, 19.93980096515866, 19.854662614422022, 19.87489271591614,
                                      19.82991106606763, 19.464960756396753, 19.022974364492875, 16.383587024177924, 13.57531227773416,
                                      0.57, 0.57, 27.365999999999996, 32.221199999999996, 35.22544, 35.819328,
                                      35.862953600000004, 35.314456320000005, 35.435481984, 35.4599876608, 35.37109392896,
                                      34.958216317951994, 34.4578620493824, 33.509215673466876, 32.64541554456986, 31.708926243607344,
                                      28.95286835763544, 22.572358920248558, 15.103045455576801, 2.62, 2.62, 0.92, 17.676, 21.6912,
                                      26.849439999999998, 27.940128000000005, 28.6719136, 28.518408320000002, 28.886064384,
                                      28.9428945408, 29.041791784960004, 28.746937265152003, 28.0657458100224, 27.22853661503488,
                                      26.542856485011452, 26.320278620009265, 23.198627021004143, 17.66578112820268, 10.97, 1.76, 1.76,
                                      0.78, 0.46, 0.46, 23.098000000000003, 28.229599999999998, 32.86952, 34.091824, 35.5822688,
                                      36.442818560000006, 36.825017472000006, 36.659567206400006, 36.28891693568001,
                                      35.283696828416005, 34.2965227528192, 33.186043916247044, 32.93251333381325, 32.829711450012056,
                                      32.76444495676507, 32.39683128135543, 31.976255247624103, 31.088617305795907, 30.172974510684003,
                                      29.15831836329598, 28.892258574795996, 28.688115387618392, 28.646074792482874, 28.27683803602026,
                                      28.036582565700627, 27.31468412034418, 26.566253337208963, 25.71618749151063, 25.45648816574392,
                                      25.272535131450912, 25.221804659438966, 24.866867958177977, 22.919734523523385,
                                      20.593320496340272, 15.57, 15.57, 2.62, 2.62, 0.93, 0.64, 0.64, 19.93, 27.836000000000002,
                                      32.955200000000005, 35.24023999999999, 36.085088, 36.423065599999994, 35.71163072, 34.812939264,
                                      33.6669139968, 33.20397065216, 32.800176929791995, 32.54482951639041, 31.983001289236476,
                                      31.175566161125374, 30.25771349007237, 29.098655930239552, 28.34927388406238, 27.633585962860387,
                                      27.336571969384558, 26.88803158644899, 26.49292071116671, 25.902190459523137, 25.06702223413797,
                                      24.143842538732223, 23.504172954574038, 23.24160309866125, 23.09, 22.86]
        self.challenge3.vol_sensibility = 2
        self.challenge3.curr_rythm = [('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25)]
        self.challenge3.process_audio_stream()
        print(self.challenge3.played)
        self.assertEqual([('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25)], self.challenge3.played)
        self.assertEqual(1, self.challenge3.score)

    def test_process_audio_stream_parcially_invalid_answer(self):
        self.challenge3.vol_stream = [0.04, 0.04, 0.06, 0.06, 9.48, 9.48, 21.154, 23.3168, 26.274160000000002, 27.488191999999998,
                                      28.1524704, 27.922132480000005, 27.372920576000002, 26.7010106112, 26.606786237439998,
                                      26.529559369728, 26.571269121433602, 26.35616569823232, 26.21748696393318, 25.5987305324331,
                                      24.959243499273253, 24.21959480634127, 24.089767661122902, 23.999872493492834,
                                      24.039928030923146, 23.807960104883197, 23.30157762716127, 22.68590754640889, 22.04749703471403,
                                      21.902680916224583, 21.85203559018772, 21.88494330128246, 21.78539577829404, 21.5020678159153,
                                      20.97549271884187, 20.363512106951436, 19.93980096515866, 19.854662614422022, 19.87489271591614,
                                      19.82991106606763, 19.464960756396753, 19.022974364492875, 16.383587024177924, 13.57531227773416,
                                      0.57, 0.57, 27.365999999999996, 32.221199999999996, 35.22544, 35.819328,
                                      35.862953600000004, 35.314456320000005, 35.435481984, 35.4599876608, 35.37109392896,
                                      34.958216317951994, 34.4578620493824, 33.509215673466876, 32.64541554456986, 31.708926243607344,
                                      28.95286835763544, 22.572358920248558, 15.103045455576801, 2.62, 2.62, 0.92, 17.676, 21.6912,
                                      26.849439999999998, 27.940128000000005, 28.6719136, 28.518408320000002, 28.886064384,
                                      28.9428945408, 29.041791784960004, 28.746937265152003, 28.0657458100224, 27.22853661503488,
                                      26.542856485011452, 26.320278620009265, 23.198627021004143, 17.66578112820268, 10.97, 1.76, 1.76,
                                      0.78, 0.46, 0.46, 23.098000000000003, 28.229599999999998, 32.86952, 34.091824, 35.5822688,
                                      36.442818560000006, 36.825017472000006, 36.659567206400006, 36.28891693568001,
                                      35.283696828416005, 34.2965227528192, 33.186043916247044, 32.93251333381325, 32.829711450012056,
                                      32.76444495676507, 32.39683128135543, 31.976255247624103, 31.088617305795907, 30.172974510684003,
                                      29.15831836329598, 28.892258574795996, 28.688115387618392, 28.646074792482874, 28.27683803602026,
                                      28.036582565700627, 27.31468412034418, 26.566253337208963, 25.71618749151063, 25.45648816574392,
                                      25.272535131450912, 25.221804659438966, 24.866867958177977, 22.919734523523385,
                                      20.593320496340272, 15.57, 15.57, 2.62, 2.62, 0.93, 0.64, 0.64, 19.93, 27.836000000000002,
                                      32.955200000000005, 35.24023999999999, 36.085088, 36.423065599999994, 35.71163072, 34.812939264,
                                      33.6669139968, 33.20397065216, 32.800176929791995, 32.54482951639041, 31.983001289236476,
                                      31.175566161125374, 30.25771349007237, 29.098655930239552, 28.34927388406238, 27.633585962860387,
                                      27.336571969384558, 26.88803158644899, 26.49292071116671, 25.902190459523137, 25.06702223413797,
                                      24.143842538732223, 23.504172954574038, 23.24160309866125, 23.09, 22.86]
        self.challenge3.vol_sensibility = 2
        self.challenge3.curr_rythm = [('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25), ('note', 0.25)]
        self.challenge3.process_audio_stream()
        self.assertEqual([('note', 0.25), ('note', 0.125), ('note', 0.125), ('note', 0.25), ('note', 0.25)], self.challenge3.played)
        self.assertEqual(0.6, self.challenge3.score)

if __name__ == '__main__':
    unittest.main()
