import pygame
from pygame import Rect, Surface

from .note_renderer import NoteRenderer
from .renderable import Renderable
from .root_dir import root_dir
from .save_operations.read_save import Module
from ..render.staff import Staff


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
        self.perfected_chapters = None
        self.completed_chapters = None
        self.total_chapters = None
        self.surface = Surface((width, screen.get_height()))
        self.staff = staff
        self.c3 = staff.c3_position
        self.change_state = change_state
        self.x_pos = x_pos
        self.module: Module = module
        self.full_star = pygame.image.load(root_dir + "/assets/images/filled_star.png")
        self.blank_star = pygame.image.load(root_dir + "/assets/images/blank_star.png")
        self.note_renderer = NoteRenderer(self.surface, c3_pos=self.c3)

    @staticmethod
    def calculate_note_x_placements(
            width: int, number_of_elements: int
    ):
        num_notes = number_of_elements
        notes_list = [width // (num_notes + 1) * i for i in range(1, num_notes + 1)]

        return notes_list

    def generate_text(self, module: Module, title: str):
        self.total_chapters = len(module.chapters)
        self.completed_chapters = sum(
            chapter["completed"] for chapter in module.chapters
        )
        self.perfected_chapters = sum(
            chapter["perfected"] for chapter in module.chapters
        )
        return f"{title} ({self.completed_chapters}/{self.total_chapters})"

    def calculate_rect(self, x_pos: int, y_pos: int, height: int) -> Rect:
        return Rect(self.x_pos + x_pos,
                    y_pos - self.staff.note_spacing,
                    20, height * self.staff.line_spacing)
