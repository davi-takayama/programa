import pygame
from pygame import Surface
from pygame.font import Font

from ..utils.image_rescaler import ImageRescaler
from ..utils.root_dir import root_dir


class Staff:
    NUM_LINES = 5
    line_spacing = 16
    note_spacing = line_spacing // 2
    c3_position = 0

    def __init__(
            self,
            screen: Surface,
            y_pos: int = None,
            time_signature: tuple[int, int] | None = None,
    ):
        self.screen = screen
        _dir = root_dir
        self.y_pos = (screen.get_height() // 2) if y_pos is None else y_pos
        self.line_positions = []
        for i in range(self.NUM_LINES):
            self.line_positions.append(
                self.y_pos
                - self.line_spacing * (self.NUM_LINES // 2)
                + i * self.line_spacing
            )
        self.c3_position = self.line_positions[-1] + self.line_spacing
        self.trebble_cleff_asset = ImageRescaler.rescale_from_height(
            pygame.image.load(_dir + "assets/images/trebble_cleff.png"),
            self.line_spacing * 6,
        )
        self.time_signature = time_signature
        self.font = Font(None, 64)
        self.start_x = self.trebble_cleff_asset.get_width() * 2.5

    def render(self, render_cleff=True, render_time_signature=True,
               time_signature_color: tuple[str, str] = ("black", "black")):
        line_width = 2
        for line_position in self.line_positions:
            pygame.draw.line(
                self.screen,
                "black",
                (0, line_position),
                (self.screen.get_width(), line_position),
                line_width,
            )

        if render_cleff:
            self.__render_cleff()

        if self.time_signature is not None and render_time_signature:
            self.__render_time_signature(self.time_signature, time_signature_color)

    def __render_cleff(self):
        cleff_y_position = (
            self.line_positions[2] - self.trebble_cleff_asset.get_height() // 2
            if self.trebble_cleff_asset is not None
            else 0
        )
        self.screen.blit(self.trebble_cleff_asset, (0, cleff_y_position))

    def __render_time_signature(self, time_signature: tuple[int, int], time_signature_color: tuple[str, str]):
        def render_num(x: int, n: int, color: str):
            self.screen.blit(
                self.font.render(str(n), True, color),
                (self.trebble_cleff_asset.get_width() + 10, self.line_positions[x] - 4),
            )

        n_1, n_2 = time_signature
        render_num(0, n_1, time_signature_color[0])
        render_num(2, n_2, time_signature_color[1])
