import os

import pygame
from pygame import Surface

from .render.intro_scr import IntroScr
from .render.renderable import Renderable


class StateHandler(Renderable):
    def __init__(self, screen: Surface) -> None:
        super().__init__()
        self.screen: Surface = screen
        if not self.__check_save():
            self.state: Renderable = IntroScr(self.screen, pygame.font.Font(None, 32))
        else:
            self.state: Renderable = self.PlaceholderState(self.screen)

    def __check_save(self) -> bool:
        _dir = os.path.dirname(__file__)[: __file__.index("src")]
        save_path = os.path.join(_dir + "/savestate", "save.json")
        return os.path.isfile(save_path)

    def render(self) -> None:
        self.state.render()

    def event_check(self, event: pygame.event.Event | None) -> None:
        self.state.event_check(event)

    class PlaceholderState(Renderable):
        def __init__(self, screen: Surface) -> None:
            super().__init__()
            self.screen = screen

        def render(self) -> None:
            self.screen.fill("black")

        def event_check(self, event) -> None:
            """
            Placeholder event check
            """
            pass
