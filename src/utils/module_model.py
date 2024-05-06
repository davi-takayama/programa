from typing import List

import pygame
from pygame import Rect, Surface

from ..render.staff import Staff
from .note_renderer import NoteRenderer
from .renderable import Renderable
from .root_dir import root_dir
from .save_operations.read_save import Module


class ModuleClass(Renderable):

    def __init__(
        self,
        screen: Surface,
        staff: Staff,
        change_state: classmethod,
        x_pos: int,
        width: int,
        module: Module,
    ) -> None:
        super().__init__(screen, change_state)
        self.surface = Surface((width, screen.get_height()))
        self.staff = staff
        self.c3 = staff.c3_position
        self.change_state = change_state
        self.x_pos = x_pos
        self.module = module
        self.full_star = pygame.image.load(root_dir + "/assets/images/filled_star.png")
        self.blank_star = pygame.image.load(root_dir + "/assets/images/blank_star.png")
        self.note_renderer = NoteRenderer(self.surface, c3_pos=self.c3)

    def calculate_note_placements(
        self, width: int, number_of_notes: int, notes: List[int]
    ):
        num_notes = number_of_notes
        notes_list = [width // (num_notes + 1) * (i) for i in range(1, num_notes + 1)]

        self.note_rects = [
            Rect(
                notes_list[index + 1] + self.x_pos + 10,
                note - 10,
                20,
                20,
            )
            for index, note in enumerate(notes)
        ]

        return notes_list

    def generate_text(self, module, title: str):
        self.total_chapters = len(module.chapters)
        self.completed_chapters = sum(
            chapter["completed"] for chapter in module.chapters
        )
        self.perfected_chapters = sum(
            chapter["perfected"] for chapter in module.chapters
        )
        return f"{title} ({self.completed_chapters}/{self.total_chapters})"
