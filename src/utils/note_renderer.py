from typing import List, Literal

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

    def __draw_sharp_or_flat(
        self, x_pos: int, y_pos: int, symbol: Literal["#", "b", "♮"], color: str
    ):
        font = Font(None, 32)
        text_surface = font.render(symbol, True, color)
        self.screen.blit(text_surface, (x_pos - 3, y_pos))

    def __note_base(
        self,
        x_pos: int,
        y_pos: int,
        has_sharp: Literal["none", "sharp", "flat", "natural"],
        color: str,
    ) -> Rect:
        note_rect = pg.draw.ellipse(self.screen, color, (x_pos, y_pos - 7, 20, 16))
        if has_sharp == "sharp":
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10, "#", color)
        elif has_sharp == "flat":
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10, "b", color)
        elif has_sharp == "natural":
            self.__draw_sharp_or_flat(x_pos - 12, y_pos - 10, "♮", color)
        if y_pos >= self.c3_pos:
            for i in range(self.c3_pos, y_pos + 1, 16):
                pg.draw.line(self.screen, color, (x_pos - 5, i), (x_pos + 25, i), 2)
        return note_rect

    def __draw_stem(self, x_pos: int, y_pos: int, color: str) -> Rect:
        pg.draw.line(
            self.screen, color, (x_pos + 18, y_pos), (x_pos + 18, y_pos - 40), 3
        )

    def whole(
        self,
        x_pos: int,
        y_pos: int,
        has_sharp: Literal["none", "sharp", "flat", "natural"] = "none",
        color: str = "black",
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        self.__note_base(x_pos, y_pos, has_sharp, color)
        pg.draw.ellipse(self.screen, "white", (x_pos + 3, y_pos - 4, 14, 8))

    def half(
        self,
        x_pos: int,
        y_pos: int,
        has_sharp: Literal["none", "sharp", "flat", "natural"] = "none",
        color: str = "black",
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        self.whole(x_pos, y_pos, has_sharp, color)
        self.__draw_stem(x_pos, y_pos, color)

    def quarter(
        self,
        x_pos: int,
        y_pos: int,
        has_sharp: Literal["none", "sharp", "flat", "natural"] = "none",
        color: str = "black",
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        self.__note_base(x_pos, y_pos, has_sharp, color)
        pg.draw.ellipse(self.screen, color, (x_pos + 3, y_pos - 5, 14, 8), 3)
        self.__draw_stem(x_pos, y_pos, color)

    def single_eighth(
        self,
        x_pos: int,
        y_pos: int,
        has_sharp: Literal["none", "sharp", "flat", "natural"] = "none",
        color: str = "black",
    ) -> Rect:
        """
        x_pos: x position of the note
        y_pos: y position of the note
        has_sharp: if the note has a sharp or flat (0 for none, 1 for sharp, 2 for flat)
        color: color of the note
        """
        self.quarter(x_pos, y_pos, has_sharp, color)
        self.screen.blit(self.eigth_stem, (x_pos + 20, y_pos - 40))

    def eighth(
        self,
        positions: List[tuple[int, int]],
        has_sharp: List[Literal["none", "sharp", "flat", "natural"]] | int = 0,
        color: str | List[str] = "black",
        sixteenth: bool = False,
    ) -> List[Rect]:
        """
        positions: list of tuples with the x and y position of the notes
        has_sharp: list with the sharp or flat of each note
        color: color of the notes
        """
        rects = []
        index = 0
        if isinstance(color, str):
            color = [color] * len(positions)
        if isinstance(has_sharp, int):
            has_sharp = [has_sharp] * len(positions)

        for pos, sharp in zip(positions, has_sharp):
            if index == len(positions) - 1 and len(positions) % 2 != 0:
                rect = self.single_eighth(pos[0], pos[1], sharp, color[index])
            else:
                rect = self.quarter(pos[0], pos[1], sharp, color[index])

                if index % 2 == 1:

                    pg.draw.line(
                        self.screen,
                        color[(index - 1) if index > 1 else 0],
                        (positions[index - 1][0] + 18, positions[index - 1][1] - 40),
                        (pos[0] + 18, pos[1] - 40),
                        6,
                    )
                    if sixteenth:
                        pg.draw.line(
                            self.screen,
                            color[(index - 1) if index > 1 else 0],
                            (
                                positions[index - 1][0] + 18,
                                positions[index - 1][1] - 32,
                            ),
                            (pos[0] + 18, pos[1] - 32),
                            6,
                        )

            rects.append(rect)
            index += 1
