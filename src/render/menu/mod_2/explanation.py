import textwrap

import pygame
from pygame import Surface
from pygame.event import Event

from ...staff import Staff
from ....utils.bottom_screen_button import bottom_screen_button
from ....utils.button import Button
from ....utils.note_renderer import NoteRenderer
from ....utils.renderable import Renderable
from ....utils.save_operations.read_save import Save


class Explanation2(Renderable):
    def __init__(self, screen: Surface, change_state: classmethod) -> None:
        super().__init__(screen, change_state)
        self.staff = Staff(screen=screen, time_signature=(4, 4))
        self.pg_count = 0
        self.__top_text = [
            "Você deve ter percebido que algumas das notas são representadas de formas diferentes.",
            "A duração das notas depende da assinatura de tempo. cada número nesta indica uma coisa diferente.",
            "A assinatura abaixo é a mais comum. quando uma partitura a omite, assume-se que esta seja a assinatura usada.",
            "Em qualquer marcação temos as seguintes proporções entre as notas:",
            "Para agrupar corretamente as notas em um compasso, devemos seguir o número de cima da assinatura de tempo.",
            "Deste modo, no tempo de 6/4 esta regra segue a mesma, mas com 6 batidas em vez de 4"
        ]
        self.__bottom_text = [
            "A forma como cada uma é mostrada indica a duração dela.",
            "As músicas são regradas por uma medida de tempo medida em BPM (Batidas Por Minuto).",
            "O número de cima indica quantas batidas tem um compasso enquanto o de baixo indica o valor que as notas assumem.",
            "Enquanto a primeira nota tem valor inteiro (4 tempos), as seguintes têm metade, um quarto, um oitavo e assim por diante.",
            "número de batidas por compasso: 4\nnúmero de batidas por compasso: 6",
            "número de batidas por compasso: 4\nnúmero de batidas por compasso: 6"
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

    def render(self) -> None:
        self.screen.fill("white")
        if self.pg_count < len(self.__top_text):
            self.button.render()

            time_signature_color = ("black", "black")
            if self.pg_count == 2:
                time_signature_color = ("forestgreen", "forestgreen")
            elif self.pg_count == 4:
                time_signature_color = ("forestgreen", "black")
            elif self.pg_count == 5:
                time_signature_color = ("forestgreen", "black")
                self.staff.time_signature = (6, 4)

            self.staff.render(
                time_signature_color=time_signature_color
            )
            top_text = (
                self.__top_text[self.pg_count]
                if self.pg_count < len(self.__top_text)
                else ""
            )
            bottom_text = (
                self.__bottom_text[self.pg_count].split("\n")
                if self.pg_count < len(self.__bottom_text)
                else ""
            )
            font = pygame.font.Font(None, 38)

            self.__render_text(bottom_text, font, top_text)

            y = self.staff.c3_position - (2.5 * self.staff.line_spacing)
            width = (self.screen.get_width() / 4) * 3

            if self.pg_count < 2:
                x_positions = [
                    50 + int((width // 10) * (i + 1)) for i in range(9)
                ]

                self.note_renderer.whole(x_positions[0], y)
                self.note_renderer.half(x_positions[1], y)
                self.note_renderer.quarter(x_positions[2], y)
                self.note_renderer.eighth([(x_positions[3], y), (x_positions[4], y)])
                self.note_renderer.eighth(
                    [(x_positions[5], y), (x_positions[6], y), (x_positions[7], y), (x_positions[8], y)],
                    sixteenth=True,
                )

            elif self.pg_count == 3:
                x_positions = [
                    75 + int((width // 19) * (i + 1)) for i in range(18)
                ]
                self.__render_notes_1(x_positions, y)

            elif self.pg_count == 4 or self.pg_count == 5:
                x_positions = [
                    100 + int((width // 14) * (i + 1)) for i in range(13)
                ]
                self.__render_notes_2(x_positions, y)

        else:
            self.__end_explanation()

    def __render_notes_1(self, x_positions, y):
        def render_equals_char(text, x, y_):
            temp_font = pygame.font.Font(None, 32)
            text_surface = temp_font.render(text, True, "black")
            text_rect = text_surface.get_rect()
            text_rect.x = x
            text_rect.centery = y_
            self.screen.blit(text_surface, text_rect)

        self.note_renderer.whole(x_positions[0], y)
        render_equals_char("=", x_positions[1] + 4, y)
        for i in range(2, 4):
            self.note_renderer.half(x_positions[i], y)
        render_equals_char("=", x_positions[4] + 4, y)
        for i in range(5, 9):
            self.note_renderer.quarter(x_positions[i], y)
        render_equals_char("=", x_positions[9] + 4, y)
        coords = []
        for i in range(10, 18):
            coords.append((x_positions[i], y))
        self.note_renderer.eighth(coords)

    def __render_notes_2(self, x_positions, y):
        def draw_line(x_position):
            pygame.draw.line(self.screen, "black", (x_position, self.staff.c3_position - self.staff.line_spacing),
                             (x_position, self.staff.c3_position - (self.staff.line_spacing * 5)), 3)

        middle_point = (len(x_positions) // 2) + 1
        distance_to_middle = abs(x_positions[middle_point] - self.screen.get_width() // 2)
        x_positions = [x + distance_to_middle for x in x_positions]

        self.note_renderer.whole(x_positions[0], y)
        draw_line(x_positions[1] + 8)
        self.note_renderer.half(x_positions[2], y)
        self.note_renderer.quarter(x_positions[3], y)
        self.note_renderer.quarter(x_positions[4], y)
        draw_line(x_positions[5] + 8)
        self.note_renderer.eighth([(x_positions[6], y), (x_positions[7], y)])
        self.note_renderer.quarter(x_positions[8], y)
        self.note_renderer.quarter(x_positions[9], y)
        self.note_renderer.half(x_positions[10], y)
        self.note_renderer.quarter(x_positions[11], y)
        draw_line(x_positions[12] + 8)

        distance = abs(x_positions[0] - x_positions[5]) - 20
        line_1_color = "forestgreen" if self.pg_count == 4 else "red"
        pygame.draw.arc(self.screen, line_1_color, (x_positions[0] + 10, self.staff.c3_position, distance, 20), 3.14, 0, 3)

        distance = abs(x_positions[5] - x_positions[-2]) - 20
        line_2_color = "forestgreen" if self.pg_count == 5 else "red"
        pygame.draw.arc(self.screen, line_2_color, (x_positions[6] + 10, self.staff.c3_position, distance, 20), 3.14, 0, 3)

    def __render_text(self, bottom_text, font, top_text):
        for index, text in enumerate(textwrap.wrap(top_text, width=50)):
            text_surface = font.render(text, True, "black")
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.screen.get_width() // 2
            text_rect.top = 50 + (index * (font.size(text)[1] + 10))
            self.screen.blit(text_surface, text_rect)
        if isinstance(bottom_text, list):
            for index, text in enumerate(textwrap.wrap(bottom_text[0], width=20 if len(bottom_text) > 1 else 50)):
                text_surface = font.render(text, True, "black")
                text_rect = text_surface.get_rect()
                text_rect.centerx = self.screen.get_width() // (4 if len(bottom_text) > 1 else 2)
                text_rect.topleft = (
                    text_rect.centerx - text_rect.width // 2,
                    (self.screen.get_height() // 2 + 75)
                    + (index * (font.size(text)[1] + 10)),
                )
                self.screen.blit(text_surface, text_rect.topleft)
            if len(bottom_text) > 1:
                for index, text in enumerate(textwrap.wrap(bottom_text[1], width=25)):
                    text_surface = font.render(text, True, "black")
                    text_rect = text_surface.get_rect()
                    text_rect.centerx = (self.screen.get_width() // 4) * 3
                    text_rect.topleft = (
                        text_rect.centerx - text_rect.width // 2,
                        (self.screen.get_height() // 2 + 75)
                        + (index * (font.size(text)[1] + 10)),
                    )
                    self.screen.blit(text_surface, text_rect.topleft)

    def __end_explanation(self):
        text = "Gostaria de rever a explicação?"
        width, height = self.screen.get_size()
        font = pygame.font.Font(None, 32)
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
        save = Save.load()
        chapter = save.md2.chapters[0]
        chapter["unlocked"] = True
        save.md2.chapters[0] = chapter
        save.save()
        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))

    def event_check(self, event_arg: Event | None = None):
        for item in self.events:
            item(event_arg)
