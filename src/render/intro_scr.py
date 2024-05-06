import pygame
from pygame import Surface

from ..utils.bottom_screen_button import bottom_screen_button
from ..utils.note_renderer import NoteRenderer
from ..utils.renderable import Renderable
from .staff import Staff


class IntroScr(Renderable):
    def __init__(
        self, screen: Surface, change_state: classmethod, font: pygame.font.Font
    ) -> None:
        super().__init__(screen, change_state)
        self.screen = screen
        self.change_state = change_state
        self.staff = Staff(screen, time_signature=(4, 4))
        self.note_drawer = NoteRenderer(screen)
        self.font = font
        self.rendered_state = self.__st1
        self.event_check_state = self.__on_click_note

        def on_click():
            from .menu.mod_1.explanation import Explanation1

            self.change_state(Explanation1(self.screen, self.change_state))

        self.button = bottom_screen_button(
            screen=screen,
            on_click=on_click,
        )

    def render(self) -> None:
        self.rendered_state()

    def __st1(self):
        self.screen.fill("white")
        self.staff.render(render_cleff=False)
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

    def st_02(self):
        self.screen.fill("white")

        self.button.render()

        lines = "Bem vindo ao tutorial\nEste tutorial vai te ensinar os básicos da partitura".split(
            "\n"
        )
        font = pygame.font.Font(None, 40)

        for i, line in enumerate(lines):
            text = font.render(line, True, "black")
            text_rect = text.get_rect()

            # Centralize o texto
            screen_width, screen_height = self.screen.get_size()
            text_rect.center = (
                screen_width // 2,
                screen_height // 2 + (i - len(lines) // 2) * font.get_linesize(),
            )

            self.screen.blit(text, text_rect)

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
                self.rendered_state = self.st_02

    def event_check(self, event):
        self.event_check_state(event)
        self.button.event_check(event)
