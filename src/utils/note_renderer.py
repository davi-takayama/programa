from typing import List, Literal

import pygame as pg
from pygame import Surface
from pygame.font import Font

from src.utils.image_rescaler import ImageRescaler
from src.render.staff import Staff
from src.utils.root_dir import root_dir

class NoteRenderer:
    def __init__(self, screen: Surface, c3_pos: int = None, draw_lines: bool = True) -> None:
        self.screen = screen
        _dir = root_dir
        self.eigth_stem = pg.image.load(_dir + "assets/images/eigth_stem.png")
        self.eigth_stem = ImageRescaler.rescale_from_height(self.eigth_stem, 35)
        self.__c3_pos = c3_pos if c3_pos is not None and draw_lines else screen.get_height() // 2
        self.__line_spacing = Staff.line_spacing
        self.__draw_lines = draw_lines
        self.__whole_pause = ImageRescaler.rescale_from_height(pg.image.load(_dir + "assets/images/pauses/whole_pause.png"), 10)
        self.__half_pause = ImageRescaler.rescale_from_height(pg.image.load(_dir + "assets/images/pauses/half_pause.png"), 10)
        self.__quarter_pause = ImageRescaler.rescale_from_height(pg.image.load(_dir + "assets/images/pauses/quarter_pause.png"), 48)
        self.__eighth_pause = ImageRescaler.rescale_from_height(pg.image.load(_dir + "assets/images/pauses/eighth_pause.png"), 32)

    def __draw_accident(
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
    ):
        pg.draw.ellipse(self.screen, color, (x_pos, y_pos - 7, 20, 16))
        if has_sharp == "sharp":
            self.__draw_accident(x_pos - 12, y_pos - 10, "#", color)
        elif has_sharp == "flat":
            self.__draw_accident(x_pos - 12, y_pos - 10, "b", color)
        elif has_sharp == "natural":
            self.__draw_accident(x_pos - 12, y_pos - 10, "♮", color)
        if y_pos >= self.__c3_pos and self.__draw_lines:
            for i in range(self.__c3_pos, y_pos + 1, 16):
                pg.draw.line(self.screen, color, (x_pos - 5, i), (x_pos + 25, i), 2)

    def __draw_stem(self, x_pos: int, y_pos: int, color: str):
        pg.draw.line(
            self.screen, color, (x_pos + 18, y_pos), (x_pos + 18, y_pos - 40), 3
        )

    def whole(
            self,
            x_pos: int,
            y_pos: int,
            has_sharp: Literal["none", "sharp", "flat", "natural"] = "none",
            color: str = "black",
    ):
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
    ):
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
    ):
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
    ):
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
    ):
        """
        positions: list of tuples with the x and y position of the notes
        has_sharp: list with the sharp or flat of each note
        color: color of the notes
        """
        index = 0
        if isinstance(color, str):
            color = [color] * len(positions)
        if isinstance(has_sharp, int):
            has_sharp = [has_sharp] * len(positions)

        def draw_note(note_pos, note_has_sharp, note_color):
            if index == len(positions) - 1 and len(positions) % 2 != 0:
                return self.single_eighth(note_pos[0], note_pos[1], note_has_sharp, note_color)
            else:
                return self.quarter(note_pos[0], note_pos[1], note_has_sharp, note_color)

        for pos, sharp in zip(positions, has_sharp):
            draw_note(pos, sharp, color[index])
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
                        (positions[index - 1][0] + 18, positions[index - 1][1] - 32),
                        (pos[0] + 18, pos[1] - 32),
                        6,
                    )

            index += 1

    def pause(self, pos: int, pause_length: int, y_pos: int = None):
        """
        pos: x and y position of the pause
        pause_length: [
          - 0 for whole
          - 1 for half
          - 2 for quarter
          - 3 for eighth
        ]
        """
        match pause_length:
            case 0:
                x = pos - self.__whole_pause.get_width() // 2
                y = y_pos if y_pos is not None else self.__c3_pos - (self.__line_spacing * 2.6)
                height = self.__whole_pause.get_height()
                self.screen.blit(self.__whole_pause, (x, y - height // 2))
            case 1:
                x = pos - self.__half_pause.get_width() // 2
                y = y_pos if y_pos is not None else self.__c3_pos - (self.__line_spacing * 2.3)
                height = self.__half_pause.get_height()
                self.screen.blit(self.__half_pause, (x, y - height // 2))
            case 2:
                x = pos - self.__quarter_pause.get_width() // 2
                y = y_pos if y_pos is not None else self.__c3_pos - (self.__line_spacing * 3)
                height = self.__quarter_pause.get_height()
                self.screen.blit(self.__quarter_pause, (x, y - height // 2))
            case 3:
                x = pos - self.__eighth_pause.get_width() // 2
                y = y_pos if y_pos is not None else self.__c3_pos - (self.__line_spacing * 3)
                height = self.__eighth_pause.get_height()
                self.screen.blit(self.__eighth_pause, (x, y - height // 2))
            case _:
                raise ValueError("Invalid pause length")
