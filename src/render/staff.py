import os

import pygame
from pygame import Surface
from pygame.font import Font

from ..utils.image_rescaler import ImageRescaler
from ..utils.note_renderer import NoteRenderer
from .renderable import Renderable


class Staff(Renderable):
    NUM_LINES = 5
    line_positions = []
    line_spacing = 16
    note_spacing = line_spacing // 2
    c3_position = 0

    def __init__(
        self,
        screen: Surface,
        y_pos: int | None = None,
        time_signature: tuple[int, int] | None = None,
    ):
        self.screen = screen
        _dir = os.path.dirname(__file__)[: __file__.index("src")]
        self.y_pos = (screen.get_height() // 2) if y_pos is None else y_pos
        for i in range(self.NUM_LINES):
            self.line_positions.append(
                (self.y_pos)
                - self.line_spacing * (self.NUM_LINES // 2)
                + i * self.line_spacing
            )
        self.c3_position = self.line_positions[-1] + self.line_spacing
        self.trebble_cleff_asset = ImageRescaler.rescale_from_height(
            pygame.image.load(_dir + "assets/images/trebble_cleff.png"),
            self.line_spacing * 6,
        )
        self.time_signature = time_signature
        self.note_drawer = NoteRenderer(screen)
        self.font = Font(None, 64)

    def render(self, render_cleff=True, render_time_signature=True):
        line_width = 2
        for i in range(self.NUM_LINES):
            pygame.draw.line(
                self.screen,
                "black",
                (0, self.line_positions[i]),
                (self.screen.get_width(), self.line_positions[i]),
                line_width,
            )

        if render_cleff:
            self.__render_cleff()
            if self.time_signature is not None and render_time_signature:
                self.__render_time_signature(self.time_signature)

    def __render_cleff(self):
        cleff_y_position = (
            self.line_positions[2] - self.trebble_cleff_asset.get_height() // 2
            if self.trebble_cleff_asset is not None
            else 0
        )
        cleff_x_position = -20
        self.screen.blit(self.trebble_cleff_asset, (cleff_x_position, cleff_y_position))

    def __render_time_signature(self, time_signature: tuple[int, int]):
        def render_num(x: int, n: int):
            self.screen.blit(
                self.font.render(str(n), True, "black"),
                (self.trebble_cleff_asset.get_width() - 40, self.line_positions[x] - 4),
            )

        n_1, n_2 = time_signature
        render_num(0, n_1)
        render_num(2, n_2)

    def event_check(self, event):
        return super().event_check(event)
