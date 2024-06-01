import textwrap

import pygame
from pygame import Surface
from pygame.event import Event

from src.render.menu.main_menu import Menu
from src.render.staff import Staff
from src.utils.bottom_screen_button import bottom_screen_button
from src.utils.button import Button
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable


class Explanation(Renderable):
    def __init__(self, screen: Surface, change_state) -> None:
        super().__init__(screen, change_state)
        self.staff = Staff(screen=screen, time_signature=(4, 4))
        self.pg_count = 0
        self.__top_text = [
            "Agora que você já sabe sobre notas e tempo, vamos aprender sobre a melodia.",
            "A melodia é a parte de uma música que é cantada ou tocada por um instrumento, normalmente, tocando apenas uma nota por vez.",
        ]
        self.__bottom_text = [
            "Esta é, basicamente, a junção dos dois elementos que você já aprendeu.",
            "Neste módulo, você aprenderá a tocar uma melodia simples de Beethoven, chamada de 'Ode à Alegria'.",
        ]

        def click_continue():
            if self.pg_count < self.__top_text.__len__():
                self.pg_count += 1
            else:
                self.__see_again()

        self.button: Button = bottom_screen_button(
            screen=screen,
            on_click=click_continue,
        )
        self.events = [self.button.event_check]
        self.note_renderer = NoteRenderer(screen, self.staff.c3_position)

    def render(self):
        self.screen.fill("white")
        if self.pg_count < len(self.__top_text):
            self.staff.render()
            self.button.render()
            top_text = (
                self.__top_text[self.pg_count]
                if self.pg_count < len(self.__top_text)
                else ""
            )

            bottom_text = (
                self.__bottom_text[self.pg_count]
                if self.pg_count < len(self.__bottom_text)
                else ""
            )

            font = pygame.font.Font(None, 38)

            for index, text in enumerate(textwrap.wrap(top_text, width=50)):
                text_surface = font.render(text, True, "black")
                text_rect = text_surface.get_rect()
                text_rect.centerx = self.screen.get_width() // 2
                text_rect.top = 50 + (index * (font.size(text)[1] + 10))
                self.screen.blit(text_surface, text_rect)

            for index, text in enumerate(textwrap.wrap(bottom_text, width=50)):
                text_surface = font.render(text, True, "black")
                text_rect = text_surface.get_rect()
                text_rect.centerx = self.screen.get_width() // 2
                text_rect.topleft = (
                    text_rect.centerx - text_rect.width // 2,
                    (self.screen.get_height() // 2 + 75)
                    + (index * (font.size(text)[1] + 10)),
                )
                self.screen.blit(text_surface, text_rect.topleft)

        else:
            self.__end_explanation()

    def event_check(self, event_arg: Event):
        if self.pg_count < len(self.__top_text):
            self.button.event_check(event_arg)
        else:
            for event in self.events:
                event(event_arg)

    def __see_again(self):
        self.events = [self.button.event_check]
        self.pg_count = 0

    def __end_explanation(self):
        text = "Gostaria de rever a explicação?"
        width, height = self.screen.get_size()
        font = pygame.font.Font(None, 36)
        text_width, text_height = font.size(text)
        self.screen.blit(
            font.render(text, True, "black"),
            (
                (width // 2) - (text_width // 2),
                (height // 4) - (text_height // 2),
            ),
        )

        def __continue():
            from src.utils.save_operations.read_save import Save
            save = Save.load()
            save.md3.chapters[0]["unlocked"] = True
            save.save()

            self.change_state(Menu(self.screen, self.change_state))

        confirm_button = Button(
            font=font,
            screen=self.screen,
            text="Sim",
            on_click=self.__see_again,
            pos=(width // 2 - 200 - (font.size("Sim")[0] // 2), height // 2),
        )
        continue_button = Button(
            font=font,
            screen=self.screen,
            text="Não",
            on_click=__continue,
            pos=(width // 2 + 200 - (font.size("Não")[0] // 2), height // 2),
        )

        confirm_button.render()
        continue_button.render()

        self.events = [confirm_button.event_check, continue_button.event_check]
