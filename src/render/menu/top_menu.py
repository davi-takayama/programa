import pygame
from pygame import Surface
from pygame.font import Font


class TopMenu:
    def __init__(
            self,
            screen: Surface,
            completed_chapters: int,
            perfected_chapters: int,
            total_chapters: int,
    ):
        self.screen = screen
        self.completed_chapters = completed_chapters
        self.perfected_chapters = perfected_chapters
        self.total_chapters = total_chapters
        self.progress_value = (self.completed_chapters + self.perfected_chapters) / (
                self.total_chapters * 2
        )
        self.progress_percent = int(self.progress_value * 100)

    def render(self):
        surface = Surface((self.screen.get_width(), 60))
        surface.fill("white")
        self.screen.blit(surface, (0, 0))
        pygame.draw.line(
            self.screen, "black", (0, 60), (self.screen.get_width(), 60), 2
        )
        render_font = Font(None, 24)

        self.__render_save_info(
            self.screen.get_width() // 4,
            "capitulos concluidos",
            self.completed_chapters,
            0,
            render_font,
        )
        self.__render_save_info(
            self.screen.get_width() // 4,
            "capitulos perfeitos",
            self.perfected_chapters,
            self.screen.get_width() // 4,
            render_font,
        )

        self.__progress_info()

    def __render_save_info(
            self, rect_width: int, label: str, value: int, position: int, font_arg: Font
    ):
        rect = Surface((rect_width, 60))
        rect.fill("white")
        text = font_arg.render(label, True, "black")
        text_rect = text.get_rect(center=(rect_width // 2, 20))
        rect.blit(text, text_rect)
        text = font_arg.render(f"{value} / {self.total_chapters}", True, "black")
        text_rect = text.get_rect(center=(rect_width // 2, 40))
        rect.blit(text, text_rect)
        self.screen.blit(rect, (position, 0))

    def __progress_info(self):
        progress_rect = Surface((self.screen.get_width() // 2, 60))
        progress_rect.fill("white")

        progress_bar = Surface(
            (progress_rect.get_width() * 3 // 4, progress_rect.get_height() // 3)
        )
        progress_bar.fill("white")
        pygame.draw.rect(progress_bar, "black", progress_bar.get_rect(), 2)

        fill_width = progress_bar.get_width() * self.progress_value

        pygame.draw.rect(
            progress_bar, "black", (0, 0, fill_width, progress_bar.get_height())
        )

        progress_rect.blit(progress_bar, (25, progress_rect.get_height() // 3))

        render_font = Font(None, 24)
        text = render_font.render(f"{self.progress_percent}%", True, "black")
        text_rect = text.get_rect(
            center=((progress_bar.get_width() + 50), progress_rect.get_height() // 2)
        )
        progress_rect.blit(text, text_rect)
        self.screen.blit(progress_rect, (self.screen.get_width() // 2, 0))
