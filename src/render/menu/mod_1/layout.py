import pygame
from pygame import Surface
from pygame.event import Event

from src.render.staff import Staff
from src.utils.image_rescaler import ImageRescaler
from src.utils.module_model import ModuleClass
from src.utils.save_operations.read_save import Module, Save


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
        self.__note_y_placement = [
            self.staff.c3_position - (i * self.staff.line_spacing) for i in range(4)
        ]
        self.__note_x_placements = self.calculate_note_x_placements(width, 9)
        self.first_chord_rect = self.calculate_rect(self.__note_x_placements[0], self.__note_y_placement[2], 3)
        self.text = self.generate_text(module, "Clave e notas")

    def render(self):
        self.surface.fill("white")
        self.__render_chord()
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placements[i + 1] - 16,
                y_pos=self.__note_y_placement[i],
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
                        self.__note_x_placements[i + 1] - 16 + star_asset.get_width() // 4,
                        self.__note_y_placement[i] + 20,
                    ),
                )

        for i in range(6, 9):
            self.note_renderer.quarter(self.__note_x_placements[5], self.__note_y_placement[i - 5],
                                       color=("black" if self.module.chapters[2]["completed"] else "gray"),
                                       )
        for i in range(6, 9):
            self.note_renderer.quarter(self.__note_x_placements[i], self.__note_y_placement[i - 5],
                                       color=("black" if self.module.chapters[i - 3]["unlocked"] else "gray"),
                                       )
            star_asset = (
                self.full_star
                if self.module.chapters[i - 3]["perfected"]
                else self.blank_star
            )
            if self.module.chapters[i - 3]["completed"]:
                star_asset = ImageRescaler.rescale_from_height(star_asset, 16)
                self.surface.blit(
                    star_asset,
                    (
                        self.__note_x_placements[i + 1] - 16 + star_asset.get_width() // 4,
                        self.__note_y_placement[i] + 20,
                    ),
                )

        pygame.draw.line(
            self.surface,
            "black",
            (self.__note_x_placements[4], self.staff.line_positions[0]),
            (self.__note_x_placements[4], self.staff.line_positions[-1]),
            5,
        )
        text = pygame.font.Font(size=32).render(self.text, True, "black")
        text_x = (self.surface.get_width() - text.get_width()) // 2
        text_y = self.screen.get_height() // 4
        self.surface.blit(text, (text_x, text_y))

        self.screen.blit(self.surface, (50, 0))

    def event_check(self, event_arg: Event | None = None):
        if event_arg.type == pygame.MOUSEBUTTONDOWN:
            if self.first_chord_rect.collidepoint(event_arg.pos):
                from .explanation_1 import Explanation1

                self.change_state(Explanation1(self.screen, self.change_state))

            from .challenge_1 import Challenge

            if (
                    self.calculate_rect(self.__note_x_placements[1], self.__note_y_placement[0], 1).collidepoint(event_arg.pos)
                    and self.module.chapters[0]["unlocked"]
            ):
                self.change_state(Challenge(self.screen, self.change_state, 0))

            elif (
                    self.calculate_rect(self.__note_x_placements[2], self.__note_y_placement[1], 1).collidepoint(event_arg.pos)
                    and self.module.chapters[1]["unlocked"]
            ):

                self.change_state(Challenge(self.screen, self.change_state, 1, True))

            elif (
                    self.calculate_rect(self.__note_x_placements[3], self.__note_y_placement[2], 2).collidepoint(event_arg.pos)
                    and self.module.chapters[2]["unlocked"]
            ):
                self.change_state(Challenge(self.screen, self.change_state, 2, True, 15))

            elif (
                    self.calculate_rect(self.__note_x_placements[5] + 16, self.__note_y_placement[3], 3).collidepoint(event_arg.pos)
                    and self.module.chapters[2]["completed"]
            ):

                save = Save.load()
                chapter = save.md1.chapters[3]
                chapter["unlocked"] = True
                save.md1.chapters[3] = chapter
                save.save()
                from .explanation_2 import Explanation2

                self.change_state(Explanation2(self.screen, self.change_state))

    def __render_chord(self):
        for i in range(3):
            self.note_renderer.quarter(
                x_pos=self.__note_x_placements[0] - 16,
                y_pos=self.__note_y_placement[0] - (self.staff.line_spacing * i),
            )
        star_asset = (
            self.blank_star
            if self.perfected_chapters != self.total_chapters
            else self.full_star
        )
        star_height = 30
        star_asset = ImageRescaler.rescale_from_height(star_asset, star_height)
        star_x = self.__note_x_placements[0] - 16 - star_asset.get_width() // 4
        star_y = self.first_chord_rect.bottom + self.staff.line_spacing
        perfected_completed_text = f"{self.perfected_chapters}/{self.total_chapters}"
        text = pygame.font.Font(size=24).render(perfected_completed_text, True, "black")
        text_y = star_y + star_height + 5
        self.surface.blit(text, (star_x + 5, text_y))
        self.surface.blit(star_asset, (star_x, star_y))
