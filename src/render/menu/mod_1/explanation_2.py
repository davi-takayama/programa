import textwrap
from typing import Literal

import pygame
from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from src.render.staff import Staff
from src.utils.bottom_screen_button import bottom_screen_button
from src.utils.button import Button
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable


class Explanation2(Renderable):
    def __init__(self, screen: Surface, change_state) -> None:
        super().__init__(screen, change_state)
        self.note_renderer = NoteRenderer(screen)
        self.staff = Staff(screen, time_signature=(4, 4))
        self.pg_count = 0
        self.top_text = [
            "Anteriormente foi explicado que existiam 7 notas distribuidas nas linhas e espaços da pauta.",
            "Na escala cromática (que tem todas as notas), existem 12 notas, sendo 7 naturais e 5 acidentadas.",
            "Percebe-se que as notas E e B não possuem sustenidos (meio tom acima), e as notas F e C não possuem bemóis (meio tom "
            "abaixo)"
        ]
        self.bottom_text = [
            "No entanto, estas 7 notas são as notas naturais.",
            "Nesta, temos as notas C, C#/Db, D, D#/Eb, E, F, F#/Gb, G, G#/Ab, A, A#/Bb, B.",
            "já que não possuem notas "
            "Isso acontece porquê esses pares não possuem meio tom entre si.",
        ]

        def __on_click_continue():
            if self.pg_count < self.bottom_text.__len__():
                self.pg_count += 1
            else:
                self.__see_again()

        self.button: Button = bottom_screen_button(
            screen=screen,
            on_click=__on_click_continue,
        )

        self.events = [self.button.event_check]

    def render(self) -> None:
        self.screen.fill("white")
        if self.pg_count < len(self.bottom_text):
            self.button.render()
            self.staff.render(render_cleff=True, render_time_signature=True, )
            top_text = (self.top_text[self.pg_count] if self.pg_count < len(self.top_text) else "")
            bottom_text = (self.bottom_text[self.pg_count] if self.pg_count < len(self.bottom_text) else "")
            font = Font(None, 38)

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
                    (self.screen.get_height() // 2 + 100) + (index * (font.size(text)[1] + 10)))
                self.screen.blit(text_surface, text_rect.topleft)

            if self.pg_count == 0:
                self.__render_pg_count_0()

            elif self.pg_count == 1:
                self.__render_pg_count_1()

            elif self.pg_count == 2:
                self.__render_pg_count_2()

        else:
            self.__end_explanation()

    def __render_pg_count_0(self):
        for i, letter in enumerate(["C", "D", "E", "F", "G", "A", "B"]):
            x = 100 + 50 * i
            y = self.staff.c3_position - (i * self.staff.note_spacing)
            self.note_renderer.quarter(x_pos=x, y_pos=y, color="black")
            self.__text_under_note(letter, x, y)

    def __render_pg_count_1(self):
        index = -1
        for i, letter in enumerate(["C", "C#/Db", "D", "D#/Eb", "E", "F", "F#/Gb", "G", "G#/Ab", "A", "A#/Bb", "B"]):
            index += 1 if letter.find("#") == -1 else 0
            x = 100 + 50 * i
            y = self.staff.c3_position - (index * self.staff.note_spacing)
            has_sharp: Literal['sharp', 'none'] = 'sharp' if letter.find("#") != -1 else 'none'
            color = 'forestgreen' if letter.find("#") != -1 else 'black'
            self.note_renderer.quarter(x_pos=x, y_pos=y, color=color, has_sharp=has_sharp)
            self.__text_under_note(letter, x, y, color)

    def __render_pg_count_2(self):
        wid = self.screen.get_width() // 2
        x_pos = [
            (wid // 2) + (wid // 15 * i) for i in range(15)
        ]
        y_pos = self.staff.c3_position

        def draw_vertical_line(x_position):
            pygame.draw.line(
                self.screen,
                "black",
                (x_position, self.staff.line_positions[0]),
                (x_position, self.staff.line_positions[-1]),
                3,
            )

        def draw_equals(x_position, y_position):
            eq = pygame.font.Font(None, 24).render("=", True, "black", "white")
            eq_rect = eq.get_rect()
            eq_rect.topleft = (x_position + 2, y_position + 2)
            self.screen.blit(eq, eq_rect.topleft)

        self.note_renderer.quarter(x_pos=x_pos[0], y_pos=y_pos - self.staff.note_spacing * 2, color="black", has_sharp="sharp")
        draw_equals(x_pos[1], y_pos - self.staff.note_spacing * 4)
        self.note_renderer.quarter(x_pos=x_pos[2], y_pos=y_pos - self.staff.note_spacing * 3, color="black")
        draw_vertical_line(x_pos[3])
        self.note_renderer.quarter(x_pos=x_pos[4], y_pos=y_pos - self.staff.note_spacing * 6, color="black", has_sharp="sharp")
        draw_equals(x_pos[5], y_pos - self.staff.note_spacing * 8)
        self.note_renderer.quarter(x_pos=x_pos[6], y_pos=y_pos - self.staff.note_spacing * 7, color="black")
        draw_vertical_line(x_pos[7])
        self.note_renderer.quarter(x_pos=x_pos[8], y_pos=y_pos - self.staff.note_spacing * 3, color="black", has_sharp="flat")
        draw_equals(x_pos[9], y_pos - self.staff.note_spacing * (3 + 1))
        self.note_renderer.quarter(x_pos=x_pos[10], y_pos=y_pos - self.staff.note_spacing * 2, color="black")
        draw_vertical_line(x_pos[11])
        self.note_renderer.quarter(x_pos=x_pos[12], y_pos=y_pos - self.staff.note_spacing * 7, color="black", has_sharp="flat")
        draw_equals(x_pos[13], y_pos - self.staff.note_spacing * (7 + 1))
        self.note_renderer.quarter(x_pos=x_pos[14], y_pos=y_pos - self.staff.note_spacing * 6, color="black")


    def __text_under_note(self, word_param, x_pos_param, y_pos_param, color_param="black"):
        text = pygame.font.Font(None, 24).render(word_param, True, color_param)
        text_surface = text.convert_alpha()
        text_rect = text_surface.get_rect()
        text_rect.topleft = (x_pos_param + 2, y_pos_param + (self.staff.note_spacing * 2) + 2)
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

        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))

    def event_check(self, event_arg: Event | None = None):
        for item in self.events:
            item(event_arg)
