import os

import pygame
from pygame import Surface
from pygame.font import Font

from ..utils.button import Button
from ..utils.check_save import check_save
from .renderable import Renderable
from .staff import Staff


class Explanation1(Renderable):
    def __init__(self, screen: Surface) -> None:
        super().__init__()
        self.screen: Surface = screen
        self.staff = Staff(screen, time_signature=(4, 4))
        self.pg_count = 0
        self.top_text = [
            "Welcome to the music theory tutorial!",
            "This tutorial will teach you the basics of music theory.",
            "Let's start with the staff.",
        ]
        self.has_save = check_save()

    def render(self) -> None:
        self.screen.fill("white")
        self.staff.render(
            render_cleff=self.pg_count > 1, render_time_signature=self.pg_count > 2
        )
