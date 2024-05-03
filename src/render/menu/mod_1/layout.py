import pygame
from pygame import Rect, Surface

from ....utils.note_renderer import NoteRenderer
from ....utils.root_dir import root_dir
from ....utils.save_operations.read_save import Module, Save
from ...renderable import Renderable
from ...staff import Staff
from ....utils.image_rescaler import ImageRescaler


class Module1(Renderable):

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
        self.staff = staff
        self.surface = Surface((width, screen.get_height()))
        self.change_state = change_state
        self.c3 = staff.c3_position
        self.note_renderer = NoteRenderer(self.surface, c3_pos=self.c3)
        self.x_pos = x_pos
        self.notes = [
            self.staff.c3_position - (i * self.staff.line_spacing) for i in range(3)
        ]
        self.note_placements = self.__calculate_note_placements(width)
        self.chord_rect = self.__calculate_chord_rect()
        self.text = self.__generate_text(module)
        self.star_asset = self.__load_star_asset(module)
        self.__module = module

    def __calculate_note_placements(self, width):
        num_notes = 4
        notes_list = [width // (num_notes + 1) * (i) for i in range(1, num_notes + 1)]

        self.note_rects = [
            Rect(
                notes_list[index + 1] + self.x_pos + 10,
                note - 10,
                20,
                20,
            )
            for index, note in enumerate(self.notes)
        ]

        return notes_list

    def __calculate_chord_rect(self):
        chord_height = self.staff.line_spacing * 3
        return Rect(
            self.x_pos + self.note_placements[0] + 20,
            self.c3 - chord_height + self.staff.note_spacing,
            20,
            chord_height,
        )

    def __generate_text(self, module):
        self.total_chapters = len(module.chapters)
        self.completed_chapters = sum(
            chapter["completed"] for chapter in module.chapters
        )
        self.perfected_chapters = sum(
            chapter["perfected"] for chapter in module.chapters
        )
        return f"Clave e notas ({self.completed_chapters}/{self.total_chapters})"

    def __load_star_asset(self, module):
        star_image = (
            "filled_star.png"
            if sum(chapter["perfected"] for chapter in module.chapters)
            == len(module.chapters)
            else "blank_star.png"
        )
        return pygame.image.load(root_dir + f"/assets/images/{star_image}")

    def render(self):
        self.surface.fill("white")
        self.render_chord()
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.note_placements[i + 1],
                y_pos=self.notes[i],
                color=("black" if self.__module.chapters[i]["unlocked"] else "gray"),
            )
        pygame.draw.line(
            self.surface,
            "black",
            (self.surface.get_width() - 1, self.staff.line_positions[0]),
            (self.surface.get_width() - 1, self.staff.line_positions[-1]),
            5,
        )
        text = pygame.font.Font(size=32).render(self.text, True, "black")
        text_x = (self.surface.get_width() - text.get_width()) // 2
        text_y = self.screen.get_height() // 4
        self.surface.blit(text, (text_x, text_y))

        self.screen.blit(self.surface, (50, 0))

    def event_check(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.chord_rect.collidepoint(event.pos):
                from .explanation import Explanation1

                self.change_state(Explanation1(self.screen, self.change_state))
            if self.note_rects[0].collidepoint(event.pos):
                from .challenge_1 import Challenge1

                self.change_state(Challenge1(self.screen, self.change_state, 0))

    def render_chord(self):
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.note_placements[0],
                y_pos=self.c3 - (self.staff.line_spacing * i),
            )
        star_height = 30
        star_asset = ImageRescaler.rescale_from_height(self.star_asset, star_height)
        star_x = self.note_placements[0] - star_asset.get_width() // 4
        star_y = self.chord_rect.bottom + self.staff.line_spacing
        perfected_completed_text = f"{self.perfected_chapters}/{self.total_chapters}"
        text = pygame.font.Font(size=24).render(perfected_completed_text, True, "black")
        text_y = star_y + star_height + 5
        self.surface.blit(text, (star_x + 5, text_y))
        self.surface.blit(star_asset, (star_x, star_y))
