import os

import pygame
from pygame import Surface
from pygame.font import Font
from pyparsing import alphanums

from ..utils.button import Button
from ..utils.note_renderer import NoteRenderer
from .renderable import Renderable
from .staff import Staff


class IntroScr(Renderable):
    def __init__(self, screen: Surface, font: pygame.font.Font) -> None:
        super().__init__()
        self.screen = screen
        self.staff = Staff(screen, time_signature=(4, 4))
        self.note_drawer = NoteRenderer(screen)
        self.font = font
        self.rendered_state = self.__st1
        self.event_check_state = self.__on_click_note

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
        button_text = "Continuar"
        button_font = Font(None, 48)
        text_width, text_height = button_font.size(button_text)
        screen_width, screen_height = self.screen.get_size()
        button_padding = 11

        button_x = screen_width - (text_width) - (button_padding * 2) - 10
        button_y = screen_height - (text_height) - button_padding - 10
        button = Button(
            screen=self.screen,
            text=button_text,
            pos=(button_x, button_y),
            font=button_font,
            on_click=lambda: None,
        )
        button.render()

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
