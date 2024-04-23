import pygame

from ..utils.image_rescaler import ImageRescaler
from ..utils.note_renderer import NoteRenderer
from .renderable import Renderable


class Pentagram(Renderable):
    NUM_LINES = 5
    line_positions = []
    line_spacing = 16
    note_spacing = line_spacing // 2
    c3_position = 0
    
    def __init__(self, screen: pygame.Surface, main_path: str):
        self.screen = screen
        self.main_path = main_path
        for i in range(self.NUM_LINES):
            self.line_positions.append(self.screen.get_height() // 2 - self.line_spacing * (self.NUM_LINES // 2) + i * self.line_spacing)
        self.c3_position = self.line_positions[-1] + self.line_spacing
        self.trebble_cleff_asset = ImageRescaler.rescale_from_height(pygame.image.load(self.main_path + "assets/images/trebble_cleff.png"), 100)
        self.note_drawer = NoteRenderer(screen)

    def render(self, render_cleff = True):
        line_width = 2
        for i in range(self.NUM_LINES):
            pygame.draw.line(self.screen, "black", (0, self.line_positions[i]), (self.screen.get_width(), self.line_positions[i]), line_width)
    
        if render_cleff:
            cleff_y_position = self.screen.get_height() // 2 - self.trebble_cleff_asset.get_height() // 2 if self.trebble_cleff_asset is not None else 0
            cleff_x_position = 0
            self.screen.blit(self.trebble_cleff_asset, (cleff_x_position, cleff_y_position))
        
    def event_check(self):
        return super().event_check()