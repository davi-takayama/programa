import os

import pygame as pg
from pygame import Rect, Surface
from pygame.font import Font

from .image_rescaler import ImageRescaler
from ..utils.root_dir import root_dir


class NoteRenderer:
    def __init__(self, screen: Surface, c3_pos: int = None) -> None:
        self.screen = screen
        _dir = root_dir
        self.eigth_stem = pg.image.load(_dir + "assets/images/eigth_stem.png")
        self.eigth_stem = ImageRescaler.rescale_from_height(self.eigth_stem, 35)
        self.c3_pos = c3_pos if c3_pos is not None else screen.get_height() // 2

    def __draw_sharp_or_flat(self, x_pos: int, y_pos: int, sharp: bool, color: str):
        font = Font(None, 32)
        text_surface = font.render("#" if sharp else "♭", True, color)
        self.screen.blit(text_surface, (x_pos - 3, y_pos))

    def __note_base(self, x_pos: int, y_pos: int, has_sharp: int, color: str) -> Rect:
        note_rect = pg.draw.ellipse(self.screen, color, (x_pos, y_pos - 7, 20, 16))
        if has_sharp == 1:
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10, True, color)
        elif has_sharp == 2:
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10, False, color)
        if y_pos >= self.c3_pos:
            for i in range(self.c3_pos, y_pos + 1, 16):
                pg.draw.line(self.screen, color, (x_pos - 5, i), (x_pos + 25, i), 2)
        return note_rect

    def __draw_stem(self, x_pos: int, y_pos: int, color: str) -> Rect:
        stem_rect = pg.draw.line(
            self.screen, color, (x_pos + 18, y_pos), (x_pos + 18, y_pos - 40), 3
        )
        return stem_rect

    def whole(
        self, x_pos: int, y_pos: int, has_sharp: int = 0, color: str = "black"
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        rect = self.__note_base(x_pos, y_pos, has_sharp, color)
        pg.draw.ellipse(self.screen, "white", (x_pos + 3, y_pos - 4, 14, 8))
        return rect

    def half(
        self, x_pos: int, y_pos: int, has_sharp: int = 0, color: str = "black"
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        rect = self.whole(x_pos, y_pos, has_sharp, color)
        stem_rect = self.__draw_stem(x_pos, y_pos, color)
        return rect.union(stem_rect)

    def quarter(
        self, x_pos: int, y_pos: int, has_sharp: int = 0, color: str = "black"
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        rect = self.__note_base(x_pos, y_pos, has_sharp, color)
        pg.draw.ellipse(self.screen, color, (x_pos + 3, y_pos - 5, 14, 8), 3)
        stem = self.__draw_stem(x_pos, y_pos, color)
        return rect.union(stem)

    def single_eighth(
        self, x_pos: int, y_pos: int, has_sharp: int = 0, color: str = "black"
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        rect = self.quarter(x_pos, y_pos, has_sharp, color)
        self.screen.blit(self.eigth_stem, (x_pos + 20, y_pos - 40))
        return rect
