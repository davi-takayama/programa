import pygame
from pygame import Surface
from pygame.event import Event

from ...staff import Staff
from ....utils.image_rescaler import ImageRescaler
from ....utils.module_model import ModuleClass
from ....utils.save_operations.read_save import Module


class Module3(ModuleClass):

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
        self.text = self.generate_text(module, "Melodia")
        self.note_y_placement = [self.staff.c3_position - i * self.staff.note_spacing for i in range(9)]
        self.note_x_placement = self.calculate_note_x_placements(width, 5)

    def render(self):
        text = pygame.font.Font(None, size=32).render(self.text, True, "black")
        text_x = (self.screen.get_width() - text.get_width()) // 2
        text_y = self.screen.get_height() // 4
        self.screen.blit(text, (text_x, text_y))

        self.__first_chord()
        self.draw_chapter_quarter((self.note_x_placement[1], self.note_y_placement[1]), 0)
        self.draw_chapter_quarter((self.note_x_placement[2], self.note_y_placement[2]), 1)

        pygame.draw.line(
            self.screen,
            "black",
            (self.note_x_placement[3], self.staff.line_positions[0]),
            (self.note_x_placement[3], self.staff.line_positions[-1]),
            5,
        )

        self.draw_chapter_quarter((self.note_x_placement[4], self.note_y_placement[1]), 2, True)
        self.__last_chord()

    def event_check(self, event_arg: Event | None = None):
        def check_and_change_state(x, y, height, chapter_index, challenge_class: int, unlock_next: bool = False,
                                   unlock_previous: bool = False):
            if self.calculate_rect(x, y, height).collidepoint(event_arg.pos):
                print("Clicked")
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                check_and_change_state(self.note_x_placement[1], self.note_y_placement[1], 3, 0, 1, unlock_previous=True)
                check_and_change_state(self.note_x_placement[2], self.note_y_placement[2], 3, 1, 2, unlock_previous=True)
                check_and_change_state(self.note_x_placement[4], self.note_y_placement[1], 3, 2, 3, unlock_previous=True)

    def __first_chord(self):
        for i in range(3):
            self.note_renderer.half(
                x_pos=self.note_x_placement[0],
                y_pos=self.note_y_placement[i * 2],
                color="black" if self.module.unlocked else "gray",
            )
        star_asset = (
            self.blank_star
            if self.perfected_chapters != self.total_chapters
            else self.full_star
        )
        star_height = 30
        star_asset = ImageRescaler.rescale_from_height(star_asset, star_height)
        star_x = self.note_x_placement[0] - star_asset.get_width() // 4
        star_y = self.note_y_placement[0] + self.staff.line_spacing
        perfected_completed_text = f"{self.perfected_chapters}/{self.total_chapters}"
        text = pygame.font.Font(size=24).render(perfected_completed_text, True, "black")
        text_y = star_y + star_height + 5
        self.screen.blit(text, (star_x + 5, text_y))
        self.screen.blit(star_asset, (star_x, star_y))

    def __last_chord(self):
        for i in range(3):
            self.note_renderer.half(
                x_pos=self.note_x_placement[-1],
                y_pos=self.note_y_placement[i * 2],
                color="black" if self.module.chapters[-1]["completed"] else "gray",
            )
