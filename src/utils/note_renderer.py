import pygame as pg
import os

from .image_rescaler import ImageRescaler


class NoteRenderer:
    def __init__(self, screen: pg.Surface) -> None:
        self.screen = screen
        _dir = os.path.dirname(__file__)[:__file__.index("src")]
        self.eigth_stem = pg.image.load(_dir + "assets/images/eigth_stem.png")
        self.eigth_stem = ImageRescaler.rescale_from_height(self.eigth_stem, 35)

    def __draw_sharp_or_flat(self, x_pos: int, y_pos: int, sharp: bool = True):
        font = pg.font.Font(None, 32)
        text_surface = font.render("#" if sharp else "♭", True, (0, 0, 0))
        self.screen.blit(text_surface, (x_pos - 20, y_pos))

    def __note_base(self, x_pos: int, y_pos: int, has_sharp: bool = False) -> None:
        pg.draw.ellipse(self.screen, "black", (x_pos, y_pos - 7, 20, 16))
        if has_sharp:
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10)

    def __draw_stem(self, x_pos: int, y_pos: int) -> None:
        pg.draw.line(
            self.screen, "black", (x_pos + 18, y_pos), (x_pos + 18, y_pos - 40), 3
        )

    def whole(self, x_pos: int, y_pos: int, has_sharp: bool = False) -> None:
        self.__note_base(x_pos, y_pos, has_sharp)
        pg.draw.ellipse(self.screen, "white", (x_pos + 3, y_pos - 4, 14, 8))

    def half(self, x_pos: int, y_pos: int, has_sharp: bool = False) -> None:
        self.whole(x_pos, y_pos, has_sharp)
        self.__draw_stem(x_pos, y_pos)

    def quarter(self, x_pos: int, y_pos: int, has_sharp: bool = False) -> None:
        self.__note_base(x_pos, y_pos, has_sharp)
        pg.draw.ellipse(self.screen, "black", (x_pos + 3, y_pos - 5, 14, 8), 3)
        self.__draw_stem(x_pos, y_pos)

    def single_eighth(self, x_pos: int, y_pos: int, has_sharp: bool = False) -> None:
        self.quarter(x_pos, y_pos, has_sharp)
        self.screen.blit(self.eigth_stem, (x_pos + 20, y_pos - 40))