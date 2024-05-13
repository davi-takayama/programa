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
            use_audio: bool = False,
            num_challenges: int = 10,
            unlock_next: bool = True,
    ):
        super().__init__(screen, change_state, chapter_index, use_audio, num_challenges)
        self.notes_dict: dict[float, callable] = {
            1: self.note_renderer.whole,
            0.5: self.note_renderer.half,
            0.25: self.note_renderer.quarter,
            0.125: self.note_renderer.single_eighth
        }

        self.__pushed_notes = []
        self.__chosen_notes = []
        self.__note_buttons = self.__init_note_buttons()
        self.__delete_button = self.__init_delete_button()
        self.__continue_button = self.init_continue_button(self.__click_continue)
        self.__pick_notes()
        self.__note_pos_area = abs(self.staff.trebble_cleff_asset.get_width() * 2.2 - self.screen.get_width() // 2)
        self.__end_button = self.init_end_button(self.__click_end)
        self.__unlock_next = unlock_next

    def render(self):
        self.screen.fill("white")
        if self.current_challenge < self.num_challenges:
            if len(self.__pushed_notes) < self.__num_notes_selected():
                self.__challenge_render()
            else:
                self.__continue_render()
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
        for button in self.__note_buttons:
            button.render()
        self.go_back_button.render()
        self.__delete_button.render()
        self.__cleff_notes_render()

        text = f"Selecione {self.__num_notes_selected()} notas cujo valor seja igual às figuras da esquerda"
        width, _ = self.font.size(text)
        self.screen.blit(
            self.font.render(text, True, "black"),
            (
                (self.screen.get_width() // 2) - (width // 2),
                (self.screen.get_height() // 2 + 20),
            ),
        )

    def __cleff_notes_render(self):
        note_y = int(self.staff.c3_position - self.staff.line_spacing * 2.5)
        for index, note in enumerate(self.__chosen_notes):
            x = (self.staff.trebble_cleff_asset.get_width() * 2.2) + (index * (self.__note_pos_area // len(self.__chosen_notes)))
            self.notes_dict[note](x, note_y)
        #     draw a vertical line on the middle of the screen
        pygame.draw.line(self.screen, "black", (self.screen.get_width() // 2, self.staff.line_positions[0]),
                         (self.screen.get_width() // 2, self.staff.line_positions[-1]), 5)
        for index, note in enumerate(self.__pushed_notes):
            x = (self.staff.trebble_cleff_asset.get_width() * 2.2) + (
                    index * (self.__note_pos_area // len(self.__pushed_notes))) + self.screen.get_width() // 2
            self.notes_dict[note](int(x), note_y)

    def __continue_render(self):
        self.staff.render()
        self.go_back_button.render()
        self.__cleff_notes_render()
        self.__continue_button.render()
        text = "Correto!" if sum(self.__pushed_notes) == sum(self.__chosen_notes) else "Incorreto!"
        text = self.font.render(text, True, "black")
        self.screen.blit(text, (self.screen.get_width() // 2 - text.get_width() // 2, 20))

    def __init_note_buttons(self) -> List[Button]:
        note_renderer = NoteRenderer(
            self.screen, (self.screen.get_height() // 4 * 3) + 32
        )
        notes_dict: dict[float, callable] = {
            1: note_renderer.whole,
            0.5: note_renderer.half,
            0.25: note_renderer.quarter,
            0.125: note_renderer.single_eighth,
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
            random.choice(list(self.notes_dict.keys()))
            for _ in range(self.__num_notes_selected())
        ]
        nums_dict = {1: 8, 0.5: 4, 0.25: 2, 0.125: 1}
        num_of_notes = sum([nums_dict[num] for num in nums])
        num_of_notes = random.randint(len(nums), num_of_notes)

        chosen_notes = []
        while sum(chosen_notes) < sum(nums):
            chosen_notes = [
                random.choice(list(self.notes_dict.keys()))
                for _ in range(num_of_notes)
            ]

        max_iter = 500
        iters = 0
        while sum(chosen_notes) != sum(nums):
            values_list = list(self.notes_dict.keys())
            for i in range(len(chosen_notes)):
                if sum(chosen_notes) != sum(nums):
                    chosen_notes[i] = random.choice(values_list)
                else:
                    break
            iters += 1
            if iters > max_iter:
                chosen_notes = nums

        self.__chosen_notes = chosen_notes

        print(chosen_notes, sum(chosen_notes))
        print(nums, sum(nums))

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

        if self.score >= int(self.num_challenges * 0.7):
            chapter["completed"] = True
            if self.score == self.num_challenges:
                chapter["perfected"] = True
            if self.chapter_index + 1 < len(save.md2.chapters) and self.__unlock_next:
                next_chapter = save.md2.chapters[self.chapter_index + 1]
                next_chapter["unlocked"] = True
            else:
                save.md3.unlocked = True
        save.md2.chapters[self.chapter_index] = chapter
        save.save()
        from ..main_menu import Menu

        self.change_state(Menu(self.screen, self.change_state))
