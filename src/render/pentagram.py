from math import e
import math
from matplotlib.pylab import noncentral_chisquare
from nbclient import NotebookClient
import pygame

from ..utils.image_rescaler import ImageRescaler



class Pentagram:
    NUM_LINES = 5
    line_positions = []
    line_spacing = 16
    note_spacing = line_spacing // 2
    e3_position = 0
    
    
    def __init__(self, screen, main_path):
        self.screen = screen
        self.main_path = main_path
        for i in range(self.NUM_LINES):
            self.line_positions.append(self.screen.get_height() // 2 - self.line_spacing * (self.NUM_LINES // 2) + i * self.line_spacing)
        self.e3_position = self.line_positions[-1]
        self.trebble_cleff = ImageRescaler.rescale_from_height(pygame.image.load(self.main_path + "assets/images/trebble_cleff.png"), 100)
        

    def render(self):
        cleff_y_position = self.screen.get_height() // 2 - self.trebble_cleff.get_height() // 2 if self.trebble_cleff is not None else 0
        cleff_x_position = 5
        line_width = 2
        
        for i in range(self.NUM_LINES):
            pygame.draw.line(self.screen, "black", (0, self.line_positions[i]), (self.screen.get_width(), self.line_positions[i]), line_width)
            
        self.screen.blit(self.trebble_cleff, (cleff_x_position, cleff_y_position))
        
    def draw_note(self, note: str, x_pos: int = 100, note_type: str = "whole"):
        note_name_copy = note.replace('#', '')
        note_name = note_name_copy[0]
        note_quad = int(note[-1])
        has_sharp = '#' in note
        notes_in_order = ['E', 'F', 'G', 'A', 'B', 'C', 'D']
        note_index = notes_in_order.index(note_name)
        quadrant_space = 7 * self.note_spacing
        note_position = self.e3_position - (quadrant_space * (note_quad - 4)) - (note_index * self.note_spacing)
        print(note_position, self.e3_position)
        # if note_position >= self.e3_position + self.note_spacing:
        #         num_lines = math.ceil((note_position - self.e3_position + 1) / self.line_spacing)
        #         for i in range(num_lines):
        #             pygame.draw.line(self.screen, "black", (x_pos, note_position - i * self.line_spacing), (x_pos + self.quarter_note_asset.get_width() + 10, note_position - i * self.line_spacing), 2)
                                
        # self.screen.blit(self.quarter_note_asset, (x_pos, note_position - self.quarter_note_asset.get_height() + self.note_spacing))
        self._draw_note(x_pos, note_position, note_type)
            
    def _draw_note(self, x_pos: int, y_pos: int, note_type: str = "quarter"):
        valid_note_types = ["whole", "half", "quarter"]
        if note_type in valid_note_types:
            if note_type == "whole":
                pygame.draw.ellipse(self.screen, "black", (x_pos, y_pos - self.note_spacing + 1, self.note_spacing * 2.5, self.note_spacing * 2), 3)
            elif note_type == "half":
                pygame.draw.ellipse(self.screen, "black", (x_pos, y_pos - self.note_spacing + 1, self.note_spacing * 2.5, self.note_spacing * 2), 3)
                pygame.draw.line(self.screen, "black", ((x_pos + self.note_spacing * 2.5) - 2, y_pos), ((x_pos + self.note_spacing * 2.5) - 2, y_pos - self.note_spacing * 5), 3)
            elif note_type == "quarter":
                pygame.draw.ellipse(self.screen, "black", (x_pos, y_pos - self.note_spacing + 1, self.note_spacing * 2.5, self.note_spacing * 2), self.note_spacing)
                pygame.draw.line(self.screen, "black", ((x_pos + self.note_spacing * 2.5) - 2, y_pos), ((x_pos + self.note_spacing * 2.5) - 2, y_pos - self.note_spacing * 5), 3)
        else:
            raise ValueError("Invalid note type. Valid note types are: whole, half, quarter, eighth")