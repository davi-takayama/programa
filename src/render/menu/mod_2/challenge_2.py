import random
from typing import List

import numpy as np
from pygame import Surface
from pygame.event import Event

from src.utils.button import Button
from src.utils.challenge_model import ChallengeBase
from src.utils.save_operations.read_save import Save


class Challenge2(ChallengeBase):
    def __init__(self, screen: Surface, change_state, chapter_index: int, num_challenges: int = 10) -> None:
        super().__init__(screen, change_state, chapter_index, num_challenges=num_challenges)
        self.get_random_time_signature()
        self.staff.time_signature = self.time_signature
        self.notes = []
        self.notes_and_pauses = []
        self.get_random_notes()
        self._continue = False
        self.notes_dict = {
            1: self.note_renderer.whole,
            0.5: self.note_renderer.half,
            0.25: self.note_renderer.quarter,
            0.125: self.note_renderer.single_eighth
        }
        self.pauses_dict = {1: 0, 0.5: 1, 0.25: 2, 0.125: 3}

        self.buttons = self.init_buttons()
        self.continue_button = self.init_continue_button(self.click_continue)
        self.feedback_text = ""

        self.end_button = self.init_end_button(self.click_end)

    def render(self):
        self.screen.fill("white")
        if self.current_challenge != self.num_challenges:
            self.staff.render()
            self.go_back_button.render()

            notes_render_width = self.screen.get_width() - self.staff.trebble_cleff_asset.get_width() * 4

            self.render_notes(notes_render_width)
            if not self._continue:
                for button in self.buttons:
                    button.render()

                text = "Estas notas fecham o compasso da assinatura de tempo?"
                text_render = self.font.render(text, True, "black")
                self.screen.blit(text_render,
                                 (self.screen.get_width() // 2 - text_render.get_width() // 2, self.screen.get_height() // 2))

            else:
                text_render = self.font.render(self.feedback_text, True, "black")
                self.screen.blit(text_render,
                                 (self.screen.get_width() // 2 - text_render.get_width() // 2, self.screen.get_height() // 2))

                self.continue_button.render()

            self.render_challenge_info()
        else:
            self.end_render()
            self.end_button.render()

    def event_check(self, event_arg: Event | None = None):
        if self.current_challenge != self.num_challenges:
            self.go_back_button.event_check(event_arg)
            for button in self.buttons:
                button.event_check(event_arg)

            if self._continue:
                self.continue_button.event_check(event_arg)
        else:
            self.end_button.event_check(event_arg)

    def render_notes(self, width):
        x_positions = [
            (self.staff.trebble_cleff_asset.get_width()) + i * (width // len(self.notes) + 1) for i in
            range(1, len(self.notes) + 1)
        ]
        y_pos = int(self.staff.c3_position - self.staff.line_spacing * 2.5)

        def render_eighth_note(x_pos, i):
            if not self.notes_and_pauses[i]:
                self.note_renderer.pause(x_pos[i], 3, shift=True)
            else:
                if i + 1 < len(self.notes) and self.notes_and_pauses[i + 1] and np.isclose(
                        self.notes[i + 1], 0.125, rtol=1e-09, atol=1e-09):
                    self.note_renderer.eighth([(x_pos[i], y_pos), (x_pos[i + 1], y_pos)])
                elif i - 1 >= 0 and self.notes_and_pauses[i - 1] and np.isclose(
                        self.notes[i - 1], 0.125, rtol=1e-09, atol=1e-09):
                    return
                else:
                    self.note_renderer.eighth([(x_pos[i], y_pos)])

        def render_note_or_pause(x_pos, i, render_note_method, pause_arg):
            if self.notes_and_pauses[i]:
                render_note_method(x_pos[i], y_pos)
            else:
                self.note_renderer.pause(x_pos[i], pause_arg, shift=True)

        for i in range(len(self.notes)):
            if np.isclose(self.notes[i], 0.125, rtol=1e-09, atol=1e-09):
                render_eighth_note(x_positions, i)
            elif np.isclose(self.notes[i], 0.25, rtol=1e-09, atol=1e-09):
                render_note_or_pause(x_positions, i, self.note_renderer.quarter, 2)
            elif np.isclose(self.notes[i], 0.5, rtol=1e-09, atol=1e-09):
                render_note_or_pause(x_positions, i, self.note_renderer.half, 1)
            else:
                render_note_or_pause(x_positions, i, self.note_renderer.whole, 0)

    def get_random_time_signature(self):
        upper_numbers = [2, 3, 4, 6, 8]
        lower_numbers = [2, 4, 8]
        upper_num = random.choice(upper_numbers)
        lower_num = random.choice(lower_numbers)
        if lower_num == 8 and upper_num == 2:
            upper_num = 4
        if lower_num == 2 and upper_num == 8:
            lower_num = 4
        self.time_signature = upper_num, lower_num

    def get_random_notes(self):
        time_values = [1, 0.5, 0.25, 0.125]
        time_sig_value = self.time_signature[0] / self.time_signature[1]
        num_notes = random.randint(2, min(int(8 * time_sig_value), 8))

        def adjust_values(values):
            for index, value in enumerate(values):
                if sum(values) < time_sig_value:
                    values[index] = random.choice([v for v in time_values if v >= value])
                else:
                    values[index] = random.choice([v for v in time_values if v <= value])
            return values

        notes_list = [random.choice(time_values) for _ in range(num_notes)]
        while sum(notes_list) != time_sig_value:
            notes_list = adjust_values(notes_list)

        if not bool(random.getrandbits(1)):
            notes_list[random.randint(0, len(notes_list) - 1)] = random.choice(time_values)

        self.notes = notes_list
        notes_and_pauses_list = [random.choice([True, False]) for _ in range(len(self.notes))]

        for i in range(len(notes_and_pauses_list) - 1):
            if not notes_and_pauses_list[i] and not notes_and_pauses_list[i + 1]:
                notes_and_pauses_list[i + 1] = True

        self.notes_and_pauses = notes_and_pauses_list

    def init_buttons(self) -> List[Button]:
        def button_callback(value: bool):
            if (sum(self.notes) == self.time_signature[0] / self.time_signature[1]) == value:
                self.score += 1
                if value:
                    self.feedback_text = "Correto! Estas notas fecham um compasso da assinatura de tempo!"
                else:
                    if sum(self.notes) < self.time_signature[0] / self.time_signature[1]:
                        self.feedback_text = "Correto! Estas notas não fecham um compasso da assinatura de tempo!"
                    else:
                        self.feedback_text = "Correto! Estas notas passam de um compasso da assinatura de tempo!"
                self.correct_se.play()
            else:
                self.feedback_text = (
                    f"Incorreto! As notas somam {sum(self.notes) * self.time_signature[1]} tempos e o compasso requer "
                    f"{self.time_signature[0]} tempos.")
                self.incorrect_se.play()

            self._continue = True

        x_pos = [int((self.screen.get_width() / 3) * i) for i in range(1, 3)]
        y_pos = self.screen.get_height() // 4 * 3

        return [
            Button(
                self.screen,
                (x_pos[i] - (self.font.size("Correto" if i == 0 else "Incorreto")[0] // 2), y_pos),
                "Correto" if i == 0 else "Incorreto",
                self.font,
                lambda i_=i: button_callback(i_ == 0)
            )
            for i in range(2)
        ]

    def click_continue(self):
        self.current_challenge += 1
        self._continue = False
        self.get_random_time_signature()
        self.staff.time_signature = self.time_signature
        self.notes = []
        self.get_random_notes()

    def click_end(self):
        save = Save.load()
        chapter = save.md2.chapters[self.chapter_index]

        chapter["completed"] = self.score >= int(self.num_challenges * 0.7)
        chapter["perfected"] = self.score == self.num_challenges

        save.save()
        from ..main_menu import Menu
        self.change_state(Menu(self.screen, self.change_state))
