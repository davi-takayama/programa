import pygame

from src.state_handler import StateHandler

pygame.init()
screen = pygame.display.set_mode((800, 450))
clock = pygame.time.Clock()
running_pygame = True

last_note = None

state_handler = StateHandler(screen=screen)

while running_pygame:
    clock.tick(60)

    pygame.display.flip()
    state_handler.render()

    for event in pygame.event.get():
        state_handler.event_check(event)
        if event.type == pygame.QUIT:
            running_pygame = False
            pygame.quit()
            pygame.mixer.quit()
            pygame.font.quit()
            try:
                pygame.threads.quit()
            except AttributeError:
                pass

exit()
