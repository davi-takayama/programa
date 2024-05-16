import pygame.threads

from src.utils.root_dir import root_dir


class Metronome(pygame.threads.Thread):
    def __init__(self):
        super().__init__()
        self.__bpm = 60
        self.__time_signature = (4, 4)
        __dir = root_dir
        self.trebble_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_trebble.wav")
        self.bass_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_bass.wav")
        self.playing = False
        self.__metronome_counter = 0

    def run(self):
        while True:
            if self.playing:
                self.__metronome()
                pygame.time.wait(60000 // self.__bpm)

    def __metronome(self):
        if self.__metronome_counter % self.__time_signature[0] != 0:
            self.bass_beep.play()
        else:
            self.trebble_beep.play()
        self.__metronome_counter += 1
