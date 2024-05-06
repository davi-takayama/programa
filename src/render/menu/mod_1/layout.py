import pygame
from pygame import Rect, Surface

from ....utils.image_rescaler import ImageRescaler
from ....utils.module_model import ModuleClass
from ....utils.save_operations.read_save import Module
from ...staff import Staff


class Module1(ModuleClass):
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
        self.__note_y_position = [
            self.staff.c3_position - (i * self.staff.line_spacing) for i in range(3)
        ]
        self.__note_x_placements = self.calculate_note_placements(
            width, 4, [self.__note_y_position[0]] + self.__note_y_position
        )
        self.chord_rect = self.calculate_chord_rect(
            3, self.__note_x_placements[0], self.__note_y_position[0]
        )
        self.text = self.generate_text(module, "Clave e notas")

    def render(self):
        self.surface.fill("white")
        self.__render_chord()
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placements[i + 1],
                y_pos=self.__note_y_position[i],
                color=("black" if self.module.chapters[i]["unlocked"] else "gray"),
            )
            star_asset = (
                self.full_star
                if self.module.chapters[i]["perfected"]
                else self.blank_star
            )
            if self.module.chapters[i]["completed"]:
                star_asset = ImageRescaler.rescale_from_height(star_asset, 16)
                self.surface.blit(
                    star_asset,
                    (
                        self.__note_x_placements[i + 1] + star_asset.get_width() // 4,
                        self.__note_y_position[i] + 20,
                    ),
                )

        pygame.draw.line(
            self.surface,
            "black",
            (self.surface.get_width() - 20, self.staff.line_positions[0]),
            (self.surface.get_width() - 20, self.staff.line_positions[-1]),
            5,
        )
        text = pygame.font.Font(size=32).render(self.text, True, "black")
        text_x = (self.surface.get_width() - text.get_width()) // 2
        text_y = self.screen.get_height() // 4
        self.surface.blit(text, (text_x, text_y))

        self.screen.blit(self.surface, (50, 0))

    def event_check(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.chord_rect.collidepoint(event.pos):
                from .explanation import Explanation1

                self.change_state(Explanation1(self.screen, self.change_state))

            from .challenge import Challenge

            if (
                self.note_rects[1].collidepoint(event.pos)
                and self.module.chapters[0]["unlocked"]
            ):
                self.change_state(Challenge(self.screen, self.change_state, 0))

            elif (
                self.note_rects[2].collidepoint(event.pos)
                and self.module.chapters[1]["unlocked"]
            ):

                self.change_state(Challenge(self.screen, self.change_state, 1, True))

            elif (
                self.note_rects[3].collidepoint(event.pos)
                and self.module.chapters[2]["unlocked"]
            ):
                self.change_state(
                    Challenge(self.screen, self.change_state, 2, True, 15)
                )

    def __render_chord(self):
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placements[0],
                y_pos=self.c3 - (self.staff.line_spacing * i),
            )
        star_asset = (
            self.blank_star
            if self.perfected_chapters != self.total_chapters
            else self.full_star
        )
        star_height = 30
        star_asset = ImageRescaler.rescale_from_height(star_asset, star_height)
        star_x = self.__note_x_placements[0] - star_asset.get_width() // 4
        star_y = self.chord_rect.bottom + self.staff.line_spacing
        perfected_completed_text = f"{self.perfected_chapters}/{self.total_chapters}"
        text = pygame.font.Font(size=24).render(perfected_completed_text, True, "black")
        text_y = star_y + star_height + 5
        self.surface.blit(text, (star_x + 5, text_y))
        self.surface.blit(star_asset, (star_x, star_y))
