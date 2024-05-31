from abc import abstractmethod

import pygame
from pygame import Rect, Surface
from pygame.event import Event

from .image_rescaler import ImageRescaler
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
        self.staff = staff
        self.c3 = staff.c3_position
        self.change_state = change_state
        self.start_pos = x_pos
        self.module: Module = module
        self.full_star = pygame.image.load(root_dir + "/assets/images/filled_star.png")
        self.blank_star = pygame.image.load(root_dir + "/assets/images/blank_star.png")
        self.action_sound = pygame.mixer.Sound("assets/audio/metronome_trebble.wav")
        self.note_renderer = NoteRenderer(self.screen, c3_pos=self.c3)

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def event_check(self, event_arg: Event):
        pass

    def calculate_note_x_placements(self, width: int, number_of_elements: int):
        num_notes = number_of_elements
        notes_list = [self.start_pos + (width // (num_notes + 1) * i) for i in range(1, num_notes + 1)]

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
        return Rect(x_pos,
                    y_pos - self.staff.note_spacing,
                    20, height * self.staff.line_spacing)

    def __draw_star(self, pos: tuple[int, int], chapter_index: int):
        if self.module.chapters[chapter_index]["completed"]:
            star_asset = self.full_star if self.module.chapters[chapter_index]["perfected"] else self.blank_star
            star_height = 16
            star_asset = ImageRescaler.rescale_from_height(star_asset, star_height)
            star_x = pos[0] + star_asset.get_width() // 10
            star_y = pos[1] + self.staff.line_spacing
            self.screen.blit(star_asset, (star_x, star_y))

    def draw_chapter_quarter(self, pos: tuple[int, int], chapter_index: int, half: bool = False):
        self.note_renderer.quarter(
            x_pos=pos[0],
            y_pos=pos[1],
            color="black" if self.module.chapters[chapter_index]["unlocked"] else "gray"
        ) if not half else self.note_renderer.half(
            x_pos=pos[0],
            y_pos=pos[1],
            color="black" if self.module.chapters[chapter_index]["unlocked"] else "gray"
        )

        if self.module.chapters[chapter_index]["completed"]:
            self.__draw_star(pos, chapter_index)

    def draw_chapter_eighth(self, pos_list: list[tuple[int, int]], chapter_index_list: list[int]):
        colors = ["black" if self.module.chapters[chapter_index]["unlocked"] else "gray" for chapter_index in chapter_index_list]
        self.note_renderer.eighth(pos_list, None, colors)

        for pos, chapter_index in zip(pos_list, chapter_index_list):
            if self.module.chapters[chapter_index]["completed"]:
                self.__draw_star(pos, chapter_index)
