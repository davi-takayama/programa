import os

import pygame
from src.utils.audioinput.audio_analyzer import AudioAnalyzer
from src.utils.audioinput.threading_helper import ProtectedList
from src.render.pentagram import Pentagram

queue = ProtectedList()
analyzer = AudioAnalyzer(queue)
analyzer.start()

pygame.init()
screen = pygame.display.set_mode((800, 450))
clock = pygame.time.Clock()
running_pygame = True
root_dir_path = os.path.dirname(os.path.realpath(__file__)) + "\\"

pentagram = Pentagram(screen, root_dir_path)
last_note = None
while running_pygame:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running_pygame = False
            analyzer.stop()
            break
    screen.fill("white")
    clock.tick(60)
    freq = queue.get()
    if freq is not None:
        last_note = analyzer.frequency_to_note_name(freq, 440)

    pentagram.render()

    pygame.display.flip()

pygame.quit()
analyzer.join()
exit()