import textwrap

import pygame
from pygame import Surface
from pygame.event import Event

from ....utils.bottom_screen_button import bottom_screen_button
from ....utils.button import Button
from ....utils.note_renderer import NoteRenderer
from ....utils.save_operations.check_save import save_exists
from ....utils.save_operations.create_save import create_save
from ....utils.renderable import Renderable
from ...staff import Staff


class Explanation1(Renderable):

    def __init__(self, screen: Surface, change_state: classmethod) -> None:
        super().__init__(screen, change_state)
        self.note_renderer = NoteRenderer(screen)
        self.staff = Staff(screen, time_signature=(4, 4))
        self.pg_count = 0
        self.top_text = [
            "Para entender como ler uma partitura é necessário primeiro entender seus elementos.",
            "Cada linha e espaço no PAUTA representa uma nota diferente.",
            "Além da clave, existem outros elementos que ficam no inicio da pauta, como a assinatura de tempo.",
            "As notas possiveis dentro da partitura são 'C', 'D', 'E', 'F', 'G', 'A', 'B', sempre sendo lidas de "
            "baixo para cima.",
            "Colocando as notas em seus respectivos lugares, cada linha e espaço são:",
            "Para memorizar as notas de cada grupo podemos usar algumas frases, como:",
        ]
        self.bottom_text = [
            "Nelas sempre haverão 5 linhas paralelas que formam um conjunto chamado PAUTA.",
            "As notas que cada um indica variam dependendo da CLAVE que o acompanha.",
            "esta define a métrica das notas e a duração dos compassos. Estes serão explicados depois.",
            "o G (sol) no campo da CLAVE DE SOL fica na segunda linha, onde a ponta interna se encontra.",
            "Note que a nota de cada espaço é seguinte à nota da linha anterior.",
            "",
        ]
        self.has_save = save_exists()

        def __on_click_continue():
            if self.pg_count < self.bottom_text.__len__():
                self.pg_count += 1
            else:
                self.__see_again()

        self.button: Button = bottom_screen_button(
            screen=screen,
            on_click=__on_click_continue,
        )

    def render(self) -> None:
        self.screen.fill("white")
        if self.pg_count < 6:
            self.button.render()
            self.staff.render(
                render_cleff=self.pg_count >= 1,
                render_time_signature=self.pg_count >= 2,
            )
            top_text = (
                self.top_text[self.pg_count]
                if self.pg_count < len(self.top_text)
                else ""
            )
            bottom_text = (
                self.bottom_text[self.pg_count]
                if self.pg_count < len(self.bottom_text)
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

        if self.pg_count == 3:
            self.note_renderer.quarter(
                x_pos=100, y_pos=self.staff.c3_position - self.staff.note_spacing * 4
            )

        if self.pg_count == 4:
            self.__show_notes_in_cleff()

        if self.pg_count == 5:
            self.__show_notes_in_cleff(show_letter_only=True)

    def __show_notes_in_cleff(self, show_letter_only=False):
        horizontal_spacing = 40
        for index, word in enumerate(
                ["Elefantes", "Grandes", "Brincam", "Durante", "Festas"]
        ):
            x_pos = 100 + index * horizontal_spacing
            y_pos = self.staff.c3_position - self.staff.line_spacing * (index + 1)
            self.note_renderer.quarter(x_pos=x_pos, y_pos=y_pos)
            self.__text_under_note(show_letter_only, word, x_pos, y_pos)

        for index, word in enumerate(["Fadas", "Adoram", "Cantar", "Encantos"]):
            x_pos = (self.screen.get_width() // 2) + index * horizontal_spacing
            y_pos = (
                    self.staff.c3_position
                    - (self.staff.line_spacing * (index + 1))
                    - self.staff.note_spacing
            )

            self.note_renderer.quarter(x_pos=x_pos, y_pos=y_pos)
            self.__text_under_note(show_letter_only, word, x_pos, y_pos)

    def __text_under_note(self, show_letter_only, word, x_pos, y_pos):
        text = pygame.font.Font(None, 24).render(
            word if show_letter_only else word[0], True, "black"
        )
        text_surface = text.convert_alpha()
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x_pos + 2, y_pos + (self.staff.note_spacing * 2) + 2)
        pygame.draw.rect(self.screen, "white", text_rect)
        self.screen.blit(text_surface, text_rect.topleft)

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
            on_click=self.__continue,
            pos=(width // 2 + 200 - (font.size("Não")[0] // 2), height // 2),
        )

        confirm_button.render()
        continue_button.render()

        self.events = [confirm_button.event_check, continue_button.event_check]

    def __see_again(self):
        self.events = [self.button.event_check]
        self.pg_count = 0

    def __continue(self):
        if not save_exists():
            create_save()
        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))

    def event_check(self, event_arg: Event | None = None) -> None:
        for item in self.events:
            item(event_arg)
