import textwrap

import pygame
from pygame import Surface
from pygame.event import Event
from pygame.font import Font

from src.render.staff import Staff
from src.utils.bottom_screen_button import bottom_screen_button
from src.utils.button import Button
from src.utils.metronome import Metronome
from src.utils.note_renderer import NoteRenderer
from src.utils.renderable import Renderable
from src.utils.save_operations.read_save import Save


class Explanation(Renderable):
    def __init__(self, screen: Surface, change_state) -> None:
        super().__init__(screen, change_state)
        self.pg_count = 0
        print("iniciado")
        self.__top_text = [
            "Anteriormente foi visto que existem diferentes durações de notas e pausas.",
            "O uso de um metrônomo é de grande importância para garantir constância no rítmo.",
            "Existem vários metrônomos disponíveis, desde os mecânicos até os digitais.",
            "Os metrônomos digitais são mais comuns e possuem mais funcionalidades, como emitir sons diferentes para cada batida.",
        ]
        self.__bottom_text = [
            "A duração de uma nota ou pausa é regrada por algo chamado de 'metrônomo'.",
            "Ele é um dispositivo que emite um som em intervalos regulares, indicando a velocidade da música.",
            "Mas todos eles operam da mesma forma: em batidas por minuto (BPM).",
            "Tente alterar os parâmetros do metrônomo e veja como esses elementos se comportam.",
        ]

        def click_continue():
            if self.pg_count < len(self.__top_text):
                self.pg_count += 1
                if self.pg_count == 2:
                    self.__metronome.playing = True
                elif self.pg_count == 4:
                    self.__metronome.playing = False
            else:
                self.__end_explanation()

        self.__button: Button = bottom_screen_button(
            screen=screen,
            on_click=click_continue,
        )
        self.events = [self.__button.event_check]

        self.__staff = Staff(screen)
        self.note_renderer = NoteRenderer(screen, self.__staff.c3_position)
        self.__metronome = Metronome()
        self.__metronome.start()

    def __del__(self):
        self.__playing_metronome = False
        self.__metronome.join()

    def render(self):
        self.screen.fill("white")

        if self.pg_count < len(self.__top_text):
            self.__button.render()
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
            font = Font(None, 34)
            self.__render_text(bottom_text, font, top_text)

            if self.pg_count < 2:
                self.__staff.render()
                y_pos = self.__staff.line_positions[2] + self.__staff.note_spacing
                x_positions = [
                    self.screen.get_width() // 9 * i for i in range(1, 9)
                ]
                self.note_renderer.whole(x_positions[0], y_pos)
                self.note_renderer.half(x_positions[1], y_pos)
                self.note_renderer.quarter(x_positions[2], y_pos)
                self.note_renderer.eighth([(x_positions[3], y_pos)], 0)
                self.note_renderer.pause(x_positions[4], 0)
                self.note_renderer.pause(x_positions[5], 1)
                self.note_renderer.pause(x_positions[6], 2)
                self.note_renderer.pause(x_positions[7], 3)

            # elif self.pg_count == 2:
            #     self.__metronome.playing = True

        else:
            self.__end_explanation()

    def event_check(self, event_arg: Event | None = None):
        if self.pg_count < len(self.__top_text):
            self.__button.event_check(event_arg)
        if event_arg == pygame.QUIT:
            self.__metronome.playing = False
            self.__metronome.join()

        if self.pg_count == len(self.__top_text):
            for event in self.events:
                event(event_arg)

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

    def __see_again(self):
        self.events = [self.__button.event_check]
        self.pg_count = 0

    def __end_explanation(self):
        text = "Gostaria de rever a explicação?"
        width, height = self.screen.get_size()
        font = Font(None, 32)
        text_width, text_height = font.size(text)
        self.screen.blit(
            font.render(text, True, "black"),
            (
                (width // 2) - (text_width // 2),
                (height // 4) - (text_height // 2),
            ),
        )

        def __exit():
            save = Save.load()
            save.md2.chapters[3]["unlocked"] = True
            save.save()
            from ..main_menu import Menu

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
            on_click=__exit,
            pos=(width // 2 + 200 - (font.size("Não")[0] // 2), height // 2),
        )

        confirm_button.render()
        continue_button.render()

        self.events = [confirm_button.event_check, continue_button.event_check]
