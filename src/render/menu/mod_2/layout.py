import pygame
from pygame import Rect, Surface
from pygame.event import Event

from ....utils.save_operations.read_save import Module
from ...staff import Staff
from ....utils.image_rescaler import ImageRescaler
from ....utils.module_model import ModuleClass


class Module2(ModuleClass):

    def __init__(
        self,
        screen: Surface,
        staff: Staff,
        change_state: classmethod,
        x_pos: int,
        width: int,
        module: Module,
    ) -> None:
        super().__init__(screen, staff, change_state, x_pos, width, module)
        self.text = self.generate_text(module, "Métricas de tempo")
        self.__note_y_placement = [
            self.staff.c3_position
            - (i * self.staff.line_spacing)
            - self.staff.line_spacing
            for i in range(5)
        ]
        self.__note_x_placement = self.calculate_note_placements(
            width, 5, self.__note_y_placement
        )
        self.first_chord_rect: Rect = self.calculate_chord_rect(
            3, self.__note_x_placement[0], self.__note_y_placement[0]
        )

    def render(self):
        self.surface.fill("white")
        self.__render_first_chord()
        self.note_renderer.quarter(
            x_pos=self.__note_x_placement[1],
            y_pos=self.__note_y_placement[0],
            color=("black" if self.module.chapters[0]["unlocked"] else "gray"),
        )
        self.__render_second_chord()
        self.note_renderer.eigth(
            [
                (self.__note_x_placement[3], self.__note_y_placement[1]),
                (self.__note_x_placement[4], self.__note_y_placement[2]),
            ],
            0,
            [
                ("black" if self.module.chapters[2]["unlocked"] else "gray"),
                ("black" if self.module.chapters[3]["unlocked"] else "gray"),
            ],
        )

        self.screen.blit(self.surface, (self.x_pos, 0))

    def event_check(self, event_arg: Event | None = None):
        return super().event_check(event_arg)

    def __render_first_chord(self):
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placement[0],
                y_pos=self.__note_y_placement[i],
                color=("black" if self.module.unlocked else "gray"),
            )
        star_asset = (
            self.blank_star
            if self.perfected_chapters != self.total_chapters
            else self.full_star
        )
        star_height = 30
        star_asset = ImageRescaler.rescale_from_height(star_asset, star_height)
        star_x = self.__note_x_placement[0] - star_asset.get_width() // 4
        star_y = self.first_chord_rect.bottom + self.staff.line_spacing
        perfected_completed_text = f"{self.perfected_chapters}/{self.total_chapters}"
        text = pygame.font.Font(size=24).render(perfected_completed_text, True, "black")
        text_y = star_y + star_height + 5
        self.surface.blit(text, (star_x + 5, text_y))
        self.surface.blit(star_asset, (star_x, star_y))

    def __render_second_chord(self):
        for i in range(2):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placement[2],
                y_pos=self.__note_y_placement[i + 1],
                color=("black" if self.module.chapters[1]["unlocked"] else "gray"),
            )
