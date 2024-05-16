import pygame.threads

from src.utils.root_dir import root_dir


class Metronome(pygame.threads.Thread):
    def __init__(self):
        super().__init__()
        self.bpm = 60
        self.time_signature = (4, 4)
        __dir = root_dir
        self.trebble_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_trebble.wav")
        self.bass_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_bass.wav")
        self.playing = False
        self.running = True
        self.__metronome_counter = 0

    def run(self):
        while self.running:
            if self.playing:
                self.__metronome()
                pygame.time.wait(60000 // self.bpm)

    def __metronome(self):
        if self.__metronome_counter % self.time_signature[0] != 0:
            self.bass_beep.play()
        else:
            self.trebble_beep.play()
        self.__metronome_counter += 1

    def stop(self):
        self.playing = False
        self.running = False
        self.__metronome_counter = 0
        self.join()

    def increase_bpm(self, by: int = 1):
        self.bpm += by

    def decrease_bpm(self, by: int = 1):
        self.bpm -= by if self.bpm - by > 0 else 0

    def change_time_signature(self, time_signature):
        self.time_signature = time_signature if time_signature[0] > 0 and time_signature[1] > 0 else self.time_signature
