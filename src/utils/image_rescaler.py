import pygame


class ImageRescaler:
    def __init__(self, main_path):
        self.main_path = main_path

    @staticmethod
    def rescale_from_width(image, width):
        aspect_ratio = image.get_width() / image.get_height()
        height = width / aspect_ratio
        return pygame.transform.scale(image, (width, int(height)))
    
    @staticmethod
    def rescale_from_height(image, height):
        aspect_ratio = image.get_width() / image.get_height()
        width = height * aspect_ratio
        return pygame.transform.scale(image, (int(width), height))