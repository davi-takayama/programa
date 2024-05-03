from random import randint
from typing import List

import click
from numpy import size
from pygame import Surface
from pygame.font import Font

from ....utils.button import Button
from ....utils.note_renderer import NoteRenderer
from ....utils.save_operations.read_save import Chapter, Save
from ...renderable import Renderable
from ...staff import Staff


class Challenge1(Renderable):
    def __init__(
        self, screen: Surface, change_state: classmethod, chapter_index: int
    ) -> None:
        super().__init__(screen, change_state)
        self.screen = screen
        self.change_state = change_state
        self.__staff = Staff(screen, self.screen.get_height() // 3, (4, 4))
        self.__staff_notes = ["E", "F", "G", "A", "B", "C", "D", "E", "F"]
        self.__num_challenges = 10
        self.__completed_challenges = 0
        self.score = 0
        self.__font = Font(None, 32)
        self.__current_note = self.__pick_random_note()
        self.__continue = False
        self.__note_buttons: List[Button] = []
        self.__init_note_buttons()
        self.__end_button = self.__init_end_button()
        self.__note_renderer = NoteRenderer(screen, self.__staff.c3_position)
        self.__continue_button = self.__init_continue_button()
        self.__continue_text = ""
        self.__chapter_index = chapter_index

    def render(self):
        if self.__completed_challenges == self.__num_challenges:
            self.final_screen()
        else:
            self.__challenges()

    def __challenges(self):
        self.screen.fill("white")
        self.__staff.render()

        self.__note_renderer.quarter(
            x_pos=self.__staff.trebble_cleff_asset.get_width() * 2 + 10,
            y_pos=(self.__staff.c3_position - self.__staff.note_spacing * 2)
            - self.__current_note[1] * self.__staff.note_spacing,
            has_sharp=0,
        )

        text = "Qual nota está sendo exibida?"
        width, _ = self.__font.size(text)
        self.screen.blit(
            self.__font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2),
            ),
        )

        if not self.__continue:
            for button in self.__note_buttons:
                button.render()
        else:
            text_width, text_height = self.__font.size(self.__continue_text)
            text_x = self.screen.get_width() // 2 - text_width // 2
            text_y = self.__continue_button.pos[1] - text_height - 10
            self.screen.blit(
                self.__font.render(self.__continue_text, True, "black"),
                (text_x, text_y),
            )

            self.__continue_button.render()

    def __init_continue_button(self):

        def click_continue():
            self.__current_note = self.__pick_random_note()
            self.__continue = False
            self.__completed_challenges += 1

        return Button(
            font=self.__font,
            text="Continuar",
            on_click=click_continue,
            pos=(
                self.screen.get_width() // 2
                - (self.__font.size("Continuar")[0] // 2)
                - 10,
                self.screen.get_height() - 50,
            ),
            screen=self.screen,
        )

    def __init_note_buttons(self):

        def __check_answer(text: str):
            if text == self.__current_note[0]:
                self.score += 1
                self.__continue_text = "Correto!"
            else:
                self.__continue_text = (
                    "Incorreto! A resposta correta era: " + self.__current_note[0]
                )
            self.__continue = True

        buttons = []

        for index, letter in enumerate(["C", "D", "E", "F", "G", "A", "B"]):
            button = Button(
                font=self.__font,
                text=letter,
                on_click=lambda letter=letter: __check_answer(letter),
                pos=(
                    (self.screen.get_width() // 8 * (index + 1)) - 25,
                    self.screen.get_height() // 4 * 3,
                ),
                screen=self.screen,
            )
            buttons.append(button)

        self.__note_buttons = buttons

    def __init_end_button(self):
        def click_end():
            print("score", self.score, "num_challenges", self.__num_challenges)
            save = Save.load()
            chapter = save.md1.chapters[self.__chapter_index]

            if self.score >= int(self.__num_challenges * 0.7):
                chapter["completed"] = True
                if self.score == self.__num_challenges:
                    chapter["perfected"] = True
                if self.__chapter_index + 1 < len(save.md1.chapters):
                    next_chapter = save.md1.chapters[self.__chapter_index + 1]
                    next_chapter["unlocked"] = True
                else:
                    save.md1["completed"] = True
                    save.md2["unlocked"] = True
            chapter["score"] = (
                self.score if self.score > chapter["score"] else chapter["score"]
            )
            save.md1.chapters[0] = chapter
            save.save()
            from ..main_menu import Menu

            self.change_state(Menu(self.screen, self.change_state))

        button_text = "Voltar ao menu"
        button_x = self.screen.get_width() // 2 - self.__font.size(button_text)[0] // 2
        button_y = (self.screen.get_height() // 4) * 3

        return Button(
            self.screen, (button_x, button_y), button_text, self.__font, click_end
        )

    def __pick_random_note(self):
        num = randint(0, len(self.__staff_notes) - 1)
        return (self.__staff_notes[num], num)

    def final_screen(self):
        self.screen.fill("white")
        text = "Parabéns! Você completou o capítulo!"
        width, _ = self.__font.size(text)
        self.screen.blit(
            self.__font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 3),
            ),
        )

        text = (
            "Sua pontuação foi: " + str(self.score) + "/" + str(self.__num_challenges)
        )
        width, _ = self.__font.size(text)
        self.screen.blit(
            self.__font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2),
            ),
        )
        self.__end_button.render()

    def event_check(self, event):
        if self.__completed_challenges == self.__num_challenges:
            self.__end_button.event_check(event)
        else:
            if not self.__continue:
                for button in self.__note_buttons:
                    button.event_check(event)
            else:
                self.__continue_button.event_check(event)
