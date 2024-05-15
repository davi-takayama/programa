import random
from typing import List

from pygame import Surface
from pygame.event import Event

from src.utils.button import Button
from src.utils.challenge_model import ChallengeBase
from src.utils.save_operations.read_save import Save


class Challenge2(ChallengeBase):
    def __init__(self, screen: Surface, change_state, chapter_index: int, num_challenges: int = 10) -> None:
        super().__init__(screen, change_state, chapter_index, num_challenges=num_challenges)
        self.__get_random_time_signature()
        self.staff.time_signature = self.__time_signature
        self.notes = []
        self.__notes_and_pauses = []
        self.get_random_notes()
        self.__continue = False
        self.notes_dict = {
            1: self.note_renderer.whole,
            0.5: self.note_renderer.half,
            0.25: self.note_renderer.quarter,
            0.125: self.note_renderer.single_eighth
        }
        self.pauses_dict = {1: 0, 0.5: 1, 0.25: 2, 0.125: 3}

        self.buttons = self.__init_buttons()
        self.__continue_button = self.init_continue_button(self.__click_continue)
        self.__feedback_text = ""

        self.__end_button = self.init_end_button(self.__click_end)

    def render(self):
        self.screen.fill("white")
        if self.current_challenge != self.num_challenges:
            self.staff.render(self.screen)
            self.go_back_button.render()

            notes_render_width = self.screen.get_width() - self.staff.trebble_cleff_asset.get_width() * 4

            self.__render_notes(notes_render_width)
            if not self.__continue:
                for button in self.buttons:
                    button.render()

                text = "Estas notas fecham o compasso da assinatura de tempo?"
                text_render = self.font.render(text, True, "black")
                self.screen.blit(text_render,
                                 (self.screen.get_width() // 2 - text_render.get_width() // 2, self.screen.get_height() // 2))

            else:
                text_render = self.font.render(self.__feedback_text, True, "black")
                self.screen.blit(text_render,
                                 (self.screen.get_width() // 2 - text_render.get_width() // 2, self.screen.get_height() // 2))

                self.__continue_button.render()
        else:
            self.end_render()
            self.__end_button.render()

    def event_check(self, event_arg: Event | None = None):
        if self.current_challenge != self.num_challenges:
            self.go_back_button.event_check(event_arg)
            for button in self.buttons:
                button.event_check(event_arg)

            if self.__continue:
                self.__continue_button.event_check(event_arg)
        else:
            self.__end_button.event_check(event_arg)

    def __render_notes(self, width):
        x_positions = [
            (self.staff.trebble_cleff_asset.get_width()) + i * (width // len(self.notes) + 1) for i in
            range(1, len(self.notes) + 1)
        ]
        y_pos = self.staff.c3_position - self.staff.line_spacing * 2.5
        for i, note in enumerate(self.notes):
            if self.__notes_and_pauses[i]:
                self.notes_dict[note](x_positions[i], y_pos)
            else:
                self.note_renderer.pause(x_positions[i], self.pauses_dict[note])

    def __get_random_time_signature(self):
        upper_numbers = [2, 3, 4, 6, 8]
        lower_numbers = [2, 4, 8]

        self.__time_signature = random.choice(upper_numbers), random.choice(lower_numbers)

    def get_random_notes(self):
        time_values = [1, 0.5, 0.25, 0.125]
        time_sig_value = self.__time_signature[0] / self.__time_signature[1]
        num_notes = random.randint(2, min((8 * time_sig_value), 12))

        def adjust_values(values):
            for i, value in enumerate(values):
                if sum(values) < time_sig_value:
                    values[i] = random.choice([v for v in time_values if v >= value])
                else:
                    values[i] = random.choice([v for v in time_values if v <= value])
            return values

        notes_list = [random.choice(time_values) for _ in range(num_notes)]
        while sum(notes_list) != time_sig_value:
            notes_list = adjust_values(notes_list)

        if not bool(random.getrandbits(1)):
            notes_list[random.randint(0, len(notes_list) - 1)] = random.choice(time_values)

        self.notes = notes_list
        self.__notes_and_pauses = [random.choice([True, False]) for _ in range(len(self.notes))]

    def __init_buttons(self) -> List[Button]:
        def button_callback(value: bool):
            if (sum(self.notes) == self.__time_signature[0] / self.__time_signature[1]) == value:
                self.score += 1
                if value:
                    self.__feedback_text = "Correto! Estas notas fecham um compasso da assinatura de tempo!"
                else:
                    if sum(self.notes) < self.__time_signature[0] / self.__time_signature[1]:
                        self.__feedback_text = "Correto! Estas notas não fecham um compasso da assinatura de tempo!"
                    else:
                        self.__feedback_text = "Correto! Estas notas passam de um compasso da assinatura de tempo!"
            else:
                self.__feedback_text = (
                    f"Incorreto! As notas somam {sum(self.notes) * self.__time_signature[1]} tempos e o compasso requer {self.__time_signature[0]} tempos.")

            self.__continue = True

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

    def __click_continue(self):
        self.current_challenge += 1
        self.__continue = False
        self.__get_random_time_signature()
        self.staff.time_signature = self.__time_signature
        self.notes = []
        self.get_random_notes()

    def __click_end(self):
        save = Save.load()
        chapter = save.md2.chapters[self.chapter_index]

        chapter["completed"] = self.score >= int(self.num_challenges * 0.7)
        chapter["perfected"] = self.score == self.num_challenges

        if self.chapter_index + 1 < len(save.md2.chapters):
            save.md2.chapters[self.chapter_index + 1]["unlocked"] = chapter["completed"]
        else:
            save.md3.unlocked = chapter["completed"]

        save.save()
        from ..main_menu import Menu
        self.change_state(Menu(self.screen, self.change_state))
