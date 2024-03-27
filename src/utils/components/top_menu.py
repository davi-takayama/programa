from turtle import width
import pygame

from utils.audioinput.audio_analyzer import AudioAnalyzer

class TopMenu:
    def __init__(self, screen: pygame.Surface, main_path: str, audio_analyzer: AudioAnalyzer):
        self.screen = screen
        self.main_path = main_path
        self.audio_analyzer = audio_analyzer
        
    