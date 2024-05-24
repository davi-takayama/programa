import pygame.threads

from src.utils.root_dir import root_dir


class Metronome(pygame.threads.Thread):
    def __init__(self, bpm: int = 60, time_signature: tuple = (4, 4)):
        super().__init__()
        self.bpm = bpm
        self.time_signature = time_signature
        __dir = root_dir
        self.__trebble_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_trebble.wav")
        self.__bass_beep = pygame.mixer.Sound(__dir + "assets/audio/metronome_bass.wav")
        self.playing = False
        self.running = True
        self.__metronome_counter = 0

    def run(self):
        while self.running:
            if self.playing:
                self.__play_beep()
                pygame.time.wait(60000 // self.bpm)

    def __play_beep(self):
        if self.__metronome_counter % self.time_signature[0] != 0:
            self.__bass_beep.play()
        else:
            self.__trebble_beep.play()
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

    def get_cycle_time(self):
        return 60000 // self.bpm * self.time_signature[0]

    def restart(self):
        self.__metronome_counter = 0
        self.playing = True
