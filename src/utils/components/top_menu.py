from turtle import width
import pygame

class TopMenu:
    def __init__(self, screen, main_path):
        self.screen = screen
        self.main_path = main_path
        self.font = pygame.font.Font(None, 36)
        self.text = self.font.render("Upper Menu", True, "black")
        self.text_rect = self.text.get_rect()
        self.text_rect.center = (self.screen.get_width() // 2, 20)
        
    def render(self):
        
    # def update(self):
    #     pass