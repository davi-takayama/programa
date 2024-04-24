import pygame
from pygame import Surface

from .staff import Pentagram
from ..utils.note_renderer import NoteRenderer
from .renderable import Renderable


class IntroScr(Renderable):
    def __init__(self, screen: Surface, main_path: str, font: pygame.font.Font) -> None:
        super().__init__()
        self.screen = screen
        self.main_path = main_path
        self.pentagram = Pentagram(screen, main_path)
        self.note_drawer = NoteRenderer(screen)
        self.font = font

    def render(self) -> None:
        self.__st1()

    def __st1(self):
        self.screen.fill("white")
        self.pentagram.render(render_cleff=False)
        self.note_drawer.quarter(
            x_pos=(self.screen.get_width() // 2) - 10,
            y_pos=(self.screen.get_height() // 2),
        )

        text = "Clique na nota para iniciar"
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 4),
            ),
        )

    def __on_click_note(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            col = pos[0]
            row = pos[1]

            screen_middle_x = self.screen.get_width() // 2
            screen_middle_y = self.screen.get_height() // 2

            if (
                screen_middle_x - 10 <= col <= screen_middle_x + 10
                and screen_middle_y - 5 <= row <= screen_middle_y + 5
            ):
                return True
            else:
                return False

    def event_check(self, event):
        self.__on_click_note(event)
