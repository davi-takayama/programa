import pygame

from ..utils.image_rescaler import ImageRescaler



class Pentagram:
    NUM_LINES = 5
    line_positions = []
    space_positions = []
    note_positions = []
    line_spacing = 16
    natural_notes = ["E", "F", "G", "A", "B", "C", "D"]
    sharp_notes = ["F#", "G#", "A#", "C#", "D#"]
    notes = natural_notes + sharp_notes
    
    def __init__(self, screen, main_path):
        self.screen = screen
        self.main_path = main_path
        for i in range(self.NUM_LINES):
            self.line_positions.append(self.screen.get_height() // 2 - self.line_spacing * (self.NUM_LINES // 2) + i * self.line_spacing)
            self.space_positions.append(self.line_positions[i] + self.line_spacing // 2)
        self.space_positions.pop()
        
        self.note_positions = self.line_positions + self.space_positions            
        self.note_positions.sort()
        # revert the order of the notes
        self.note_positions = self.note_positions[::-1]
        

    def render(self):
        trebble_cleff = ImageRescaler.rescale_from_height(pygame.image.load(self.main_path + "assets/images/trebble_cleff.png"), 100)
        cleff_y_position = self.screen.get_height() // 2 - trebble_cleff.get_height() // 2
        cleff_x_position = 5
        line_width = 2
        
        for i in range(self.NUM_LINES):
            pygame.draw.line(self.screen, "black", (0, self.line_positions[i]), (self.screen.get_width(), self.line_positions[i]), line_width)
            
        self.screen.blit(trebble_cleff, (cleff_x_position, cleff_y_position))
        
    def draw_note(self, note: str):
        note_name_copy = note.replace('#', '')
        note_index = self.natural_notes.index(note_name_copy)
        note_position = self.note_positions[note_index]
        
        pygame.draw.circle(self.screen, "red", (20, note_position), 10)
            
            
    