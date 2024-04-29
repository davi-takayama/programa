import os

import numpy as np
import pygame
import sounddevice as sd

from src.state_handler import StateHandler
from src.utils.audioinput.audio_analyzer import AudioAnalyzer
from src.utils.audioinput.threading_helper import ProtectedList

A4_FREQ = 440
queue = ProtectedList()
analyzer = AudioAnalyzer(queue)
analyzer.start()
curr_vol = 0


def get_volume(indata, frames, time, status):
    volume_norm = np.linalg.norm(indata) * 10
    global curr_vol
    curr_vol = volume_norm


stream = sd.InputStream(callback=get_volume)
stream.start()


pygame.init()
screen = pygame.display.set_mode((800, 450))
clock = pygame.time.Clock()
running_pygame = True

last_note = None

state_handler = StateHandler(screen=screen)

while running_pygame:
    clock.tick(60)

    pygame.display.flip()

    # if curr_vol > 3:
    #     freq = queue.get()
    #     if freq is not None:
    #         last_note = analyzer.frequency_to_note_name(freq, A4_FREQ)

    state_handler.render()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_pygame = False
            pygame.quit()

        state_handler.event_check(event)


stream.stop()
stream.close()

analyzer.stop()
analyzer.join()

exit()
