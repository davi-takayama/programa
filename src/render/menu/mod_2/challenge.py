import random
from typing import List

import pygame
from pygame import Surface
from pygame.event import Event

from src.utils.button import Button
from src.utils.challenge_model import ChallengeBase
from src.utils.note_renderer import NoteRenderer
from src.utils.save_operations.read_save import Save


class Challenge(ChallengeBase):
    def __init__(
            self,
            screen: Surface,
            change_state,
            chapter_index: int,
            num_challenges: int = 10,
            unlock_next: bool = True,
            use_pauses: bool = False,
    ):
        super().__init__(screen, change_state, chapter_index, False, num_challenges)
        self.__use_pauses = use_pauses
        from typing import Dict, Callable

        self.__notes_dict: Dict[float, Callable] = {
            1.0: self.note_renderer.whole,
            0.5: self.note_renderer.half,
            0.25: self.note_renderer.quarter,
            0.125: self.note_renderer.single_eighth,
        }
        self.__chosen_notes = []
        self.__pushed_notes = []
        self.__note_buttons = self.__init_note_option_buttons() if not self.__use_pauses else self.__init_pause_option_buttons()
        self.__delete_button = self.__init_delete_button()
        self.__continue_button = self.init_continue_button(self.__click_continue)
        self.__pick_notes()
        self.__note_pos_area = abs(self.staff.trebble_cleff_asset.get_width() * 2.2 - self.screen.get_width() // 2)
        self.__end_button = self.init_end_button(self.__click_end)

    def render(self):
        self.screen.fill("white")
        if self.current_challenge < self.num_challenges:
            if len(self.__pushed_notes) < self.__num_notes_selected():
                self.__challenge_render()
            else:
                self.__continue_render()
            self.render_challenge_info()
        else:
            self.end_render()
            self.__end_button.render()

    def event_check(self, event_arg: Event | None = None):
        if self.num_challenges != self.current_challenge:
            self.go_back_button.event_check(event_arg)
            if len(self.__pushed_notes) < self.__num_notes_selected():
                for button in self.__note_buttons:
                    button.event_check(event_arg)
                self.__delete_button.event_check(event_arg)
            else:
                self.__continue_button.event_check(event_arg)
        else:
            self.__end_button.event_check(event_arg)

    def __challenge_render(self):
        self.staff.render()
        self.__cleff_notes_render()
        for button in self.__note_buttons:
            button.render()
        self.go_back_button.render()
        self.__delete_button.render()

        button_word = "notas" if not self.__use_pauses else "pausas"
        text = f"Selecione {self.__num_notes_selected()} {button_word} cujo valor seja igual às figuras da esquerda"
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2 + 20),
            ),
        )

    def __cleff_notes_render(self):
        def render_pause(x_pos, pause_key):
            match pause_key:
                case 1:
                    self.note_renderer.pause(x_pos, 0)
                case 0.5:
                    self.note_renderer.pause(x_pos, 1)
                case 0.25:
                    self.note_renderer.pause(x_pos, 2)
                case 0.125:
                    self.note_renderer.pause(x_pos, 3)

        note_y = int(self.staff.c3_position - self.staff.line_spacing * 2.5)
        for index, note in enumerate(self.__chosen_notes):
            x = (self.staff.trebble_cleff_asset.get_width() * 2.2) + (index * (self.__note_pos_area // len(self.__chosen_notes)))
            x = x if not self.__use_pauses else x + 20
            self.__notes_dict[note](x, note_y) if not self.__use_pauses else render_pause(x, note)
        pygame.draw.line(self.screen, "black", (self.screen.get_width() // 2, self.staff.line_positions[0]),
                         (self.screen.get_width() // 2, self.staff.line_positions[-1]), 5)
        for index, note in enumerate(self.__pushed_notes):
            x = (self.staff.trebble_cleff_asset.get_width() * 2.2) + (
                    index * (self.__note_pos_area // len(self.__pushed_notes))) + self.screen.get_width() // 2
            self.__notes_dict[note](int(x), note_y) if not self.__use_pauses else render_pause(x, note)

    def __continue_render(self):
        self.staff.render()
        self.go_back_button.render()
        self.__cleff_notes_render()
        self.__continue_button.render()
        text = "Correto!" if sum(self.__pushed_notes) == sum(self.__chosen_notes) else "Incorreto!"
        text = self.font.render(text, True, "black")
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 20))

    def __init_note_option_buttons(self) -> List[Button]:
        from typing import Dict, Callable
        from src.utils.note_renderer import NoteRenderer
        button_renderer = NoteRenderer(self.screen, draw_lines=False)
        notes_dict: Dict[float, Callable] = {
            1: button_renderer.whole,
            0.5: button_renderer.half,
            0.25: button_renderer.quarter,
            0.125: button_renderer.single_eighth,
        }

        def make_button_callback(value):
            return lambda: self.__pushed_notes.append(value)

        def override_button_render(button_arg, note_val, x_pos, increase_height):
            original_render = button_arg.render
            y_pos = self.screen.get_height() // 4 * 3

            if increase_height != 0:
                button_arg.height *= 2.5
            if increase_height == 3:
                button_arg.width *= 1.5

            def new_render():
                original_render()
                notes_dict[note_val](x_pos + 16, y_pos + 16)

            button_arg.render = new_render

        note_buttons = [
            self.__create_button(
                i, note, notes_dict, make_button_callback, override_button_render
            )
            for i, note in enumerate([1, 0.5, 0.25, 0.125])
        ]

        return note_buttons

    def __init_pause_option_buttons(self) -> List[Button]:
        note_renderer = NoteRenderer(self.screen, self.screen.get_height() // 9 * 8)
        notes_dict: dict[float, int] = {1: 0, 0.5: 1, 0.25: 2, 0.125: 3}

        def create_button(index, value):
            x = (self.screen.get_width() // 5) + (self.screen.get_width() // 4 * 3) // len(notes_dict) * index
            button = Button(
                self.screen,
                (x, self.screen.get_height() // 4 * 3),
                "     ",
                self.font,
                lambda: self.__pushed_notes.append(value)
            )
            button.height = int(button.height * 2.5)
            button.pos = (button.pos[0], button.pos[1] - 16)

            original_render = button.render

            def new_render():
                original_render()
                note_renderer.pause(x + 24, notes_dict[value])

            button.render = new_render

            return button

        return [create_button(index, value) for index, value in enumerate(notes_dict.keys())]

    def __create_button(
            self, i, note, notes_dict, make_button_callback, override_button_render
    ):
        note_callback = make_button_callback(note)
        button_x_pos = (self.screen.get_width() // 5) + (
                self.screen.get_width() // 4 * 3
        ) // len(notes_dict) * i
        button_y_pos = self.screen.get_height() // 4 * 3 - (32 if i != 0 else 0)
        button = Button(
            self.screen,
            (button_x_pos, button_y_pos),
            "     ",
            self.font,
            note_callback,
        )
        override_button_render(button, note, button_x_pos, i)
        return button

    def __pick_notes(self):
        nums = [
            random.choice(list(self.__notes_dict.keys()))
            for _ in range(self.__num_notes_selected())
        ]
        nums_dict = {1: 8, 0.5: 4, 0.25: 2, 0.125: 1}
        num_of_notes = sum([nums_dict[num] for num in nums])
        num_of_notes = random.randint(len(nums), num_of_notes)

        chosen_notes = []
        while sum(chosen_notes) < sum(nums):
            chosen_notes = [
                random.choice(list(self.__notes_dict.keys()))
                for _ in range(num_of_notes)
            ]

        max_iter = 500
        iters = 0
        while sum(chosen_notes) != sum(nums):
            values_list = list(self.__notes_dict.keys())
            for i in range(len(chosen_notes)):
                if sum(chosen_notes) != sum(nums):
                    chosen_notes[i] = random.choice(values_list)
                else:
                    break
            iters += 1
            if iters > max_iter:
                chosen_notes = nums

        self.__chosen_notes = chosen_notes

    def __num_notes_selected(self):
        return (self.current_challenge // 5) + 2

    def __init_delete_button(self):
        def click_delete():
            if self.__pushed_notes:
                self.__pushed_notes.pop()

        button_text = "Apagar"
        w, _ = self.font.size(button_text)

        return Button(
            self.screen, (self.screen.get_width() - 36 - w, self.staff.c3_position), button_text, self.font, click_delete
        )

    def __click_continue(self):
        if sum(self.__pushed_notes) == sum(self.__chosen_notes):
            self.score += 1
        self.current_challenge += 1
        self.__pushed_notes = []
        self.__chosen_notes = []
        self.__pick_notes()

    def __click_end(self):
        save = Save.load()
        chapter = save.md2.chapters[self.chapter_index]

        chapter["completed"] = self.score >= int(self.num_challenges * 0.7)
        chapter["perfected"] = self.score == self.num_challenges
        
        next_chapter = save.md2.chapters[self.chapter_index + 1]
        next_chapter["unlocked"] = self.score >= int(self.num_challenges * 0.7)

        save.md2.chapters[self.chapter_index] = chapter
        save.save()
        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))
